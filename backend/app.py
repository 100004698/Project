from flask import Flask, jsonify, request
# Use a direct import so the module can be run as a script
from storage import create_item, get_all, get_by_id, delete_item, find_by_name_exact, filter_by_category

app = Flask(__name__)

@app.route("/media", methods=["GET"])
def list_media():
    category = request.args.get("category")
    if category:
        items = filter_by_category(category)
    else:
        items = get_all()
    return jsonify(items), 200

@app.route("/media/search", methods=["GET"])
def search_media():
    name = request.args.get("name")
    if not name:
        return jsonify({"error": "name query param required"}), 400
    items = find_by_name_exact(name)
    return jsonify(items), 200

@app.route("/media/<item_id>", methods=["GET"])
def get_media(item_id):
    item = get_by_id(item_id)
    if not item:
        return jsonify({"error": "not found"}), 404
    return jsonify(item), 200

@app.route("/media", methods=["POST"])
def create_media():
    try:
        data = request.get_json()
        required = ("name", "publication_date", "author", "category")
        if not data or not all(k in data for k in required):
            return jsonify({"error": "Missing required fields: name, publication_date, author, category"}), 400
        
        # Call create_item which will validate
        item = create_item(data["name"], data["publication_date"], data["author"], data["category"])
        return jsonify(item), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

@app.route("/media/<item_id>", methods=["DELETE"])
def delete_media(item_id):
    try:
        if delete_item(item_id):
            return jsonify({"deleted": item_id}), 200
        else:
            return jsonify({"error": "Item not found"}), 404
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(port=5000, debug=True)
