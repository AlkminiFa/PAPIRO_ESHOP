from flask import Flask, request, jsonify, send_file, render_template
from gridfs import GridFS
from bson import ObjectId
from io import BytesIO
from flask_pymongo import PyMongo
from flask_cors import CORS


app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://127.0.0.1:5000"}})
# MongoDB setup
import os
app.config["MONGO_URI"] = "mongodb+srv://papiroEshop:1234@papiro.o5pgjqg.mongodb.net/Papiro?retryWrites=true&w=majority&appName=Papiro"





mongo = PyMongo(app)

products_collection = mongo.db.Products
fs = GridFS(mongo.db)

# Δημιουργεί text index στο πεδίο name 
products_collection.create_index([("name", "text")])


# Helper: Convert ObjectId to string
def serialize_product(product):
    product["_id"] = str(product["_id"])
    product["image"] = str(product["image"])
    return product

# POST /products - Create new product with image upload
@app.route('/products', methods=['POST'])
def create_product():
    name = request.form.get("name")
    description = request.form.get("description")
    price = request.form.get("price")  
    image_file = request.files.get("image")

    if not all([name, description, price, image_file]):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        price = float(price)  # Ensure price is a number
    except ValueError:
        return jsonify({"error": "Price must be a number"}), 400

    image_id = fs.put(image_file, filename=image_file.filename, content_type=image_file.content_type)

    product = {
        "name": name,
        "description": description,
        "price": price,  
        "image": image_id,
        "like": 0
    }
    result = products_collection.insert_one(product)
    return jsonify({"id": str(result.inserted_id)}), 201

# GET /products/search - Search for products
@app.route('/products/search', methods=['GET'])
def search_products():
    name_query = request.args.get("name", "").strip()

    if name_query == "":
        # Empty name -> return all products
        query = {}
    else:
        # Case-insensitive regex search
        query = {"name": {"$regex": name_query, "$options": "i"}}


    # Perform the query and sort by price descending
    products = list(products_collection.find(query).sort("price", -1))
    
    # Return serialized products
    return jsonify([serialize_product(p) for p in products])

# GET /products/<id> - Get a specific product
@app.route('/products/<id>', methods=['GET'])
def get_product(id):
    product = products_collection.find_one({"_id": ObjectId(id)})
    if not product:
        return jsonify({"error": "Product not found"}), 404
    return jsonify(serialize_product(product))

# GET /products/popular-products - Get the top-5 products
@app.route('/products/popular-products', methods=['GET'])
def get_popular_products():
    top_products = list(
        products_collection.find()
        .sort("like", -1)        # Sort by likes, descending
        .limit(5)                # Limit to top 5
    )
    return jsonify([serialize_product(p) for p in top_products])


# GET /products/<id>/image - Serve product image
@app.route('/products/<id>/image', methods=['GET'])
def get_product_image(id):
    product = products_collection.find_one({"_id": ObjectId(id)})
    if not product:
        return jsonify({"error": "Product not found"}), 404
    image_file = fs.get(product["image"])
    return send_file(BytesIO(image_file.read()), mimetype=image_file.content_type)

# PATCH /products/<id>/like - Increment like count
@app.route('/products/<id>/like', methods=['PATCH'])
def like_product(id):
    result = products_collection.update_one(
        {"_id": ObjectId(id)},
        {"$inc": {"like": 1}}
    )
    if result.matched_count == 0:
        return jsonify({"error": "Product not found"}), 404
    return jsonify({"message": "Like incremented"}), 200

# DELETE /products/<id> - Delete product and image
@app.route('/products/<id>', methods=['DELETE'])
def delete_product(id):
    product = products_collection.find_one({"_id": ObjectId(id)})
    if not product:
        return jsonify({"error": "Product not found"}), 404
    fs.delete(product["image"])
    products_collection.delete_one({"_id": ObjectId(id)})
    return jsonify({"message": "Product deleted"}), 200


@app.route('/homepage')
def homepage():
    products = list(products_collection.find().sort("like", -1).limit(5))
    return render_template("homepage.html", products=[serialize_product(p) for p in products])


@app.route('/products')
def products_page():
    return render_template("products.html")

@app.route('/contact')
def contact_page():
    return render_template("contact.html")

# GET /api/products - Return all products as JSON
@app.route('/api/products', methods=['GET'])
def get_all_products():
    products = list(products_collection.find())
    return jsonify([serialize_product(p) for p in products])

from bson.errors import InvalidId

@app.route('/images/<image_id>', methods=['GET'])
def get_image_by_id(image_id):
    try:
        image_file = fs.get(ObjectId(image_id))
        # fallback τύπος σε περίπτωση που δεν έχει αποθηκευτεί MIME
        mimetype = image_file.content_type or "image/png"
        return send_file(BytesIO(image_file.read()), mimetype=mimetype)
    except InvalidId:
        return jsonify({"error": "Invalid ObjectId"}), 400
    except Exception as e:
        print(f"❌ Σφάλμα κατά την επιστροφή εικόνας: {e}")
        return jsonify({"error": str(e)}), 404

@app.route("/cart")
def cart_page():
    return render_template("cart.html")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
