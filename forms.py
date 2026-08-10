from flask_wtf import FlaskForm
from wtforms import (
    StringField, PasswordField, SelectField, FloatField, DateField,
    TextAreaField, BooleanField, SubmitField
)
from wtforms.validators import DataRequired, Length, Optional, NumberRange, Email, EqualTo


class LoginForm(FlaskForm):
    username = StringField("Nome utente", validators=[DataRequired(), Length(max=64)])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Accedi")


class TimeEntryForm(FlaskForm):
    work_date = DateField("Data", validators=[DataRequired()])
    project_id = SelectField("Progetto", coerce=int, validators=[DataRequired()])
    hours = FloatField("Ore", validators=[DataRequired(), NumberRange(min=0.25, max=24)])
    notes = TextAreaField("Note", validators=[Optional(), Length(max=255)])
    submit = SubmitField("Salva")


class UserForm(FlaskForm):
    username = StringField("Nome utente", validators=[DataRequired(), Length(max=64)])
    full_name = StringField("Nome e cognome", validators=[DataRequired(), Length(max=128)])
    email = StringField("Email", validators=[Optional(), Email(), Length(max=120)])
    password = PasswordField(
        "Password (lascia vuoto per non cambiarla)",
        validators=[Optional(), Length(min=6, message="Almeno 6 caratteri")]
    )
    role = SelectField("Ruolo", choices=[("employee", "Dipendente"), ("admin", "Amministratore")])
    active = BooleanField("Attivo", default=True)
    submit = SubmitField("Salva")


class ProjectForm(FlaskForm):
    name = StringField("Nome progetto", validators=[DataRequired(), Length(max=128)])
    description = StringField("Descrizione", validators=[Optional(), Length(max=255)])
    active = BooleanField("Attivo", default=True)
    submit = SubmitField("Salva")
