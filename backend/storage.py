"""Database storage module for library items using JSON."""
import json
import uuid
import re
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
    """Create and store a new item with validation."""
    # Validate all inputs
    if not name or not isinstance(name, str) or not name.strip():
        raise ValueError("Name is required and must be a non-empty string")
    if not pub_date or not isinstance(pub_date, str) or not pub_date.strip():
        raise ValueError("Publication date is required")
    if not author or not isinstance(author, str) or not author.strip():
        raise ValueError("Author is required and must be a non-empty string")
    if not category or not isinstance(category, str) or not category.strip():
        raise ValueError("Category is required")
    
    # Validate date format (YYYY-MM-DD)
    if not re.match(r'^\d{4}-\d{2}-\d{2}$', pub_date.strip()):
        raise ValueError("Publication date must be in YYYY-MM-DD format")
    
    # Validate category
    valid_categories = ["Book", "Film", "Magazine"]
    if category.strip() not in valid_categories:
        raise ValueError(f"Category must be one of: {', '.join(valid_categories)}")
    
    db = load_db()
    item_id = str(uuid.uuid4())
    item = {
        "id": item_id,
        "name": name.strip(),
        "publication_date": pub_date.strip(),
        "author": author.strip(),
        "category": category.strip()
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
