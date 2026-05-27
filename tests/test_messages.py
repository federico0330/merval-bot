"""Tests sobre build_message: formato HTML para Telegram."""

import main


def _vela(fecha, close):
    return {"fecha": fecha, "open": 0, "high": 0, "low": 0, "close": close}


def test_build_message_sin_alcistas_informa_explicitamente():
    data = {"GGAL.BA": _vela("2026-05-25", 100.0)}
    msg = main.build_message(data, alcistas=[])

    assert "Cierre semanal Merval" in msg
    assert "Ninguna acción cerró alcista esta semana" in msg
    assert "GGAL.BA" in msg


def test_build_message_con_alcistas_incluye_variacion_y_lista():
    data = {"GGAL.BA": _vela("2026-05-25", 110.0)}
    alcistas = [{"ticker": "GGAL.BA", "variacion": 10.0, "barrida": False}]

    msg = main.build_message(data, alcistas)

    assert "<b>GGAL.BA</b>" in msg
    assert "+10.0%" in msg
    assert "ATENCIÓN" in msg


def test_build_message_marca_barrida_con_emoji_y_explicacion():
    data = {"GGAL.BA": _vela("2026-05-25", 110.0)}
    alcistas = [{"ticker": "GGAL.BA", "variacion": 10.0, "barrida": True}]

    msg = main.build_message(data, alcistas)

    assert "🔥" in msg
    assert "toma de liquidez" in msg


def test_build_message_no_explica_barrida_si_no_hay_ninguna():
    data = {"GGAL.BA": _vela("2026-05-25", 110.0)}
    alcistas = [{"ticker": "GGAL.BA", "variacion": 10.0, "barrida": False}]

    msg = main.build_message(data, alcistas)

    assert "toma de liquidez" not in msg
