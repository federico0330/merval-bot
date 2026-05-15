# CLAUDE.md - merval-bot

## Skills Activas
- **Caveman**: Activo por defecto (modo conciso y directo, eficiencia de tokens).
- **Humanizer**: Aplicar siempre en README, mensajes de Telegram, comentarios y cualquier texto destinado a usuarios.
- **Napkin**: Memoria persistente del proyecto. Registrar decisiones, problemas encontrados y soluciones.
- **Skill Creator**: Usar solo si necesito crear una skill nueva.

## Reglas Generales del Proyecto

1. **Estilo de Respuesta (Caveman)**
   - Responder de forma corta, clara y técnica.
   - Código primero, explicaciones después y solo si son necesarias.
   - Usar bullet points y bloques de código limpios.

2. **Calidad Humana (Humanizer)**
   - Todo texto visible (README, mensajes de Telegram, commits, documentación) debe pasar por Humanizer.
   - Evitar lenguaje robótico, frases repetitivas y estructura demasiado perfecta.

3. **Memoria (Napkin)**
   - Registrar siempre:
     - Problemas con yfinance o pandas
     - Decisiones de formato del Excel
     - Errores encontrados en GitHub Actions
     - Cambios en la lógica de coloreado

4. **Optimización**
   - Evitar código innecesario.
   - Preferir soluciones simples y mantenibles.

## Reglas Específicas del Proyecto

### Estructura y Convenciones
- Python 3.11+
- Virtualenv en `.venv`
- Todo el código principal en `main.py`
- Usar `python-dotenv` para cargar variables de entorno
- Mantener el Excel `registro_merval.xlsx` versionado (NO ignorarlo)
- Usar `openpyxl` para manipular el Excel (no pandas)

### Funciones Obligatorias
- `fetch_weekly_data(tickers)` → devuelve dict con última vela semanal cerrada
- `update_excel(data, filename='registro_merval.xlsx')` → maneja creación, columnas dinámicas y resaltado verde
- `build_message(data, alcistas)` → mensaje en HTML para Telegram
- `send_telegram(message)` → usa `requests` y variables de entorno
- Flujo principal: fetch → update_excel → build_message → send_telegram

### Requisitos del Excel
- Detectar automáticamente la próxima "Semana N"
- Agregar siempre 5 columnas nuevas por ejecución
- Resaltado verde (`90EE90`) solo cuando el cierre actual > cierre anterior
- Mantener formato y datos existentes

### GitHub Actions
- Workflow en `.github/workflows/check.yml`
- Ejecutar los lunes a las 13:00 UTC
- Commit del Excel actualizado usando github-actions[bot]
- Usar Secrets para TELEGRAM_TOKEN y CHAT_ID

## Flujo de Trabajo Recomendado

1. Entender el pedido
2. Implementar o modificar código
3. Probar localmente (`python main.py`)
4. Aplicar Humanizer a cualquier texto visible
5. Actualizar Napkin con problemas/soluciones
6. Confirmar que todo funciona antes de pasar al siguiente paso

**Regla prioritaria**: El bot debe ser confiable, el Excel debe mantenerse intacto entre ejecuciones, y los mensajes de Telegram deben verse profesionales y claros.
