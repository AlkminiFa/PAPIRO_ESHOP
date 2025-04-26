import pymongo, gridfs
from pymongo import MongoClient

cluster = MongoClient("mongodb+srv://papiroEshop:1234@papiro.o5pgjqg.mongodb.net/?retryWrites=true&w=majority&appName=Papiro")
db = cluster["Papiro"]
collection = db["Products"]

fs = gridfs.GridFS(db)

# Upload an image to GridFS
with open("A4.png", "rb") as image_file:
    image_id = fs.put(image_file, filename="A4.png")
                      
post0 = { "name": "Paper A4",
        "image": image_id,
        "description": "Χαρτί μεγέθους Α4",
        "likes": 0,
        "price": 3.5
        }
with open("alcohol_markers.png", "rb") as image_file:
    image_id = fs.put(image_file, filename="alcohol_markers.png")
                      
post1 = { "name": "Alcohol Markers",
        "image": image_id,
        "description": "Μαρκαδόροι ζωγραφικής διπλής όψης",
        "likes": 0,
        "price": 5
        }
with open("blue_backpack.png", "rb") as image_file:
    image_id = fs.put(image_file, filename="blue_backpack.png")
                      
post2 = { "name": "Blue Backpack",
        "image": image_id,
        "description": "Μπλε σακίδιο πλάτης",
        "likes": 0,
        "price": 20
        }





collection.insert_one(post0)
    

collection.create_index({"name" : 1})