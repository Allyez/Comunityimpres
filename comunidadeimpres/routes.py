from comunidadeimpres.forms import Login, CriarConta, EditarPerfil, CriarPost
from flask import render_template, redirect, url_for, flash, request, abort
from comunidadeimpres import app, database, bcrypt
from comunidadeimpres.models import Usuario, Post
from flask_login import login_user, logout_user, current_user, login_required
import secrets
import os
from PIL import Image

@app.route("/")
def homepage():
    posts = Post.query.order_by(Post.id.desc())
    return render_template("homepage.html", posts=posts)

@app.route("/contato")
@login_required
def contato():
    return render_template("contato.html")

@app.route("/usuarios")
@login_required
def usuarios():
    lista_usuarios = Usuario.query.all()
    return render_template("usuarios.html", lista_usuarios=lista_usuarios)

@app.route("/login", methods=['GET', 'POST'])
def login():
    form_login = Login()
    form_criarconta = CriarConta()
    if form_login.validate_on_submit() and 'botao' in request.form:
        usuario = Usuario.query.filter_by(email=form_login.email.data).first()
        if usuario and bcrypt.check_password_hash(usuario.senha, form_login.senha.data):
            login_user(usuario, remember=form_login.lembrar_dados.data)
            flash(f'Succesfully login: {form_login.email.data}', 'alert alert-success')
            param_next = request.args.get('next')
            if param_next:
                return redirect(param_next)
            else:
                return redirect(url_for('homepage'))
        else:
            flash('Falha no login. E-mail ou senha inválido.', 'alert alert-danger')
    if form_criarconta.validate_on_submit() and 'botao_criarconta' in request.form:
        senha_cripto = bcrypt.generate_password_hash(form_criarconta.senha.data)
        usuario = Usuario(username=form_criarconta.username.data,
                          email=form_criarconta.email.data,
                          senha=senha_cripto)
        database.session.add(usuario)
        database.session.commit()
        login_user(usuario)
        flash('Account create sucessfully', 'alert alert-success')
        return redirect(url_for('homepage'))
    return render_template("login.html", form_login=form_login, form_criarconta=form_criarconta)

@app.route("/post/criar", methods=['GET', 'POST'])
@login_required
def criar_post():
    form_criarpost = CriarPost()
    if form_criarpost.validate_on_submit():
        post = Post(titulo=form_criarpost.titulo.data,
                    corpo=form_criarpost.corpo.data,
                    autor=current_user)
        database.session.add(post)
        database.session.commit()
        flash('Post criado', 'alert-success')
        return redirect(url_for('homepage'))
    return render_template('criar_post.html', form=form_criarpost)

@app.route("/perfil")
@login_required
def perfil():
    foto_perfil = url_for('static', filename='fotos_perfil/{}'.format(current_user.foto_perfil))
    return render_template('perfil.html', foto_perfil=foto_perfil)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logout sucessfully", 'alert-success')
    return redirect(url_for('homepage'))

def salvar_imagem(imagem):
    codigo = secrets.token_hex(8)
    nome, extensao = os.path.splitext(imagem.filename)
    nome_arquivo = nome + codigo + extensao
    caminho_completo = os.path.join(app.root_path, 'static/fotos_perfil', nome_arquivo)
    tamanho = (200, 200)
    imagem_reduzida = Image.open(imagem)
    imagem_reduzida.thumbnail(tamanho)
    imagem_reduzida.save(caminho_completo)
    return nome_arquivo

def atualizar_cursos(form):
    lista_cursos = []
    for campo in form:
        if 'curso_' in campo.name:
            if campo.data:
                lista_cursos.append(campo.label.text)
    return ';'.join(lista_cursos)


@app.route("/editar_perfil", methods=['GET', 'POST'])
@login_required
def editar_perfil():
    form_editarperfil = EditarPerfil()
    if form_editarperfil.validate_on_submit():
        current_user.email = form_editarperfil.email.data
        current_user.username = form_editarperfil.username.data
        if form_editarperfil.foto_perfil.data:
            nome_imagem = salvar_imagem(form_editarperfil.foto_perfil.data)
            current_user.foto_perfil = nome_imagem
        current_user.cursos = atualizar_cursos(form_editarperfil)
        database.session.commit()
        flash('Alterações de perfil atualizadas', 'alert-success')
        return redirect(url_for('perfil'))
    elif request.method == 'GET':
        form_editarperfil.email.data = current_user.email
        form_editarperfil.username.data = current_user.username
        for campo in form_editarperfil:
            if campo.label.text in current_user.cursos.split(';'):
                campo.data = True
    foto_perfil = url_for('static', filename='fotos_perfil/{}'.format(current_user.foto_perfil))
    return render_template('editar_perfil.html', foto_perfil=foto_perfil, form=form_editarperfil)


@app.route('/post/<post_id>', methods=['GET', 'POST'])
@login_required
def exibir_post(post_id):
    post = Post.query.get(post_id)
    if current_user == post.autor:
        form = CriarPost()
        if request.method == 'GET':
            form.titulo.data = post.titulo
            form.corpo.data = post.corpo
        elif form.validate_on_submit():
            post.titulo = form.titulo.data
            post.corpo = form.corpo.data
            database.session.commit()
            flash('Alterações de post realizadas', 'alert-success')
            return redirect(url_for('homepage'))
    else:
        form = None
    return render_template('exibir_post.html', post=post, form=form)


@app.route('/post/<post_id>/excluir', methods=['GET', 'POST'])
@login_required
def excluir_post(post_id):
    post = Post.query.get(post_id)
    if current_user == post.autor:
        database.session.delete(post)
        database.session.commit()
        flash('Seu post foi excluído', 'alert-danger')
        return redirect(url_for('homepage'))
    else:
        abort(403)
