"""Desplegar el Portal TI y publicar una revisión Git para su validación en AWS."""

import argparse
import json
import re
import shutil
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parents[2]


def run(*args, capture=False):
    return subprocess.run(
        args,
        cwd=ROOT,
        check=True,
        text=True,
        stdout=subprocess.PIPE if capture else None,
    ).stdout


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("step", choices=("deploy", "publish", "all"))
    parser.add_argument("--region", default="us-east-1")
    parser.add_argument("--name", default="tile23-portal")
    parser.add_argument("--profile")
    args = parser.parse_args()
    if not re.fullmatch(r"[a-z][a-z0-9-]{2,30}", args.name):
        parser.error("--name debe tener entre 3 y 31 caracteres alfanuméricos o guiones")
    if run("git", "status", "--porcelain", capture=True).strip():
        parser.error("confirma o guarda los cambios antes de publicar una revisión")
    revision = run("git", "rev-parse", "HEAD", capture=True).strip()
    version = run("git", "show", f"{revision}:VERSION", capture=True).strip()

    def aws(*command, capture=False):
        options = ["--region", args.region, "--no-cli-pager"]
        if args.profile:
            options.extend(["--profile", args.profile])
        return run("aws", *options, *command, capture=capture)

    def deploy(suffix, template, **parameters):
        stack_name = args.name + suffix
        command = [
            "cloudformation",
            "deploy",
            "--template-file",
            f"infra/evaluacion/{template}.yml",
            "--stack-name",
            stack_name,
            "--capabilities",
            "CAPABILITY_IAM",
            "--no-fail-on-empty-changeset",
            "--tags",
            "Project=TILE23-Evaluacion4",
        ]
        if parameters:
            command.extend(["--parameter-overrides", *(f"{k}={v}" for k, v in parameters.items())])
        aws(*command)

    def outputs(suffix):
        items = aws(
            "cloudformation",
            "describe-stacks",
            "--stack-name",
            args.name + suffix,
            "--query",
            "Stacks[0].Outputs",
            "--output",
            "json",
            capture=True,
        )
        return {item["OutputKey"]: item["OutputValue"] for item in json.loads(items)}

    with TemporaryDirectory(prefix="tile23-") as temporary:
        scratch = Path(temporary)
        source = scratch / "portal-source.zip"
        run("git", "archive", "--format=zip", f"--output={source}", revision)
        if args.step in {"deploy", "all"}:
            deploy("-artefactos", "artefactos")
            bucket = outputs("-artefactos")["Bucket"]
            checked_out = scratch / "source"
            with ZipFile(source) as archive:
                archive.extractall(checked_out)
            package = scratch / "package"
            run(
                sys.executable,
                "-m",
                "pip",
                "install",
                "--disable-pip-version-check",
                "--no-compile",
                "--only-binary=:all:",
                "--implementation",
                "cp",
                "--platform",
                "manylinux_2_28_x86_64",
                "--platform",
                "manylinux2014_x86_64",
                "--python-version",
                "3.12",
                "--target",
                str(package),
                "-r",
                str(checked_out / "requirements-lambda.txt"),
            )
            shutil.copytree(checked_out / "app", package / "app")
            code = shutil.make_archive(str(scratch / "lambda"), "zip", package)
            key = f"lambda/{revision}.zip"
            code_version = aws(
                "s3api",
                "put-object",
                "--bucket",
                bucket,
                "--key",
                key,
                "--body",
                code,
                "--query",
                "VersionId",
                "--output",
                "text",
                capture=True,
            ).strip()
            deploy(
                "",
                "portal",
                ArtifactBucket=bucket,
                CodeKey=key,
                CodeVersion=code_version,
                Release=version,
                Revision=revision,
                DeployedAt=datetime.now(UTC).isoformat(),
            )
            portal = outputs("")
            deploy(
                "-ci",
                "pipeline",
                ArtifactBucket=bucket,
                AuditBucket=portal["AuditBucket"],
                PortalUrl=portal["Url"],
                FunctionName=portal["Function"],
                ApiId=portal["ApiId"],
            )
            print(f"Portal desplegado en {portal['Url']}")
        if args.step in {"publish", "all"}:
            bucket = outputs("-artefactos")["Bucket"]
            portal = outputs("")
            deployed = aws(
                "lambda",
                "get-function-configuration",
                "--function-name",
                portal["Function"],
                "--query",
                "Environment.Variables.APP_REVISION",
                "--output",
                "text",
                capture=True,
            ).strip()
            if deployed != revision:
                parser.error(f"la revisión desplegada es {deployed}; ejecuta deploy primero")
            with ZipFile(source, "a", compression=ZIP_DEFLATED) as archive:
                archive.writestr(
                    "release.json", json.dumps({"revision": revision, "version": version})
                )
            aws(
                "s3api",
                "put-object",
                "--bucket",
                bucket,
                "--key",
                "source/portal.zip",
                "--body",
                str(source),
                "--query",
                "VersionId",
                "--output",
                "text",
            )
            print(f"Revisión publicada para pruebas automáticas: {revision}")


if __name__ == "__main__":
    main()
