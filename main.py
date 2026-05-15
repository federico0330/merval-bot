import os
from datetime import date, timedelta

import yfinance as yf
from openpyxl import Workbook, load_workbook
from openpyxl.styles import PatternFill

VERDE = PatternFill(start_color='90EE90', end_color='90EE90', fill_type='solid')

TICKERS = [
    'GGAL.BA', 'YPFD.BA', 'PAMP.BA', 'BMA.BA', 'TXAR.BA',
    'ALUA.BA', 'CEPU.BA', 'EDN.BA', 'LOMA.BA', 'TGSU2.BA',
]


def fetch_weekly_data(tickers):
    """Baja velas semanales y devuelve la última completamente cerrada por ticker.

    Una vela semanal queda cerrada recién cuando termina su semana. yfinance
    incluye la semana en curso como última fila, así que se descarta todo lo
    que pertenezca a la semana actual o posterior.
    """
    today = date.today()
    current_monday = today - timedelta(days=today.weekday())

    data = {}
    for ticker in tickers:
        df = yf.Ticker(ticker).history(period='3mo', interval='1wk')

        if df.empty:
            data[ticker] = None
            continue

        closed = df[[d.date() < current_monday for d in df.index]]
        if closed.empty:
            data[ticker] = None
            continue

        last = closed.iloc[-1]
        data[ticker] = {
            'fecha': closed.index[-1].date().isoformat(),
            'open': round(float(last['Open']), 2),
            'high': round(float(last['High']), 2),
            'low': round(float(last['Low']), 2),
            'close': round(float(last['Close']), 2),
        }

    return data


def update_excel(data, filename='registro_merval.xlsx'):
    """Registra la semana en el Excel agregando 5 columnas y devuelve los alcistas.

    Cada corrida suma un bloque de 5 columnas (fecha + OHLC). El número de semana
    se deduce contando los bloques ya escritos. Si hay semana previa, el cierre
    que la supera se pinta de verde.
    """
    if os.path.exists(filename):
        wb = load_workbook(filename)
        ws = wb.active
    else:
        wb = Workbook()
        ws = wb.active
        ws['A1'] = 'Ticker'
        for i, ticker in enumerate(data, start=2):
            ws.cell(row=i, column=1, value=ticker)

    # Bloques de 5 columnas ya escritos -> próxima semana
    semanas_previas = (ws.max_column - 1) // 5
    n = semanas_previas + 1

    base = 1 + 5 * (semanas_previas)  # última columna ocupada
    col_fecha = base + 1
    col_open = base + 2
    col_high = base + 3
    col_low = base + 4
    col_close = base + 5
    col_close_prev = base if n > 1 else None

    encabezados = [
        (col_fecha, f'Semana {n} - Fecha'),
        (col_open, f'Semana {n} - Apertura'),
        (col_high, f'Semana {n} - Máximo'),
        (col_low, f'Semana {n} - Mínimo'),
        (col_close, f'Semana {n} - Cierre'),
    ]
    for col, texto in encabezados:
        ws.cell(row=1, column=col, value=texto)

    # Mapa ticker -> fila a partir de la columna A
    filas = {}
    for fila in range(2, ws.max_row + 1):
        nombre = ws.cell(row=fila, column=1).value
        if nombre:
            filas[nombre] = fila

    alcistas = []
    for ticker, vela in data.items():
        if vela is None or ticker not in filas:
            continue
        fila = filas[ticker]

        ws.cell(row=fila, column=col_fecha, value=vela['fecha'])
        ws.cell(row=fila, column=col_open, value=vela['open'])
        ws.cell(row=fila, column=col_high, value=vela['high'])
        ws.cell(row=fila, column=col_low, value=vela['low'])
        celda_close = ws.cell(row=fila, column=col_close, value=vela['close'])

        if col_close_prev is not None:
            cierre_prev = ws.cell(row=fila, column=col_close_prev).value
            if isinstance(cierre_prev, (int, float)) and vela['close'] > cierre_prev:
                celda_close.fill = VERDE
                variacion = (vela['close'] - cierre_prev) / cierre_prev * 100
                alcistas.append({'ticker': ticker, 'variacion': round(variacion, 2)})

    wb.save(filename)
    return alcistas


if __name__ == '__main__':
    resultados = fetch_weekly_data(TICKERS)

    header = f"{'Ticker':<10} {'Fecha':<12} {'Open':>10} {'High':>10} {'Low':>10} {'Close':>10}"
    print(header)
    print('-' * len(header))

    for ticker, vela in resultados.items():
        if vela is None:
            print(f"{ticker:<10} {'sin datos':<12}")
            continue
        print(
            f"{ticker:<10} {vela['fecha']:<12} "
            f"{vela['open']:>10.2f} {vela['high']:>10.2f} "
            f"{vela['low']:>10.2f} {vela['close']:>10.2f}"
        )

    alcistas = update_excel(resultados)
    print(f"\nAlcistas: {alcistas}")
