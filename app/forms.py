
from flask_wtf import FlaskForm, RecaptchaField
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField, IntegerField, FileField
from wtforms.validators import DataRequired, Email, Length, NumberRange, Optional, URL

class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Contraseña", validators=[DataRequired(), Length(min=6)])
    submit = SubmitField("Ingresar")

class RegisterForm(FlaskForm):
    name = StringField("Nombre", validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Contraseña", validators=[DataRequired(), Length(min=6)])
    recaptcha = RecaptchaField()
    submit = SubmitField("Crear cuenta")

class NewsForm(FlaskForm):
    title = StringField("Título", validators=[DataRequired()])
    content = TextAreaField("Contenido (HTML)")  # lo llena Quill antes de submit
    activity_type = SelectField("Tipo de actividad", choices=[("General","General"),("Servicio","Servicio"),("Creatividad","Creatividad"),("Acción","Acción")])
    submit = SubmitField("Guardar")

class GalleryForm(FlaskForm):
    title = StringField("Título", validators=[DataRequired()])
    description = TextAreaField("Descripción")
    image = FileField("Imagen")
    submit = SubmitField("Subir")

class ProjectForm(FlaskForm):
    title = StringField("Título del proyecto", validators=[DataRequired()])
    course = StringField("Curso", validators=[DataRequired()])
    year = IntegerField("Año", validators=[DataRequired(), NumberRange(min=2000, max=2100)])
    description = TextAreaField("Descripción", validators=[DataRequired()])
    evidence_pdf = FileField("Evidencia PDF (opcional)")
    video_url = StringField("URL de video (opcional)", validators=[Optional(), URL()])
    images = FileField("Imágenes (hasta 8, opcional)")
    submit = SubmitField("Guardar proyecto")

class ContactForm(FlaskForm):
    name = StringField("Nombre", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    message = TextAreaField("Mensaje", validators=[DataRequired(), Length(min=10)])
    recaptcha = RecaptchaField()
    submit = SubmitField("Enviar")
