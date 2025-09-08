
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from ..forms import ProjectForm
from ..models import Project, ProjectImage
from .. import db
import os
from werkzeug.utils import secure_filename
from PIL import Image

intranet_bp = Blueprint("intranet", __name__)

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

def compress_and_save(image_storage, dest_subdir):
    rel = save_file(image_storage, dest_subdir)
    base = current_app.config["UPLOAD_FOLDER"]
    full = os.path.join(base, rel)
    try:
        img = Image.open(full)
        if img.mode in ("RGBA","P"):
            img = img.convert("RGB")
        img.thumbnail((1600, 1200))
        img.save(full, format="JPEG", quality=85, optimize=True)
    except Exception as e:
        print("Compress error:", e)
    return rel

@intranet_bp.route("/", methods=["GET","POST"])
@login_required
def dashboard():
    form = ProjectForm()
    my_projects = Project.query.filter_by(student_id=current_user.id).order_by(Project.created_at.desc()).all()
    if form.validate_on_submit():
        p = Project(
            student_id=current_user.id,
            title=form.title.data,
            course=form.course.data,
            year=form.year.data,
            description=form.description.data,
            video_url=form.video_url.data or None
        )
        if form.evidence_pdf.data:
            rel = save_file(form.evidence_pdf.data, "pdf")
            p.evidence_pdf = rel
        db.session.add(p)
        db.session.commit()

        files = request.files.getlist("images")[:8]
        for file in files:
            if file.filename.strip():
                rel_img = compress_and_save(file, "images")
                db.session.add(ProjectImage(project_id=p.id, filename=rel_img))
        db.session.commit()

        flash("Proyecto guardado. Queda pendiente de revisión por un profesor.", "success")
        return redirect(url_for("intranet.dashboard"))
    return render_template("intranet/dashboard.html", form=form, projects=my_projects)

@intranet_bp.route("/mis-proyectos")
@login_required
def mis_proyectos():
    my_projects = Project.query.filter_by(student_id=current_user.id).order_by(Project.created_at.desc()).all()
    return render_template("intranet/mis_proyectos.html", projects=my_projects)
