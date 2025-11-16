# extensions.py
# Este arquivo vai "guardar" a instância do DB
# para que app.py e models.py possam importá-la
# sem criar um círculo.

from flask_sqlalchemy import SQLAlchemy

# Crie a instância do 'db' aqui, sem nenhuma configuração
db = SQLAlchemy()