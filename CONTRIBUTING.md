# Convenciones de trabajo

## Ramas

- `feature/<descripcion>` para funcionalidades.
- `fix/<descripcion>` para correcciones.
- `docs/<descripcion>` para documentación.

## Commits

Se utiliza Conventional Commits.

Ejemplos:

- `feat: add health endpoint`
- `test: add API tests`
- `ci: add continuous integration workflow`
- `infra: define AWS environment with CloudFormation`
- `docs: document deployment architecture`

## Pull Requests

Todo cambio se propone mediante Pull Request hacia `main`. El PR debe tener una descripción clara y el pipeline CI debe finalizar correctamente antes de integrarse.
