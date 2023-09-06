from fakepinterest import database, app
from fakepinterest.models import Usuario, Post

with app.app_context(): #pegando o contexto do app e criando o banco de dados dentro dele
    database.create_all()