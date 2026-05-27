"""Tests sobre fetch_weekly_data: aislamiento de fallos por ticker."""

from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

import main


def _df_vela(fecha_lunes, close):
    """Construye un DataFrame estilo yfinance con una sola vela semanal."""
    idx = pd.DatetimeIndex([pd.Timestamp(fecha_lunes)])
    return pd.DataFrame(
        {
            "Open": [100.0],
            "High": [110.0],
            "Low": [95.0],
            "Close": [close],
        },
        index=idx,
    )


def _mock_yf_ticker(df):
    mock = MagicMock()
    mock.history.return_value = df
    return mock


def test_fetch_aisla_fallo_de_un_ticker_y_devuelve_el_resto():
    """Si yfinance falla en un ticker, los otros igual entran al reporte."""

    def side_effect(symbol):
        if symbol == "FAIL.BA":
            raise RuntimeError("rate limit simulado")
        return _mock_yf_ticker(_df_vela("2026-05-18", 108.0))

    with patch("main.yf.Ticker", side_effect=side_effect):
        data = main.fetch_weekly_data(["GGAL.BA", "FAIL.BA"])

    assert data["FAIL.BA"] is None
    assert data["GGAL.BA"] is not None
    assert data["GGAL.BA"]["close"] == 108.0


def test_fetch_falla_fuerte_si_todos_los_tickers_fallan():
    """Sin datos reales, mejor reventar que mandar un reporte vacío."""
    with patch("main.yf.Ticker", side_effect=RuntimeError("apocalipsis")):
        with pytest.raises(RuntimeError, match="ningún ticker"):
            main.fetch_weekly_data(["GGAL.BA", "YPFD.BA"])


def test_fetch_descarta_vela_si_dataframe_vacio():
    with patch("main.yf.Ticker", return_value=_mock_yf_ticker(pd.DataFrame())):
        with pytest.raises(RuntimeError):
            main.fetch_weekly_data(["GGAL.BA"])
