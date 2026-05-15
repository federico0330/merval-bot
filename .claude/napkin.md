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

## Pendiente
- main.py vacío: falta implementar fetch/update_excel/build_message/send_telegram.
