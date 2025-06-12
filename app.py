from flask import Flask
from flask_mysqldb import MySQL
from routes.home import home_bp

# inicialização
app = Flask(__name__)
app.secret_key = 'corolla_prata'

# configuração do MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '141191'
app.config['MYSQL_DB'] = 'carwash'

mysql = MySQL(app)

home_bp.mysql = mysql
app.mysql = mysql
app.register_blueprint(home_bp)

# execução
if __name__ == '__main__':
    app.run(debug=True)