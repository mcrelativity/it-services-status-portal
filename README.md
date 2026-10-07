# Portal de Monitoreo de Servicios TI

Proyecto académico orientado a demostrar un flujo DevOps completo con **Git, CI/CD, Docker, AWS e Infraestructura como Código (IaC)**.

La aplicación se encuentra desplegada en AWS y realiza chequeos HTTP reales sobre servicios públicos relacionados con el desarrollo y despliegue del proyecto.

## Enlaces de revisión

- **Aplicación desplegada:** http://ec2-52-72-236-138.compute-1.amazonaws.com
- **Health check:** http://ec2-52-72-236-138.compute-1.amazonaws.com/health
- **API de monitoreo:** http://ec2-52-72-236-138.compute-1.amazonaws.com/api/services
- **GitHub Actions:** https://github.com/mcrelativity/it-services-status-portal/actions
- **Pull Requests:** https://github.com/mcrelativity/it-services-status-portal/pulls

## ¿Qué hace la aplicación?

El portal comprueba en tiempo real la disponibilidad de cuatro servicios públicos relacionados con el proyecto:

| Servicio | Motivo del monitoreo | Endpoint |
|---|---|---|
| GitHub API | Repositorio y automatización CI/CD | `https://api.github.com` |
| PyPI | Registro utilizado para obtener dependencias Python | `https://pypi.org/pypi/fastapi/json` |
| Python.org | Sitio oficial del lenguaje utilizado | `https://www.python.org/` |
| AWS | Proveedor Cloud donde se ejecuta la solución | `https://aws.amazon.com/` |

Cada vez que se abre la página principal o se consulta `/api/services`, FastAPI ejecuta los chequeos HTTP en paralelo.

Para cada servicio se registra:

- código de respuesta HTTP;
- latencia en milisegundos;
- fecha y hora UTC del chequeo;
- estado `Operativo` o `No disponible`.

Un servicio se considera **Operativo** cuando responde con un código HTTP entre 200 y 399 dentro de un máximo de 3 segundos. Si el endpoint no responde, excede el tiempo configurado o devuelve un error, la aplicación lo marca como **No disponible**.

> La solución tiene fines académicos y no representa una plataforma de monitoreo productiva de una empresa real.

## Caso de estudio

Una organización requiere un portal web liviano que permita comprobar desde una sola interfaz la disponibilidad de dependencias web utilizadas por su equipo TI.

Además de la funcionalidad de monitoreo, el proyecto busca automatizar el ciclo completo de integración, pruebas, construcción de contenedores, publicación de imágenes y despliegue a Cloud mediante CI/CD.

## Requerimientos técnicos

| Elemento | Definición |
|---|---|
| Lenguaje | Python 3.12 |
| Framework | FastAPI |
| Puerto del contenedor | 8000 |
| Puerto público | 80 |
| Persistencia | No requerida |
| Variables de entorno | `APP_ENV`, `APP_VERSION`, `DEPLOYED_AT` |
| Contenedor | Docker |
| Registro de imágenes | Amazon ECR |
| Cloud | AWS |
| Región | `us-east-1` |
| Ejecución | Amazon EC2 `t4g.micro` + Docker |
| IaC | AWS CloudFormation |
| CI/CD | GitHub Actions |
| Autenticación hacia AWS | GitHub OIDC + IAM |

## Estructura del repositorio

```text
it-services-status-portal/
├── .github/
│   └── workflows/
│       ├── ci.yml
│       └── cd.yml
├── app/
│   ├── main.py
│   ├── static/
│   └── templates/
├── diagrams/
├── docs/
├── infra/
│   └── cloudformation.yml
├── tests/
├── .gitignore
├── Dockerfile
├── README.md
├── VERSION
├── requirements.txt
└── requirements-dev.txt
```

## Endpoints

| Endpoint | Función |
|---|---|
| `/` | Tablero web y explicación visual del monitoreo |
| `/health` | Health check del propio contenedor y versión desplegada |
| `/api/services` | Resultado JSON de los chequeos HTTP |

## Estrategia Git

Se utiliza **GitHub Flow**.

- `main` representa la versión estable.
- Los cambios se desarrollan en ramas `feature/*`, `fix/*` o `docs/*`.
- Los cambios se integran mediante **Pull Requests**.
- Antes del merge se realiza revisión técnica mediante CI y validaciones automáticas.
- Los commits siguen **Conventional Commits**, utilizando prefijos como `feat:`, `fix:`, `test:`, `ci:`, `docs:` e `infra:`.

### Protección de la rama principal

La rama `main` está protegida mediante el ruleset **`protect main`**.

Este ruleset:

- exige integración mediante Pull Request;
- bloquea la eliminación de la rama;
- bloquea cambios non-fast-forward;
- mantiene controles asociados al flujo de revisión del repositorio.

## Integración Continua (CI)

El pipeline se encuentra definido como código en:

```text
.github/workflows/ci.yml
```

Se ejecuta ante cambios en `main`, ramas de trabajo y Pull Requests.

Etapas principales:

1. checkout del repositorio;
2. instalación de dependencias;
3. análisis estático con **Ruff**;
4. auditoría de dependencias con **pip-audit**;
5. ejecución de pruebas con **Pytest**;
6. construcción de la imagen Docker.

Si cualquiera de estas etapas falla, el pipeline se detiene y registra la ejecución como fallida.

## Entrega Continua (CD)

El proceso se encuentra definido en:

```text
.github/workflows/cd.yml
```

El despliegue se ejecuta después de integrar cambios en `main`.

Flujo:

1. obtiene la versión declarada en `VERSION`;
2. valida el formato SemVer;
3. solicita credenciales temporales de AWS mediante OIDC;
4. inicia sesión en Amazon ECR;
5. construye la imagen Docker ARM64;
6. publica la imagen versionada en ECR;
7. localiza la instancia EC2 mediante tags;
8. realiza el despliegue mediante AWS Systems Manager;
9. ejecuta el health check dentro de la instancia;
10. comprueba la aplicación desde su URL pública.

No se almacenan Access Keys permanentes de AWS en el repositorio.

## Infraestructura como Código

Toda la infraestructura principal está declarada en:

```text
infra/cloudformation.yml
```

La plantilla crea y configura:

- VPC;
- subnet pública;
- Internet Gateway;
- tabla de rutas;
- Security Group;
- Amazon ECR;
- roles IAM;
- Instance Profile;
- instancia EC2 ARM64;
- configuración necesaria para AWS Systems Manager y despliegue automatizado.

### Aprovisionamiento

Desde una terminal con AWS CLI autenticado:

```bash
aws cloudformation deploy \
  --template-file infra/cloudformation.yml \
  --stack-name devops-status-portal \
  --capabilities CAPABILITY_NAMED_IAM \
  --region us-east-1
```

La operación debe finalizar con el stack en estado `CREATE_COMPLETE` o `UPDATE_COMPLETE`.

### Eliminación del ambiente

```bash
aws cloudformation delete-stack \
  --stack-name devops-status-portal \
  --region us-east-1
```

El ambiente se mantiene activo mientras dure el período de revisión académica.

## Contenedores

La aplicación se empaqueta mediante el `Dockerfile` versionado en el repositorio.

El contenedor:

- utiliza Python 3.12;
- instala únicamente las dependencias requeridas;
- expone el puerto 8000;
- ejecuta FastAPI mediante Uvicorn;
- incorpora un health check;
- se publica en Amazon ECR antes del despliegue.

## Versionamiento

Se utiliza versionamiento semántico mediante el archivo `VERSION`.

Versiones desplegadas:

- **v1.0.0:** portal inicial y health check.
- **v1.1.0:** incorporación del resumen de servicios operativos.
- **v1.2.0:** monitoreo HTTP real, código de respuesta, latencia, hora del chequeo y explicación visible del funcionamiento.

Las tres imágenes versionadas permanecen publicadas en Amazon ECR como evidencia del proceso de Entrega Continua.

## Seguridad

Se aplicaron las siguientes medidas:

- las credenciales AWS no se almacenan en el código;
- GitHub Actions utiliza OIDC y credenciales temporales;
- la instancia EC2 no expone SSH;
- el despliegue remoto se realiza mediante AWS Systems Manager;
- IMDSv2 es obligatorio;
- el volumen EBS se encuentra cifrado;
- Amazon ECR realiza análisis de imágenes al publicarlas;
- la rama `main` está protegida mediante ruleset.

## Arquitectura y pipeline

La documentación gráfica se encuentra en:

- [Arquitectura de la solución](diagrams/architecture.md)
- [Pipeline CI/CD](diagrams/pipeline.md)

## Evidencias de implementación

Las evidencias verificables se encuentran distribuidas entre:

- historial de commits;
- Pull Requests;
- GitHub Actions;
- plantilla CloudFormation versionada;
- Amazon ECR;
- instancia EC2;
- aplicación pública;
- informe técnico final.

Repositorio: https://github.com/mcrelativity/it-services-status-portal
