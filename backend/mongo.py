import pymongo, gridfs
from pymongo import MongoClient

# Σύνδεση με το MongoDB cluster στο Atlas
cluster = MongoClient("mongodb+srv://papiroEshop:1234@papiro.o5pgjqg.mongodb.net/?retryWrites=true&w=majority&appName=Papiro")
db = cluster["Papiro"]
collection = db["Products"]

fs = gridfs.GridFS(db)

# Upload an image to GridFS

with open("whiteboard_markers.png", "rb") as image_file:
    image_id = fs.put(image_file, filename="whiteboard_markers.png")
                      
post22 = { "name": "Whiteboard markers",
        "image": image_id,
        "description": "Μαρκαδόροι για πίνακα",
        "likes": 0,
        "price": 5
        }

# Εισαγωγή του προϊόντος στη συλλογή
collection.insert_one(post22)
    
