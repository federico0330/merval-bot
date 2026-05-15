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

## Excel (openpyxl)
- Layout: col A = Ticker; cada semana = bloque de 5 cols (Fecha, Apertura, Máximo, Mínimo, Cierre).
- N de semana se deduce: `(max_column - 1) // 5 + 1`. No se guarda en ningún lado.
- Cierre semana N en columna `1 + 5*N`; cierre N-1 en `1 + 5*(N-1)`.
- Verde `90EE90` solo si cierre actual > cierre anterior (N>1).
- `update_excel` devuelve lista de alcistas: `[{ticker, variacion}]`.

## GitHub Actions
- Workflow `.github/workflows/check.yml`: cron `0 13 * * 1` (lunes 13:00 UTC) + workflow_dispatch.
- Python 3.11 (el local es 3.14, pero CI fija 3.11).
- Commit del Excel con `github-actions[bot]`; usa email `41898282+github-actions[bot]@users.noreply.github.com`.
- Step de commit chequea `git diff --staged --quiet` para no commitear si no hubo cambios.

## Pendiente
- main.py completo y probado (envío Telegram OK). Falta: init de repo git y subir a GitHub.
