# merval-bot

[![Tests](https://github.com/federico0330/merval-bot/actions/workflows/tests.yml/badge.svg)](https://github.com/federico0330/merval-bot/actions/workflows/tests.yml)
[![Cierre semanal Merval](https://github.com/federico0330/merval-bot/actions/workflows/check.yml/badge.svg)](https://github.com/federico0330/merval-bot/actions/workflows/check.yml)

Bot que sigue acciones del Merval semana a semana y avisa por Telegram cuáles
vienen en alza.

## Qué hace

Cada viernes, después del cierre del mercado, baja la última vela semanal
cerrada de los tickers configurados, guarda los cierres en un Excel
(`registro_merval.xlsx`) y manda un mensaje a Telegram con el resumen. En el
Excel pinta de verde los cierres que superan al de la semana anterior, así se
ve de un vistazo qué papeles están subiendo. Si además el mínimo de la semana
perforó al mínimo previo (patrón de "toma de liquidez"), pinta el mínimo en
naranja y marca la acción con 🔥 en el mensaje.

El Excel queda versionado en el repo: cada corrida le suma columnas nuevas sin
tocar lo que ya estaba. Es idempotente, así que un re-run no duplica datos.

## Tickers seguidos

GGAL, YPFD, PAMP, BMA, TXAR, ALUA, CEPU, EDN, LOMA, TGSU2 — los más líquidos
del panel líder argentino.

## Requisitos

- Python 3.11 o superior
- Una cuenta de bot de Telegram (token y chat ID)

## Instalación

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Configuración

Copiá `.env.example` a `.env` y completá tus datos:

```bash
cp .env.example .env
```

```
TELEGRAM_TOKEN=tu_token_aca
CHAT_ID=tu_chat_id_aca
CHAT_ID_ADMIN=tu_chat_id_admin   # opcional, recibe los avisos de error
```

## Uso

```bash
python main.py
```

El flujo es: baja los datos, actualiza el Excel, arma el mensaje y lo envía a
Telegram. Si todo falla, manda un traceback al admin (sin el token).

## Tests

El proyecto tiene cobertura sobre la lógica determinística (cálculo de
alcistas, detección de toma de liquidez, idempotencia del Excel, formato del
mensaje, contrato de red mockeado).

```bash
pip install -r requirements-dev.txt
pytest -v
```

Los tests corren en CI en cada push a `main` y en cada PR.

## Automatización

Hay un workflow de GitHub Actions que corre el bot los **viernes 21:30 UTC**
(18:30 en Argentina, justo después del cierre del mercado) y commitea el Excel
actualizado. El token y el chat ID se guardan como Secrets del repo.

## Despliegue

### 1. Cargar los secrets

El workflow necesita el token del bot y tu chat ID. Nunca los pongas en el
código: van como Secrets del repositorio.

1. En GitHub, entrá al repo y abrí **Settings**.
2. En el menú lateral: **Secrets and variables → Actions**.
3. Tocá **New repository secret** y cargá:
   - `TELEGRAM_TOKEN` — el token de tu bot
   - `CHAT_ID` — tu chat ID
   - `CHAT_ID_ADMIN` — opcional, chat para los avisos de error

Los nombres tienen que ser exactos: el workflow los busca así.

### 2. Disparar el workflow a mano la primera vez

No hace falta esperar al viernes para probarlo:

1. Andá a la pestaña **Actions** del repo.
2. En la lista de la izquierda elegí **Cierre semanal Merval**.
3. A la derecha vas a ver el botón **Run workflow**. Tocalo y confirmá.
4. En unos segundos aparece la corrida. Si todo salió bien, te llega el mensaje
   a Telegram y el `registro_merval.xlsx` queda commiteado en el repo.

A partir de ahí corre solo cada viernes.

## Decisiones técnicas

- **openpyxl en lugar de pandas** para escribir el Excel: el coste de pandas
  no se justifica para escribir bloques pequeños y openpyxl da control fino
  sobre el formato (relleno de celdas, encabezados dinámicos).
- **Idempotencia por fecha**: la función `update_excel` chequea si la fecha de
  la vela ya está registrada antes de agregar un bloque nuevo. Un re-run del
  workflow no contamina el archivo.
- **Aislamiento de fallos por ticker**: si yfinance falla en un símbolo (red,
  rate limit, datos raros) el resto del reporte igual sale. Solo si fallan
  todos se reventa fuerte para que el admin se entere.
- **Sanitización del token**: el módulo `send_telegram` evita usar
  `raise_for_status()` porque su mensaje incluye la URL con el token. Arma su
  propia excepción sin exponer el secret.
- **Traceback al admin escapado y recortado**: Telegram cierra a 4096
  caracteres y rechaza HTML mal formado. El handler de error escapa el
  contenido y manda solo los últimos 3000 caracteres del traceback.
