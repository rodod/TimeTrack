import click
from flask import Flask

from config import Config
from extensions import db, login_manager, csrf
from models import User


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    from blueprints.auth import bp as auth_bp
    from blueprints.core import bp as core_bp
    from blueprints.employee import bp as employee_bp
    from blueprints.admin import bp as admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(core_bp)
    app.register_blueprint(employee_bp)
    app.register_blueprint(admin_bp)

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    @app.errorhandler(403)
    def forbidden(e):
        return "Accesso negato: non hai i permessi per questa pagina.", 403

    with app.app_context():
        db.create_all()

    register_cli(app)
    return app


def register_cli(app):
    @app.cli.command("create-admin")
    @click.option("--username", prompt=True)
    @click.option("--full-name", prompt="Nome e cognome")
    @click.option("--password", prompt=True, hide_input=True, confirmation_prompt=True)
    def create_admin(username, full_name, password):
        """Crea il primo utente amministratore: flask create-admin"""
        if User.query.filter_by(username=username).first():
            click.echo("Errore: nome utente già esistente.")
            return
        user = User(username=username, full_name=full_name, role="admin", active=True)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        click.echo(f"Amministratore '{username}' creato con successo.")


app = create_app()

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
