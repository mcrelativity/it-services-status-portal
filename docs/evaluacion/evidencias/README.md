# Evidencias de la Evaluación 4

Verificación efectuada en AWS el 16 de noviembre de 2026 sobre la revisión de código `e880a7d`. Este índice resume los resultados verificados. Las capturas de consola, las series, los mensajes y los registros originales se conservan en el paquete de evaluación para revisión docente.

| Evidencia | Resultado verificado |
|---|---|
| E01 · Infraestructura | CloudFormation separó los stacks de artefactos, portal y pipeline. |
| E02 · Portal | HTTPS devolvió HTTP 200 y cuatro comprobaciones. `/health` confirmó la versión v1.3.0 y la revisión. |
| E03 · Monitoreo | Se comprobaron las métricas de tráfico, errores y latencia, los logs de API Gateway y las sondas de Lambda. |
| E04 · Incidente | La prueba HTTP 404 activó la alarma de 4xx. SNS envió la notificación y se confirmó su recepción en SQS. |
| E05 · Auditoría | CloudTrail multirregión registró cambios de administración y los entregó a S3. La comprobación de integridad validó el digest disponible. |
| E06 · Pruebas | La publicación en S3 disparó CodePipeline mediante EventBridge. CodeBuild aprobó las ocho pruebas y verificó la revisión por HTTPS. |
| E07 · Seguridad | Se verificaron roles de servicio por función, credenciales temporales, rutas GET explícitas, TLS, cifrado y bloqueo de acceso público en S3. El rol de CodeBuild recibió `AccessDenied` al intentar listar el bucket de auditoría. |

## Correspondencia con la pauta

| Criterio | Referencia |
|---|---|
| 1. Métricas y logs | E03 |
| 2. Detección de incidentes | E04 |
| 3. Registro de acciones | E05 |
| 4. Justificación de señales | Informe, sección Monitoreo |
| 5. Pruebas automatizadas | E06 |
| 6. Integración con DevOps | E06 |
| 7. Correspondencia de pruebas y requisitos | Informe, matrices de requisitos y pruebas |
| 8. Mínimo privilegio | E06 y E07 |
| 9. Protección de credenciales | E06 y E07 |
| 10. Accesos restringidos | E07 |
| 11. Controles adicionales y trazabilidad | E05 y E07 |

- [Informe técnico en PDF](../Informe-Evaluacion-4.pdf)
- [Video de demostración (3 min 28 s)](../Demostracion-Evaluacion-4.mp4)
