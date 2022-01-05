from sqlalchemy.orm import backref
from database import db
from sqlalchemy.sql import func
import datetime

class Chamado(db.Model):
    id_chamado = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer,db.ForeignKey('usuario.id'))
    solicitante = db.Column(db.String(100),unique=False,nullable=False)
    descricao = db.Column(db.String(200),unique=False,nullable=False)
    setorChamado = db.Column(db.String(20),unique=False,nullable=False)
    data_abertura = db.Column(db.DateTime,unique=False,nullable=False,default=datetime.datetime.now())
    data_fechamento = db.Column(db.DateTime,unique=False,nullable=True)