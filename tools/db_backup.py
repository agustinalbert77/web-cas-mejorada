
import json, sys
from pathlib import Path
from wsgi import app
from app.models import User, News, GalleryItem, Project, ProjectImage
from app import db

def dump(path):
    data = {}
    models = [User, News, GalleryItem, Project, ProjectImage]
    with app.app_context():
        for M in models:
            name = M.__name__
            rows = M.query.all()
            data[name] = []
            for r in rows:
                item = {}
                for c in r.__table__.columns:
                    val = getattr(r, c.name)
                    try:
                        if hasattr(val, "isoformat"):
                            val = val.isoformat()
                    except Exception:
                        pass
                    item[c.name] = val
                data[name].append(item)
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("Dumped to", path)

def load(path):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    with app.app_context():
        db.drop_all()
        db.create_all()
        for name, items in data.items():
            Model = globals()[name]
            for it in items:
                obj = Model()
                for k,v in it.items():
                    setattr(obj, k, v)
                db.session.add(obj)
        db.session.commit()
    print("Loaded from", path)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python tools/db_backup.py [dump|load] path.json")
        sys.exit(1)
    cmd, path = sys.argv[1], sys.argv[2]
    if cmd == "dump":
        dump(path)
    elif cmd == "load":
        load(path)
    else:
        print("Unknown command")
