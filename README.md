# Portal de Estado de Servicios TI

Proyecto individual para demostrar una solución DevOps CI/CD desplegada en AWS mediante Infraestructura como Código.

## Caso de estudio

Una organización requiere un portal web liviano que permita consultar el estado operativo de servicios tecnológicos institucionales. El proyecto se enfoca en la automatización del ciclo de integración y entrega, no en la complejidad funcional de la aplicación.

## Requerimientos técnicos

| Elemento | Definición |
|---|---|
| Lenguaje | Python 3.12 |
| Framework | FastAPI |
| Puerto contenedor | 8000 |
| Puerto público | 80 |
| Persistencia | No requerida: la aplicación no administra datos transaccionales |
| Variables de entorno | `APP_ENV`, `APP_VERSION`, `DEPLOYED_AT` |
| Contenedor | Docker |
| Registro | Amazon ECR |
| Cloud | AWS, región `us-east-1` |
| Ejecución | Amazon EC2 `t4g.micro` + Docker |
| IaC | AWS CloudFormation |
| CI/CD | GitHub Actions |
| Autenticación CI/CD | GitHub OIDC hacia AWS IAM, sin access keys persistentes |

## Alcance y usuarios

La solución publica una interfaz de consulta y endpoints de salud/servicios. Los usuarios previstos son personal interno y el docente evaluador. No existe autenticación de usuarios porque el contenido es únicamente demostrativo y no contiene información sensible.

## Endpoints

- `/`: interfaz web.
- `/health`: estado de la aplicación y versión desplegada.
- `/api/services`: estado de servicios en JSON.

## Estrategia Git

Se utiliza GitHub Flow:

1. `main` representa la versión estable.
2. Cada cambio se desarrolla en una rama `feature/*`, `fix/*` o `docs/*`.
3. Los cambios se incorporan mediante Pull Request.
4. CI debe finalizar correctamente antes del merge.
5. Los commits siguen Conventional Commits (`feat:`, `fix:`, `test:`, `ci:`, `docs:`, `infra:`).

> El proyecto es individual. Por esta razón, no existe un segundo integrante disponible para aprobar Pull Requests. Se mantiene de todas formas el flujo de PR, validación automática y trazabilidad.

## CI

El workflow `.github/workflows/ci.yml` ejecuta:

1. instalación de dependencias;
2. análisis estático con Ruff;
3. auditoría de dependencias con pip-audit;
4. pruebas con Pytest;
5. construcción de la imagen Docker.

## CD

El workflow `.github/workflows/cd.yml` se ejecuta automáticamente tras integrar cambios en `main`. La versión desplegada se obtiene del archivo `VERSION` y utiliza SemVer, por ejemplo `v1.0.0` y `v1.1.0`.

1. GitHub valida el valor SemVer declarado en `VERSION`.
2. GitHub obtiene credenciales temporales mediante OIDC.
3. Se construye la imagen ARM64.
4. La imagen versionada se publica en Amazon ECR.
5. GitHub Actions localiza la instancia por tag.
6. AWS Systems Manager ejecuta el despliegue sin necesidad de abrir SSH.
7. Se valida `/health` dentro de la instancia y desde la URL pública.

## Infraestructura como Código

`infra/cloudformation.yml` declara toda la infraestructura requerida:

- VPC;
- subnet pública;
- Internet Gateway y routing;
- Security Group;
- Amazon ECR;
- roles IAM de EC2 y GitHub Actions;
- Instance Profile;
- instancia EC2 ARM64;
- instalación automatizada de Docker mediante User Data.

### Aprovisionamiento

```bash
aws cloudformation deploy \
  --template-file infra/cloudformation.yml \
  --stack-name devops-status-portal \
  --capabilities CAPABILITY_NAMED_IAM \
  --region us-east-1
```

### Eliminación

```bash
aws cloudformation delete-stack \
  --stack-name devops-status-portal \
  --region us-east-1
```

## Versiones evaluables

- `v1.0.0`: portal inicial, `/health` y API de servicios.
- `v1.1.0`: segunda versión sucesiva con una mejora visible que se incorporará mediante Pull Request y nuevo despliegue.

## Evidencias

Las evidencias se almacenan/documentan en `docs/evidencias/` y deben incluir historial Git, PR, CI, ECR, CloudFormation, EC2, CD, ambas versiones y URL funcional.

## Seguridad

- No se almacenan credenciales AWS en el repositorio.
- GitHub Actions utiliza OIDC y credenciales temporales.
- EC2 no expone SSH.
- El despliegue remoto utiliza AWS Systems Manager.
- El volumen EBS se cifra.
- IMDSv2 es obligatorio.
- ECR realiza análisis de imágenes al publicarlas.

## Arquitectura y pipeline

- [Arquitectura](diagrams/architecture.md)
- [Pipeline](diagrams/pipeline.md)
