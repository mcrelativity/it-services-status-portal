# Portal de Monitoreo de Servicios TI

Proyecto individual para demostrar una solución DevOps CI/CD desplegada en AWS mediante Infraestructura como Código.

## ¿Qué hace la aplicación?

El portal realiza **chequeos HTTP reales** sobre cuatro servicios públicos relacionados con el desarrollo y despliegue del proyecto:

| Servicio | Motivo del monitoreo | Endpoint |
|---|---|---|
| GitHub API | Repositorio y automatización CI/CD | `https://api.github.com` |
| PyPI | Registro de dependencias Python | `https://pypi.org/pypi/fastapi/json` |
| Python.org | Sitio oficial del lenguaje utilizado | `https://www.python.org/` |
| AWS | Proveedor Cloud de la solución | `https://aws.amazon.com/` |

Cada vez que se abre la página o se consulta `/api/services`, FastAPI ejecuta los chequeos en paralelo. Para cada servicio registra:

- código HTTP;
- latencia en milisegundos;
- fecha/hora UTC del chequeo;
- estado `Operativo` o `No disponible`.

Un servicio se considera operativo cuando responde con HTTP 200–399 dentro de 3 segundos. El objetivo es demostrar monitoreo funcional sin utilizar credenciales ni sistemas privados.

> La solución es académica y no representa monitoreo productivo de una organización real.

## Caso de estudio

Una organización requiere un portal liviano que permita comprobar, desde una sola interfaz, la disponibilidad de dependencias web utilizadas por su equipo TI. El proyecto se enfoca además en automatizar integración, pruebas, construcción de contenedores y despliegue mediante CI/CD.

## Requerimientos técnicos

| Elemento | Definición |
|---|---|
| Lenguaje | Python 3.12 |
| Framework | FastAPI |
| Puerto contenedor | 8000 |
| Puerto público | 80 |
| Persistencia | No requerida |
| Variables de entorno | `APP_ENV`, `APP_VERSION`, `DEPLOYED_AT` |
| Contenedor | Docker |
| Registro | Amazon ECR |
| Cloud | AWS, región `us-east-1` |
| Ejecución | Amazon EC2 `t4g.micro` + Docker |
| IaC | AWS CloudFormation |
| CI/CD | GitHub Actions |
| Autenticación CI/CD | GitHub OIDC hacia AWS IAM |

## Endpoints

- `/`: tablero visual y explicación del funcionamiento.
- `/health`: health check del propio contenedor.
- `/api/services`: resultado JSON de los chequeos HTTP.

## Estrategia Git

Se utiliza GitHub Flow. `main` representa la versión estable y los cambios se desarrollan en ramas `feature/*`, `fix/*` o `docs/*`. Se utilizan Pull Requests y commits con Conventional Commits.

El proyecto es individual. Por esta razón no existe un segundo integrante disponible para aprobar Pull Requests; se conserva de todas formas la trazabilidad mediante ramas, PR y validación automática.

## CI

`.github/workflows/ci.yml` ejecuta instalación de dependencias, Ruff, pip-audit, Pytest y construcción de la imagen Docker. Un error en cualquiera de estas etapas detiene el pipeline.

## CD

`.github/workflows/cd.yml` se ejecuta al integrar cambios en `main`:

1. resuelve la versión SemVer del archivo `VERSION`;
2. obtiene credenciales AWS temporales mediante OIDC;
3. construye la imagen ARM64;
4. publica la imagen versionada en Amazon ECR;
5. localiza la instancia EC2 por tag;
6. despliega mediante AWS Systems Manager;
7. valida `/health` desde la instancia y desde la URL pública.

## Infraestructura como Código

`infra/cloudformation.yml` declara VPC, subnet pública, Internet Gateway, routing, Security Group, ECR, IAM, Instance Profile y EC2. La infraestructura puede aprovisionarse y eliminarse desde el mismo código.

## Versiones

- `v1.0.0`: portal inicial y health check.
- `v1.1.0`: resumen de servicios operativos.
- `v1.2.0`: monitoreo HTTP real, código HTTP, latencia, hora de comprobación y explicación visible del funcionamiento.

## Seguridad

- No se guardan Access Keys en el repositorio.
- GitHub Actions usa OIDC y credenciales temporales.
- EC2 no expone SSH.
- El despliegue remoto usa Systems Manager.
- EBS está cifrado e IMDSv2 es obligatorio.
