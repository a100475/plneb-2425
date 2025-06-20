from flask import Flask

from routes.home import home_bp
from routes.add import add_bp
from routes.edit import edit_bp
from routes.remove import remove_bp
from routes.details import details_bp
from routes.table import table_bp
from routes.stats import stats_bp

app = Flask(__name__)
app.secret_key = 'pln_secret_key' # Chave secreta para sessões e mensagens flash

app.register_blueprint(home_bp)
app.register_blueprint(add_bp)
app.register_blueprint(edit_bp)
app.register_blueprint(remove_bp)
app.register_blueprint(details_bp)
app.register_blueprint(table_bp)
app.register_blueprint(stats_bp)


if __name__ == '__main__':
    app.run(host="localhost", port=4000, debug=True)