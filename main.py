from datetime import date, timedelta

import yfinance as yf

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
