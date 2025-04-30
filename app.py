from flask import Flask, request, jsonify, send_file
from gridfs import GridFS
from bson import ObjectId
from io import BytesIO
from flask_pymongo import PyMongo
from flask_cors import CORS


app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://127.0.0.1:5000"}})
# MongoDB setup
app.config["MONGO_URI"] = "mongodb+srv://papiroEshop:1234@papiro.o5pgjqg.mongodb.net/Papiro?retryWrites=true&w=majority&appName=Papiro"
mongo = PyMongo(app)

products_collection = mongo.db.Products
fs = GridFS(mongo.db)


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
    price = request.form.get("price")  # NEW: Get price
    image_file = request.files.get("image")

    if not all([name, description, price, image_file]):
        return jsonify({"error": "Missing required fields"}), 400

    try:
        price = float(price)  # Ensure price is a number
    except ValueError:
        return jsonify({"error": "Price must be a number"}), 400

    image_id = fs.put(image_file, filename=image_file.filename)
    product = {
        "name": name,
        "description": description,
        "price": price,  # NEW: Store price
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
        query = {"$text": {"$search": name_query}}


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

if __name__ == '__main__':
    app.run(debug=True)
