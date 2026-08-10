from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user

from extensions import db
from models import User
from forms import LoginForm

bp = Blueprint("auth", __name__)


@bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("core.dashboard"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data.strip()).first()
        if user and user.active and user.check_password(form.password.data):
            login_user(user, remember=False)
            flash(f"Benvenuto/a, {user.full_name}!", "success")
            next_page = request.args.get("next")
            return redirect(next_page or url_for("core.dashboard"))
        flash("Credenziali non valide o utente disattivato.", "danger")

    return render_template("login.html", form=form)


@bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Hai effettuato il logout.", "info")
    return redirect(url_for("auth.login"))
