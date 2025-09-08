
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from ..forms import NewsForm, GalleryForm
from ..models import News, GalleryItem, Project, ProjectImage, User
from .. import db
from werkzeug.utils import secure_filename
from PIL import Image
import os
from datetime import datetime

admin_bp = Blueprint("admin", __name__, template_folder="../../templates/admin")

def role_required(roles):
    def decorator(func):
        from functools import wraps
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated or current_user.role not in roles:
                flash("No tienes permisos para acceder aquí.", "danger")
                return redirect(url_for("public.home"))
            return func(*args, **kwargs)
        return wrapper
    return decorator

def save_file(storage, subdir=""):
    if not storage:
        return None
    filename = secure_filename(storage.filename)
    base = current_app.config["UPLOAD_FOLDER"]
    folder = os.path.join(base, subdir) if subdir else base
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, filename)
    storage.save(path)
    return os.path.relpath(path, base)

def process_image(file_storage, subdir="galeria", max_size=(1600, 1200), quality=85):
    rel = save_file(file_storage, subdir)
    base = current_app.config["UPLOAD_FOLDER"]
    full = os.path.join(base, rel)
    try:
        im = Image.open(full)
        if im.mode in ("RGBA","P"):
            im = im.convert("RGB")
        im.thumbnail(max_size)
        im.save(full, format="JPEG", quality=quality, optimize=True)
    except Exception as e:
        print("IMG PROCESS ERROR:", e)
    return rel

@admin_bp.route("/")
@login_required
@role_required(["admin","teacher"])
def panel():
    news = News.query.order_by(News.date.desc()).limit(10).all()
    pending_projects = Project.query.filter_by(approved=False).order_by(Project.created_at.desc()).all()
    return render_template("admin/panel.html", news=news, pending_projects=pending_projects)

@admin_bp.route("/noticias", methods=["GET","POST"])
@login_required
@role_required(["admin","teacher"])
def noticias_admin():
    form = NewsForm()
    if request.method == "POST":
        title = request.form.get("title")
        content = request.form.get("content")  # HTML de Quill
        activity_type = request.form.get("activity_type", "General")
        if title and content:
            n = News(title=title, content=content, activity_type=activity_type, author_id=current_user.id, date=datetime.utcnow().date())
            db.session.add(n)
            db.session.commit()
            flash("Noticia guardada", "success")
            return redirect(url_for("admin.noticias_admin"))
        else:
            flash("Completa título y contenido", "warning")
    news = News.query.order_by(News.date.desc()).all()
    return render_template("admin/noticias.html", form=form, news=news)

@admin_bp.route("/noticias/<int:news_id>/eliminar", methods=["POST"])
@login_required
@role_required(["admin","teacher"])
def eliminar_noticia(news_id):
    n = News.query.get_or_404(news_id)
    db.session.delete(n)
    db.session.commit()
    flash("Noticia eliminada", "info")
    return redirect(url_for("admin.noticias_admin"))

@admin_bp.route("/galeria", methods=["GET","POST"])
@login_required
@role_required(["admin","teacher"])
def galeria_admin():
    form = GalleryForm()
    if form.validate_on_submit() and form.image.data:
        rel = process_image(form.image.data, "galeria")
        g = GalleryItem(filename=rel, title=form.title.data, description=form.description.data, author_id=current_user.id)
        db.session.add(g)
        db.session.commit()
        flash("Imagen subida a la galería", "success")
        return redirect(url_for("admin.galeria_admin"))
    items = GalleryItem.query.order_by(GalleryItem.date.desc()).all()
    return render_template("admin/galeria.html", form=form, items=items)

@admin_bp.route("/galeria/<int:item_id>/eliminar", methods=["POST"])
@login_required
@role_required(["admin","teacher"])
def eliminar_galeria(item_id):
    g = GalleryItem.query.get_or_404(item_id)
    db.session.delete(g)
    db.session.commit()
    flash("Elemento eliminado", "info")
    return redirect(url_for("admin.galeria_admin"))

@admin_bp.route("/proyectos/<int:project_id>/aprobar", methods=["POST"])
@login_required
@role_required(["admin","teacher"])
def aprobar_proyecto(project_id):
    p = Project.query.get_or_404(project_id)
    p.approved = True
    img = ProjectImage.query.filter_by(project_id=p.id).first()
    if img:
        g = GalleryItem(filename=img.filename, title=p.title, description=p.description, author_id=p.student_id)
        db.session.add(g)
    db.session.commit()
    flash("Proyecto aprobado y publicado en la galería", "success")
    return redirect(url_for("admin.panel"))

@admin_bp.route("/proyectos/<int:project_id>/rechazar", methods=["POST"])
@login_required
@role_required(["admin","teacher"])
def rechazar_proyecto(project_id):
    p = Project.query.get_or_404(project_id)
    p.approved = False
    db.session.commit()
    flash("Proyecto marcado como no aprobado", "info")
    return redirect(url_for("admin.panel"))

@admin_bp.route("/usuarios", methods=["GET","POST"])
@login_required
@role_required(["admin"])
def usuarios_admin():
    if request.method == "POST":
        action = request.form.get("action")
        if action == "create":
            name = request.form.get("name","").strip()
            email = request.form.get("email","").strip().lower()
            role = request.form.get("role","teacher")
            password = request.form.get("password","")
            if not (name and email and password):
                flash("Completa nombre, email y contraseña.", "warning")
            else:
                if User.query.filter_by(email=email).first():
                    flash("Ese correo ya existe.", "warning")
                else:
                    u = User(name=name, email=email, role=role)
                    u.set_password(password)
                    db.session.add(u)
                    db.session.commit()
                    flash("Usuario creado.", "success")
        elif action == "changerole":
            user_id = request.form.get("user_id")
            new_role = request.form.get("new_role")
            u = User.query.get(int(user_id))
            if u:
                u.role = new_role
                db.session.commit()
                flash("Rol actualizado.", "success")
        return redirect(url_for("admin.usuarios_admin"))
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template("admin/usuarios.html", users=users)
