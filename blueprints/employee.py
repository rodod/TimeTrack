from datetime import date, timedelta

from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, current_app
from flask_login import login_required, current_user

from extensions import db
from models import Project, TimeEntry
from forms import TimeEntryForm

bp = Blueprint("employee", __name__, url_prefix="/me")


def _project_choices():
    projects = Project.query.filter_by(active=True).order_by(Project.name).all()
    return [(p.id, p.name) for p in projects]


def _editable_bounds():
    """Intervallo di date che il dipendente può modificare autonomamente."""
    today = date.today()
    horizon = current_app.config["PLANNING_HORIZON_DAYS"]
    grace = current_app.config["EDIT_GRACE_DAYS"]
    return today - timedelta(days=grace), today + timedelta(days=horizon)


@bp.route("/")
@login_required
def dashboard():
    today = date.today()
    start_of_week = today - timedelta(days=today.weekday())
    # Mostra dalla settimana corrente fino all'orizzonte di pianificazione
    min_date, max_date = _editable_bounds()

    entries = (
        TimeEntry.query.filter_by(user_id=current_user.id)
        .filter(TimeEntry.work_date >= start_of_week)
        .order_by(TimeEntry.work_date.asc())
        .all()
    )

    # Raggruppa per settimana per rendere la vista "rolling" più leggibile
    weeks = {}
    for e in entries:
        wk_start = e.work_date - timedelta(days=e.work_date.weekday())
        weeks.setdefault(wk_start, []).append(e)

    total_hours = sum(e.hours for e in entries)

    return render_template(
        "employee/dashboard.html",
        weeks=sorted(weeks.items()),
        total_hours=total_hours,
        min_date=min_date,
        max_date=max_date,
    )


@bp.route("/new", methods=["GET", "POST"])
@login_required
def new_entry():
    form = TimeEntryForm()
    form.project_id.choices = _project_choices()
    min_date, max_date = _editable_bounds()

    if not form.project_id.choices:
        flash("Non ci sono progetti attivi. Contatta un amministratore.", "warning")

    if form.validate_on_submit():
        if not (min_date <= form.work_date.data <= max_date):
            flash(
                f"Puoi pianificare solo tra {min_date.strftime('%d/%m/%Y')} "
                f"e {max_date.strftime('%d/%m/%Y')}.", "danger"
            )
        else:
            existing = TimeEntry.query.filter_by(
                user_id=current_user.id,
                project_id=form.project_id.data,
                work_date=form.work_date.data,
            ).first()
            if existing:
                flash("Esiste già una voce per questa data e questo progetto: modificala invece di duplicarla.", "warning")
            else:
                entry = TimeEntry(
                    user_id=current_user.id,
                    project_id=form.project_id.data,
                    work_date=form.work_date.data,
                    hours=form.hours.data,
                    notes=form.notes.data,
                    status="pianificato",
                )
                db.session.add(entry)
                db.session.commit()
                flash("Voce di orario salvata.", "success")
                return redirect(url_for("employee.dashboard"))

    return render_template("employee/entry_form.html", form=form, min_date=min_date, max_date=max_date)


@bp.route("/<int:entry_id>/edit", methods=["GET", "POST"])
@login_required
def edit_entry(entry_id):
    entry = TimeEntry.query.get_or_404(entry_id)
    # Sicurezza: un dipendente può modificare solo le PROPRIE voci
    if entry.user_id != current_user.id:
        abort(403)
    if entry.status == "confermato":
        flash("Questa voce è già stata confermata dall'amministratore e non è più modificabile.", "warning")
        return redirect(url_for("employee.dashboard"))

    form = TimeEntryForm(obj=entry)
    form.project_id.choices = _project_choices()
    min_date, max_date = _editable_bounds()

    if form.validate_on_submit():
        if not (min_date <= form.work_date.data <= max_date):
            flash(
                f"Puoi pianificare solo tra {min_date.strftime('%d/%m/%Y')} "
                f"e {max_date.strftime('%d/%m/%Y')}.", "danger"
            )
        else:
            entry.work_date = form.work_date.data
            entry.project_id = form.project_id.data
            entry.hours = form.hours.data
            entry.notes = form.notes.data
            db.session.commit()
            flash("Voce aggiornata.", "success")
            return redirect(url_for("employee.dashboard"))

    return render_template("employee/entry_form.html", form=form, min_date=min_date, max_date=max_date, editing=True)


@bp.route("/<int:entry_id>/delete", methods=["POST"])
@login_required
def delete_entry(entry_id):
    entry = TimeEntry.query.get_or_404(entry_id)
    if entry.user_id != current_user.id:
        abort(403)
    if entry.status == "confermato":
        flash("Non puoi eliminare una voce già confermata.", "warning")
        return redirect(url_for("employee.dashboard"))

    db.session.delete(entry)
    db.session.commit()
    flash("Voce eliminata.", "info")
    return redirect(url_for("employee.dashboard"))
