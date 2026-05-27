# Devolución técnica — merval-bot

Este documento explica qué capacidades demuestra este proyecto y cómo se
traducen a problemas de retail multilocal.

## Qué demuestra el proyecto

El bot orquesta yfinance, openpyxl y la API de Telegram con manejo
defensivo: si yfinance falla en un ticker, los otros igual entran al
reporte; solo revienta fuerte cuando fallan todos. Si algo se rompe a
mitad del flujo, el admin recibe el traceback por Telegram.

El Excel es la fuente de verdad y se versiona en el repo. Cada corrida
chequea si la fecha ya está en el último bloque antes de agregar
columnas, así un re-run del workflow no contamina el archivo. Es
idempotente por fecha.

El token de Telegram no aparece en ningún log. La función
`send_telegram` no usa `raise_for_status()` (que incluiría la URL con el
token en el mensaje de error); arma su propia excepción. El handler del
error global escapa el traceback antes de mandárselo al admin.

Hay dos workflows de GitHub Actions. Uno corre el bot los viernes 21:30
UTC (post-cierre del mercado) y commitea el Excel actualizado. El otro
corre la suite de tests en cada push y PR a `main`.

Los 20 tests con pytest cubren la lógica determinística: cálculo de
alcistas, detección de toma de liquidez, idempotencia del Excel, formato
del mensaje y el contrato de red mockeado. La red real nunca se toca en
los tests.

## Cómo se traduce a retail multilocal

| Lo que hace el bot acá | Cómo aplica al negocio |
|---|---|
| Trae datos por API externa con aislamiento de fallos | Sincronización de catálogo desde un ERP central a cada sucursal — si un local pierde red, el resto sigue al día |
| Cron semanal disparado por GitHub Actions | Cron diario o por hora para alertas de stock crítico por sucursal, reportes a managers, reconciliación de inventario |
| Notificación por Telegram con HTML escapado | Reemplazable por WhatsApp Business, email, o webhook a Slack/Teams para alertas operativas |
| Idempotencia por fecha en el Excel | Idempotencia por SKU+sucursal+fecha en una tabla de movimientos, para que un reintento no duplique ajustes |
| Sanitización del token en logs | Misma técnica para API keys de gateway de pago, credenciales de ERP, tokens de proveedores |
| Aviso de error al admin con traceback escapado | Notificación automática a operaciones cuando un job de sincronización rompe en producción |

## Stack y decisiones

Python 3.11 sin frameworks pesados, así el proyecto se mantiene chico y
fácil de auditar.

openpyxl en lugar de pandas para escribir el Excel: el peso de pandas no
se justifica para bloques chicos, y openpyxl da control fino sobre el
formato (rellenos de celda, encabezados dinámicos).

`python-dotenv` para configuración local y Secrets de GitHub para
producción. Un solo lugar donde cambiar el token.

`pytest` con mocks de `unittest.mock` para no tocar la red en los tests.

## Lo que pulí en esta entrega

- Tests: 20 tests pasan en menos de 1 segundo (antes había 0).
- Workflow `tests.yml` que corre la suite en cada push y PR.
- README corregido: decía "lunes 13:00 UTC" cuando el cron real es viernes
  21:30 UTC. Ahora coinciden.
- README extendido con sección de tests y decisiones técnicas, badges de CI.
