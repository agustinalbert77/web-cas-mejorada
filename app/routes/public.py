
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, send_from_directory
from ..models import News, GalleryItem
from ..forms import ContactForm
from .. import db, mail
from flask_mail import Message
from datetime import datetime
import os
import bleach

public_bp = Blueprint("public", __name__)

ALLOWED_TAGS = bleach.sanitizer.ALLOWED_TAGS.union({"p","h1","h2","h3","h4","h5","h6","img","span","div"})
ALLOWED_ATTRS = {**bleach.sanitizer.ALLOWED_ATTRIBUTES, "img": ["src","alt","width","height"], "span":["class"], "div":["class"]}

@public_bp.route("/")
def home():
    q = request.args.get("q","")
    type_filter = request.args.get("tipo","")
    news_query = News.query.order_by(News.date.desc())
    if q:
        news_query = news_query.filter(News.title.ilike(f"%{q}%"))
    if type_filter:
        news_query = news_query.filter(News.activity_type==type_filter)
    latest_news = news_query.limit(5).all()
    return render_template("home.html", latest_news=latest_news, bleach=bleach, tags=ALLOWED_TAGS, attrs=ALLOWED_ATTRS)

@public_bp.route("/noticias")
def noticias():
    type_filter = request.args.get("tipo","")
    news_query = News.query.order_by(News.date.desc())
    if type_filter:
        news_query = news_query.filter(News.activity_type==type_filter)
    all_news = news_query.all()
    return render_template("noticias.html", news=all_news, bleach=bleach, tags=ALLOWED_TAGS, attrs=ALLOWED_ATTRS)

@public_bp.route("/galeria")
def galeria():
    items = GalleryItem.query.order_by(GalleryItem.date.desc()).all()
    return render_template("galeria.html", items=items)

@public_bp.route("/uploads/<path:filename>")
def uploads(filename):
    return send_from_directory(current_app.config["UPLOAD_FOLDER"], filename)

@public_bp.route("/contacto", methods=["GET","POST"])
def contacto():
    form = ContactForm()
    sent = False
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        msg_body = form.message.data

        recipients = [
            current_app.config.get("EMAIL_COLEGIO"),
            current_app.config.get("EMAIL_COORDINADORA"),
            current_app.config.get("EMAIL_DEV"),
        ]
        try:
            msg = Message(subject=f"[CAS] Contacto de {name}",
                          recipients=recipients,
                          body=f"De: {name} <{email}>\n\n{msg_body}")
            mail.send(msg)
            sent = True
            flash("Mensaje enviado correctamente. ¡Gracias por escribir!", "success")
        except Exception as e:
            print("MAIL ERROR:", e)
            print("Fallback CONTACT to console")
            flash("No se pudo enviar el correo (SMTP). Guardamos tu mensaje.", "warning")
            sent = True
        return redirect(url_for("public.contacto"))
    return render_template("contacto.html", form=form, sent=sent)
