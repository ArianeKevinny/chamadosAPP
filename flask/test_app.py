from app import app
import pytest

aplicacao = app.test_client()

def login(client, username):
    return client.post('/usuario/login', data=dict(
        usuario=username,
        senha='654321'
    ), follow_redirects=True)

def logout(client):
    return client.get('/usuario/logout', follow_redirects=True)

@pytest.fixture
def client():
    return (aplicacao)

@pytest.fixture
def preparacao():
    app.config['WTF_CSRF_ENABLED'] = False
    yield
    app.config['WTF_CSRF_ENABLED'] = True

def test_0_principal(client):
    rv = client.get('/',follow_redirects=True)
    assert 200 == rv.status_code

def test_1_principal(client):
    rv = client.get('/',follow_redirects=True)
    assert b'Nome de usu' in rv.data
    assert b'Senha:' in rv.data

@pytest.mark.usefixtures('preparacao')
def test_2_login(client):
    rv = login(client,'Usuario')
    assert b'autenticado com sucesso' in rv.data


def test_3_chave_cadastrar_get(client):
    rv = client.get('/chave/cadastrar',follow_redirects=True)
    assert b'Nome da chave' in rv.data

def test_4_chave_listar(client):
    rv = client.get('/chave/listar',follow_redirects=True)
    assert rv.status_code==200

@pytest.mark.usefixtures('preparacao')
def test_5_login_errado(client):
    rv = login(client,'UsuarioNaoExistente')
    assert b'rio e/ou senha' in rv.data

def test_6_usuario_listar(client):
    rv = client.get('/usuario/listar',follow_redirects=True)
    assert rv.status_code==200

def test_7_chave_listar_emprestimos(client):
    rv = client.get('/chave/listar_emprestimos',follow_redirects=True)
    assert rv.status_code==200

