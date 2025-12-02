"""Testes de integração simples da aplicação FastAPI principal.

Esses testes garantem que:
- o app inicializa sem erros
- a rota raiz ("/") responde com sucesso
"""

from fastapi.testclient import TestClient

from main import app


def test_root_endpoint_returns_ok_message():
    """A rota raiz deve responder 200 e conter a mensagem padrão."""
    client = TestClient(app)

    response = client.get("/")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "message" in data
    assert "HospiCast API" in data["message"]


def test_app_has_cors_middleware_configured():
    """Garantir que o middleware de CORS foi adicionado à aplicação."""
    # user_middleware contém a lista de middlewares adicionados via add_middleware
    cors_middlewares = [m for m in app.user_middleware if "CORS" in m.cls.__name__.upper()]
    assert cors_middlewares, "Deve existir pelo menos um middleware de CORS configurado"




