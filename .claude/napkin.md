# Napkin - merval-bot

## Entorno
- Python del sistema: 3.14.4. venv en `.venv`.
- pandas 3.0.3 + yfinance 1.3.0 instalan y se importan OK en Python 3.14.
  Si aparecen warnings/errores raros de pandas, sospechar de la 3.x antes que del código.
- Proyecto creado bajo `root` al inicio; se hizo `chown` a `federico`. Si vuelven
  errores EACCES, revisar dueño de los archivos.

## Decisiones
- `*.xlsx` NO va al .gitignore: el Excel `registro_merval.xlsx` se versiona.
- Token Optimizer no es skill instalada; lo cubre Caveman.
- `fetch_weekly_data` incluye la vela de la semana EN CURSO los viernes/fin de
  semana (`today.weekday() >= 4`): el bot corre tras el cierre del viernes, así
  que esa vela ya es definitiva. De lunes a jueves solo toma semanas pasadas.
  El filtro usa `limite` (lunes actual, o +1 día los viernes/finde).

## Excel (openpyxl)
- Layout: col A = Ticker; cada semana = bloque de 5 cols (Fecha, Apertura, Máximo, Mínimo, Cierre).
- N de semana se deduce: `(max_column - 1) // 5 + 1`. No se guarda en ningún lado.
- Cierre semana N en columna `1 + 5*N`; cierre N-1 en `1 + 5*(N-1)`.
- Verde `90EE90` en celda de cierre solo si cierre actual > cierre anterior (N>1).
- Naranja `FFA500` en celda de mínimo: patrón "toma de liquidez" (barrida) →
  alcista que ADEMÁS perforó el mínimo anterior (`mínimo_x < mínimo_x-1`).
  Mínimo semana N en columna `5*N` (= `col_cierre - 1`).
- `update_excel` devuelve lista de alcistas: `[{ticker, variacion, barrida}]`.
  `barrida` es bool; en el mensaje de Telegram se marca con 🔥 + leyenda.

## GitHub Actions
- Workflow `.github/workflows/check.yml`: cron `30 21 * * 5` (viernes 21:30 UTC =
  18:30 ART, tras el cierre del mercado) + workflow_dispatch.
- Argentina es UTC-3 fijo (sin horario de verano), así que el offset no cambia.
- Python 3.11 (el local es 3.14, pero CI fija 3.11).
- Commit del Excel con `github-actions[bot]`; usa email `41898282+github-actions[bot]@users.noreply.github.com`.
- Step de commit chequea `git diff --staged --quiet` para no commitear si no hubo cambios.

## Robustez / seguridad (QA)
- `update_excel` es IDEMPOTENTE: si la última semana ya tiene la fecha de los datos,
  no agrega bloque. Un re-run (manual o reintento de Actions) no duplica columnas.
- No usar `resp.raise_for_status()` en llamadas a Telegram: su mensaje incluye la URL
  con el token del bot → se filtra a logs y avisos. Usar error propio.
- El aviso de error a Telegram escapa HTML (`html.escape`) y se recorta a 3000 chars
  (límite 4096). Sin eso, un `<` o `&` en el traceback rompe el envío.
- `fetch_weekly_data` aísla cada ticker con try/except; si fallan TODOS lanza error.
- Trampa: correr `main.py` para probar AGREGA una semana al Excel. Para tests usar
  archivo aparte (`/tmp/...`) o no llamar a la corrida completa.

## Pendiente
- Cargar secrets en GitHub (TELEGRAM_TOKEN, CHAT_ID, CHAT_ID_ADMIN opcional).
