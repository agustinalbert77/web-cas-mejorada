
# Portal CAS IB (Flask) — v2

Incluye: público, noticias con **Quill (HTML)**, galería con **compresión de imágenes**, intranet de alumnos, panel profesor/admin, **gestor de usuarios (admin)**, **reCAPTCHA v2** en registro/contacto y **banner de cookies**.

## Local
```bash
python -m venv .venv
.venv\Scripts\activate   # Windows
# source .venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
# (Opcional) Copia .env.example a .env y rellena SMTP + reCAPTCHA

# Ejecutar
python - << "PY"
from wsgi import app
if __name__ == '__main__':
    app.run(debug=True)
PY
```

Admin por defecto:
- Email: admin@dsls.cl
- Pass: admin123  (¡cámbiala!)

## Render (deploy)
- Build: `pip install -r requirements.txt`
- Start: `gunicorn wsgi:app`
- Variables: `SECRET_KEY`, `DATABASE_URL` (si usas Postgres), `MAIL_*`, `RECAPTCHA_*`

## Gmail App Password
1) Activa 2FA, crea App Password tipo “Mail”  
2) Usa `MAIL_USERNAME` y `MAIL_PASSWORD` (app password).

## reCAPTCHA v2
- Crea llaves en https://www.google.com/recaptcha/admin (tipo “Checkbox”)
- Añade `RECAPTCHA_PUBLIC_KEY`, `RECAPTCHA_PRIVATE_KEY`.

## Límite y compresión de imágenes
- Máximo **8** imágenes por proyecto (en backend y UI).
- Compresión a ~1600x1200, JPG calidad ~85.

## Gestión de usuarios (solo admin)
- `/admin/usuarios`: crear usuario, cambiar rol.

## Backups (SQLite)
```bash
python tools/db_backup.py dump backups/dump.json
python tools/db_backup.py load backups/dump.json
```
