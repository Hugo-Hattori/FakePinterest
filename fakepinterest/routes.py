# criar as rotas do nosso site (os links)
from flask import render_template, url_for, redirect
from fakepinterest import app, bcrypt, database
from flask_login import login_required, login_user, logout_user, current_user
from fakepinterest.forms import FormLogin, FormCriarConta, FormFoto
from fakepinterest.models import Usuario, Post
import os
from werkzeug.utils import secure_filename


@app.route("/", methods=["GET", "POST"])
def homepage():
    form_login = FormLogin()
    if form_login.validate_on_submit():
        usuario = Usuario.query.filter_by(email=form_login.email.data).first()
        if usuario and bcrypt.check_password_hash(usuario.senha.encode("utf-8"), form_login.senha.data):
            login_user(usuario)
            return redirect(url_for("perfil", id_usuario=usuario.id))
    return render_template("homepage.html", form=form_login)


@app.route("/criar-conta", methods=["GET", "POST"])
def criarconta():
    form_criar_conta = FormCriarConta()
    if form_criar_conta.validate_on_submit(): #verifica se o usuário clicou no botão de "criar conta" se todos os campos estão válidos
        senha_criptografada = bcrypt.generate_password_hash(form_criar_conta.senha.data).decode("utf-8")
        usuario = Usuario(username = form_criar_conta.username.data,
                          senha = senha_criptografada,
                          email = form_criar_conta.email.data)
        database.session.add(usuario)
        database.session.commit()
        login_user(usuario, remember=True)
        return redirect(url_for("perfil", id_usuario=usuario.id))
    return render_template("criarconta.html", form=form_criar_conta)


@app.route("/perfil/<id_usuario>", methods=["GET", "POST"])
@login_required
def perfil(id_usuario):
    if int(id_usuario) == int(current_user.id):
        #verifica se o usuário está vendo o perfil dele mesmo
        form_foto = FormFoto()
        if form_foto.validate_on_submit():
            arquivo = form_foto.foto.data
            nome_seguro = secure_filename(arquivo.filename)
            # salvar o arquivo na pasta fotos_posts
            caminho = os.path.join(os.path.abspath(os.path.dirname(__file__)), #abspath indica o caminho onde está esse arquivo "dirname(__file__)", ou seja, o próprio arquivo routes.py
                              app.config["UPLOAD_FOLDER"], nome_seguro)
            arquivo.save(caminho)
            # registrar o arquivo no banco de dados
            foto = Post(imagem=nome_seguro, id_usuario=current_user.id)
            database.session.add(foto)
            database.session.commit()
            return redirect(url_for("perfil", id_usuario=id_usuario))
        return render_template("perfil.html", user=current_user, form=form_foto)
    else:
        #vendo perfil de outro usuário
        usuario = Usuario.query.get(int(id_usuario))
        return render_template("perfil.html", user=usuario, form=None)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("homepage"))


@app.route("/feed")
@login_required
def feed():
    fotos = Post.query.order_by(Post.data_criacao.desc()).all()[:100] #pegando todas as fotos ordenadas de forma descendente por data até 100 fotos
    return render_template("feed.html", fotos=fotos)