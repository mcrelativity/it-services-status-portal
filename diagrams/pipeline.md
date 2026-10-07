# Pipeline CI/CD

```mermaid
flowchart TD
    PR[Push o Pull Request] --> CO[Checkout]
    CO --> DEP[Instalar dependencias]
    DEP --> LINT[Ruff]
    LINT -->|Falla| FAIL[Pipeline detenido]
    LINT --> AUDIT[pip-audit]
    AUDIT -->|Falla| FAIL
    AUDIT --> TEST[Pytest]
    TEST -->|Falla| FAIL
    TEST --> BUILD[Docker build]
    BUILD -->|Falla| FAIL
    BUILD --> OK[CI exitoso]

    MERGE[Merge a main + VERSION SemVer] --> OIDC[Autenticación OIDC AWS]
    OIDC --> PUSH[Build ARM64 + Push ECR]
    PUSH --> SSM[Despliegue remoto por SSM]
    SSM --> HEALTH[Health check local]
    HEALTH -->|Falla| FAILCD[CD fallido]
    HEALTH --> PUBLIC[Health check público]
    PUBLIC -->|Falla| FAILCD
    PUBLIC --> DONE[CD exitoso]
```

## Disparadores

- CI: `push` a `main`, `feature/**`, `fix/**`, `docs/**` y `pull_request` hacia `main`.
- CD: `push` a `main` después de integrar un Pull Request. La versión se toma de `VERSION` y debe cumplir SemVer `vX.Y.Z`.

## Condiciones de falla

El proceso se detiene si falla análisis estático, auditoría de dependencias, pruebas, construcción de imagen, publicación en ECR, despliegue mediante SSM o health check.
