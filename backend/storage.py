import json
import uuid
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "library.json"

def load_db():
    if not DB_PATH.exists():
        return {}
    with DB_PATH.open("r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def save_db(db):
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with DB_PATH.open("w", encoding="utf-8") as f:
        json.dump(db, f, indent=2, ensure_ascii=False)

def create_item(name, pub_date, author, category):
    db = load_db()
    item_id = str(uuid.uuid4())
    item = {
        "id": item_id,
        "name": name,
        "publication_date": pub_date,
        "author": author,
        "category": category
    }
    db[item_id] = item
    save_db(db)
    return item

def get_all():
    return list(load_db().values())

def get_by_id(item_id):
    return load_db().get(item_id)

def delete_item(item_id):
    db = load_db()
    if item_id in db:
        del db[item_id]
        save_db(db)
        return True
    return False

def find_by_name_exact(name):
    return [i for i in load_db().values() if i.get("name") == name]

def filter_by_category(category):
    return [i for i in load_db().values() if i.get("category") == category]
