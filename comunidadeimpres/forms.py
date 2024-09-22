from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import SubmitField, StringField, PasswordField, BooleanField, TextAreaField
from wtforms.validators import Length, DataRequired, EqualTo, Email, ValidationError
from comunidadeimpres.models import Usuario
from flask_login import current_user

class Login(FlaskForm):
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    senha = PasswordField('Senha', validators=[DataRequired(), Length(6, 18)])
    lembrar_dados = BooleanField('Lembrar dados de acesso')
    botao = SubmitField("Confirmar")


class CriarConta(FlaskForm):
    username = StringField('Nome', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    senha = PasswordField("Senha", validators=[DataRequired(), Length(6, 18)])
    confirmar_senha = PasswordField('Confirmar senha', validators=[DataRequired(), EqualTo('senha')])
    botao_criarconta = SubmitField('Criar conta')

    def validate_email(self, email):
        usuario = Usuario.query.filter_by(email=email.data).first()
        if usuario:
            raise ValidationError("Este e-mail já existe. Cadastre-se com outro e-mail ou faça login")


class EditarPerfil(FlaskForm):
    username = StringField('Nome do Usuário', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    foto_perfil = FileField('Foto de perfil', validators=[FileAllowed(['jpg', 'png'])])
    curso_python = BooleanField('Curso de Python')
    curso_PPT = BooleanField('Curso de PowerPoint')
    curso_excel = BooleanField('Curso de Excel')
    curso_Javascript = BooleanField('Curso de Javascript')
    curso_sql = BooleanField('Curso de SQL')
    curso_word = BooleanField('Curso de Word')
    curso_html = BooleanField('Curso de HTML e CSS')

    botao_confirmaredicao = SubmitField('Confirmar edição')

    def validate_email(self, email):
        if current_user.email != email.data:
            usuario = Usuario.query.filter_by(email=email.data).first()
            if usuario:
                return ValidationError('E-mail já cadastrado. Cadastre outro e-mail ou faça login')


class CriarPost(FlaskForm):
    titulo = StringField('Título do Post', validators=[DataRequired(), Length(2, 100)])
    corpo = TextAreaField('Escreva seu Post', validators=[DataRequired()])
    botao_submit = SubmitField('Criar Post')
