"""Tests sobre send_telegram y notify_all: contrato de red mockeado."""

from unittest.mock import MagicMock, patch

import pytest

import main


@pytest.fixture
def env_tokens(monkeypatch):
    monkeypatch.setenv("TELEGRAM_TOKEN", "fake-token-12345")
    monkeypatch.setenv("CHAT_ID", "111")


def test_send_telegram_falla_si_falta_token(monkeypatch):
    monkeypatch.delenv("TELEGRAM_TOKEN", raising=False)
    with pytest.raises(RuntimeError, match="TELEGRAM_TOKEN"):
        main.send_telegram("hola", chat_id="111")


def test_send_telegram_falla_si_falta_chat_id(env_tokens):
    with pytest.raises(RuntimeError, match="chat_id"):
        main.send_telegram("hola", chat_id=None)


def test_send_telegram_envia_post_con_parse_mode_html(env_tokens):
    mock_resp = MagicMock(ok=True)
    mock_resp.json.return_value = {"ok": True}

    with patch("main.requests.post", return_value=mock_resp) as mock_post:
        result = main.send_telegram("hola <b>mundo</b>", chat_id="111")

    mock_post.assert_called_once()
    _, kwargs = mock_post.call_args
    assert kwargs["data"]["parse_mode"] == "HTML"
    assert kwargs["data"]["chat_id"] == "111"
    assert kwargs["timeout"] == 15
    assert result == {"ok": True}


def test_send_telegram_no_filtra_token_en_mensaje_de_error(env_tokens):
    """El token jamás debe aparecer en la excepción que se propaga."""
    mock_resp = MagicMock(ok=False, status_code=401, text="Unauthorized")
    with patch("main.requests.post", return_value=mock_resp):
        with pytest.raises(RuntimeError) as exc:
            main.send_telegram("hola", chat_id="111")

    assert "fake-token-12345" not in str(exc.value)
    assert "401" in str(exc.value)


def test_notify_all_envia_a_principal_y_admin_si_distintos(env_tokens, monkeypatch):
    monkeypatch.setenv("CHAT_ID_ADMIN", "222")
    mock_resp = MagicMock(ok=True)
    mock_resp.json.return_value = {"ok": True}

    with patch("main.requests.post", return_value=mock_resp) as mock_post:
        main.notify_all("hola")

    assert mock_post.call_count == 2


def test_notify_all_no_duplica_envio_si_admin_es_el_mismo_chat(env_tokens, monkeypatch):
    monkeypatch.setenv("CHAT_ID_ADMIN", "111")
    mock_resp = MagicMock(ok=True)
    mock_resp.json.return_value = {"ok": True}

    with patch("main.requests.post", return_value=mock_resp) as mock_post:
        main.notify_all("hola")

    assert mock_post.call_count == 1
