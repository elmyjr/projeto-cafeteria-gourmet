# extensions.py
# Este arquivo vai "guardar" a instância do DB
# para que app.py e models.py possam importá-la
# sem criar dependências circulares. (estava com bug)

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()