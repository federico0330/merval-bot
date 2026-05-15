# merval-bot

Bot que sigue acciones del Merval semana a semana y avisa por Telegram cuáles
vienen en alza.

## Qué hace

Cada lunes baja la última vela semanal cerrada de los tickers que le pasás,
guarda los cierres en un Excel (`registro_merval.xlsx`) y manda un mensaje a
Telegram con el resumen. En el Excel pinta de verde los cierres que superan al
de la semana anterior, así se ve de un vistazo qué papeles están subiendo.

El Excel queda versionado en el repo: cada corrida le suma columnas nuevas sin
tocar lo que ya estaba.

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
```

## Uso

```bash
python main.py
```

El flujo es: baja los datos, actualiza el Excel, arma el mensaje y lo envía a
Telegram.

## Automatización

Hay un workflow de GitHub Actions que corre el bot los lunes 13:00 UTC y commitea
el Excel actualizado. El token y el chat ID se guardan como Secrets del repo.
