from flask import Blueprint, redirect, url_for
from flask_login import login_required, current_user

bp = Blueprint("core", __name__)


@bp.route("/")
@login_required
def dashboard():
    if current_user.is_admin:
        return redirect(url_for("admin.dashboard"))
    return redirect(url_for("employee.dashboard"))
