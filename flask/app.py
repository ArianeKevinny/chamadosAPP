from flask import Flask
from waitress import serve
from flask import render_template
from flask import request,url_for,redirect,flash,make_response
from flask_bootstrap import Bootstrap
from flask_wtf.csrf import CSRFProtect
import logging
import os
import datetime
from formUsuario import UsuarioForm
from formChamado import ChamadoForm
from flask_session import Session
from flask import session
from formLogin import LoginForm
import hashlib
import json
from flask_json import FlaskJSON, JsonError, json_response, as_json

app = Flask(__name__)
bootstrap = Bootstrap(app)
CSRFProtect(app)
CSV_DIR = '/flask/'

app.config['SESSION_TYPE'] = 'filesystem'
app.config['SECRET_KEY'] = os.urandom(24)
app.config['WTF_CSRF_SSL_STRICT'] = False
Session(app)
FlaskJSON(app)
app.config['JSON_ADD_STATUS'] = False

logging.basicConfig(filename=CSV_DIR + 'app.log', filemode='w', format='%(asctime)s %(name)s - %(levelname)s - %(message)s',level=logging.DEBUG)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + CSV_DIR + 'bd.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['TEMPLATES_AUTO_RELOAD'] = True

from database import db
db.init_app(app)

from Usuarios import Usuario
from Chamados import Chamado


@app.before_first_request
def inicializar_bd():
    #db.drop_all()
    db.create_all()

@app.route('/')
def root():
    if session.get('autenticado',False)==False:
        return (redirect(url_for('login')))
    return (render_template('index.html'))
        
@app.route('/chamado/cadastrar',methods=['POST','GET'])
def cadastrar_chamado():
    if session.get('autenticado',False)==False:
        return (redirect(url_for('login')))
    form = ChamadoForm()
    if form.validate_on_submit():
        #PROCESSAMENTO DOS DADOS RECEBIDOS
        solicitante = request.form['solicitante']
        sertorChamado = request.form['sertorChamado']
        novoChamado = Chamado(solicitante=solicitante,sertorChamado=sertorChamado)
        db.session.add(novoChamado)
        db.session.commit()
        flash('Chamado aberto com sucesso!')
        return(redirect(url_for('root')))
    return (render_template('form.html',form=form,action=url_for('cadastrar_chamado')))

@app.route('/chamado/listar')
def listar_chamado():
    chamados = Chamado.query.order_by(Chamado.data_abertura).all()
    return(render_template('chamados.html',chamados=chamados))

@app.route('/usuario/listar')
def listar_usuarios():
    if session.get('autenticado',False)==False:
        return (redirect(url_for('login')))
    usuarios = Usuario.query.order_by(Usuario.nome).all()
    return(render_template('usuarios.html',usuarios=usuarios))

@app.route('/usuario/cadastrar',methods=['POST','GET'])
def cadastrar_usuario():
    if session.get('autenticado',False)==False:
        return (redirect(url_for('login')))
    form = UsuarioForm()
    if form.validate_on_submit():
        #PROCESSAMENTO DOS DADOS RECEBIDOS
        nome = request.form['nome']
        username = request.form['username']
        email = request.form['email']
        telefone = request.form['telefone']
        setor = request.form['setor']
        senha = request.form['senha']
        senhahash = hashlib.sha1(senha.encode('utf8')).hexdigest()
        novoUsuario = Usuario(nome=nome,username=username,email=email,telefone=telefone,setor=setor,senha=senhahash)
        db.session.add(novoUsuario)
        db.session.commit()
        flash(u'Usuário cadastrado com sucesso!')
        return(redirect(url_for('root')))
    return (render_template('form.html',form=form,action=url_for('cadastrar_usuario')))


'''
Manipulando os Chamados
'''

@app.route('/chamado/encerrar/<id_chamado>',methods=['GET','POST'])
def encerrar_chamado(id_chamado):
    if session.get('autenticado',False)==False:
        return (redirect(url_for('login')))
    id_chamado = int(id_chamado)
    chamado = Chamado.query.get(id_chamado)
    chamado.data_fechamento = datetime.datetime.now()
    db.session.commit()
    return (redirect(url_for('root')))

@app.route('/chamado/remover/<id_chamado>',methods=['GET','POST'])
def remover_chamado(id_chamado):
    if session.get('autenticado',False)==False:
        return (redirect(url_for('login')))
    id_chamado = int(id_chamado)
    chamado = Chamado.query.get(id_chamado)
    db.session.delete(chamado)
    db.session.commit()
    return (redirect(url_for('root')))

'''
Rotas de Login e Logout
'''

@app.route('/usuario/login',methods=['POST','GET'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        #PROCESSAMENTO DOS DADOS RECEBIDOS
        usuario = request.form['usuario']
        senha = request.form['senha']
        senhahash = hashlib.sha1(senha.encode('utf8')).hexdigest()
        #Verificar se existe alguma linha na tabela usuários com o login e senha recebidos
        linha = Usuario.query.filter(Usuario.username==usuario,Usuario.senha==senhahash).all()
        if (len(linha)>0): #"Anota" na sessão que o usuário está autenticado
            session['autenticado'] = True
            session['usuario'] = linha[0].id
            flash(u'Usuário autenticado com sucesso!')
            resp = make_response(redirect(url_for('root')))
            if 'contador' in request.cookies:
                contador = int(request.cookies['contador'])
                contador = contador + 1
            else:
                contador = 1
            resp.set_cookie('contador',str(contador))
            return(resp)
        else: #Usuário e senha não conferem
            flash(u'Usuário e/ou senha não conferem!')
            resposta = make_response(redirect(url_for('login')))
            if 'contador2' in request.cookies:
                contador2 = int(request.cookies['contador2'])
                contador2 = contador2 + 1
            else:
                contador2 = 1
            resposta.set_cookie('contador2',str(contador2)) 
            return(resposta)
    return (render_template('form.html',form=form,action=url_for('login')))

@app.route('/usuario/logout',methods=['POST','GET'])
def logout():
    session.clear()
    return(redirect(url_for('login')))

'''
rotas com JSON
'''

@app.route('/chamado/listar/json')
def listar_chamados_json():
    chamados = Chamado.query.order_by(Chamado.data_abertura).all()
    resultado = json.dumps([ row.asdict() for row in chamados ])
    return(resultado)

@app.route('/chamado/situacao/<nome>')
def chamado_situacao(id):
    chamado = Chamado.query.filter(Chamado.id_chamado==id).first()
    if chamado is not None:
        if chamado.data_fechamento:
            # chamado = Chamado.query.filter(Chamado.id_chamado==id).first()
            resultado = json_response(situacao="NÃO SOLUCIONADO", solicitante=chamado.solicitante)
        else:
            resultado = json_response(situacao="SOLUCIONADO")
    else:
        resultado = json_response(situacao="CHAMADO INEXISTENTE")

    return(resultado)

# @app.route('/chave/teste')
# def chave_teste():
#     #return(json_response(aplicacao="Flask",versao="2.0",data="28/09/2021"))
#     chaves = Chave.query.order_by(Chave.nome).all()
#     lista_chaves = []
#     for chave in chaves:
#         linha = {"nome": chave.nome, "disponivel": chave.disponivel}
#         lista_chaves.append(linha)
#     resultado = json.dumps([linha for linha in lista_chaves])
#     return(resultado)

if __name__ == "__main__":
    serve(app, host='0.0.0.0', port=80, url_prefix='/app')
