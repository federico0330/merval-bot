# Devolución técnica — merval-bot

Este documento explica qué capacidades demuestra este proyecto y cómo se
traducen a problemas de retail multilocal.

## Qué demuestra el proyecto

**Automatización confiable contra APIs externas.** El bot orquesta yfinance,
openpyxl y la API de Telegram con manejo defensivo de fallos: aísla errores
por ticker (si yfinance se cae en uno, los otros igual entran al reporte),
revienta fuerte solo si TODO falla, y manda un traceback al admin en caso de
error catastrófico.

**Idempotencia.** El Excel es la fuente de verdad y se versiona en el repo.
Cada corrida chequea si la fecha ya existe en el último bloque antes de
agregar columnas, así un re-run del workflow no contamina el archivo.

**Manejo de secrets.** El token nunca se loguea: la función `send_telegram`
arma su propia excepción en lugar de usar `raise_for_status()` (que incluiría
la URL con el token), y el handler de error escapa el traceback antes de
mandárselo al admin por Telegram.

**CI/CD productivo.** Dos workflows de GitHub Actions: uno corre el bot los
viernes 21:30 UTC (post-cierre del mercado) y commitea el Excel; el otro
corre la suite de tests en cada push y PR a `main`.

**Tests sobre lógica determinística.** 20 tests con pytest cubren cálculo de
alcistas, detección del patrón "toma de liquidez", idempotencia del Excel,
formato del mensaje y contrato de red mockeado (la red real nunca se toca en
los tests).

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

- **Python 3.11+** sin frameworks pesados — el proyecto se mantiene chico,
  fácil de auditar, fácil de extender.
- **openpyxl en lugar de pandas** para escribir el Excel: el coste de pandas
  no se justifica para escribir bloques pequeños, y openpyxl da control fino
  sobre el formato (rellenos de celda, encabezados dinámicos).
- **python-dotenv** para configuración local, **Secrets de GitHub** para
  producción — un solo lugar donde cambiar el token.
- **pytest** con mocks de `unittest.mock` para no tocar la red en tests.

## Lo que pulí en esta entrega

- Tests: 20 tests pasan en menos de 1 segundo (antes había 0).
- Workflow `tests.yml` que corre la suite en cada push y PR.
- README corregido: decía "lunes 13:00 UTC" cuando el cron real es viernes
  21:30 UTC. Ahora coinciden.
- README extendido con sección de tests y decisiones técnicas, badges de CI.
