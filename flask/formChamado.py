from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField,PasswordField,SelectField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired

class ChamadoForm(FlaskForm):
    solicitante = StringField('Nome de quem solicita o atendimento: ', validators=[DataRequired()])
    sertorChamado = StringField('Setor de quem solicita o atendimento: ', validators=[DataRequired()])
    enviar = SubmitField('CADASTRAR CHAMADO')