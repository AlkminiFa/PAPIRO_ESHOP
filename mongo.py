import pymongo
from pymongo import MongoClient

cluster = MongoClient("mongodb+srv://papiroEshop:1234@papiro.o5pgjqg.mongodb.net/?retryWrites=true&w=majority&appName=Papiro")
db = cluster["Papiro"]
collection = db["Products"]


post = {
    "name": "Paper A4",
    "description": "Χαρτί τύπου Α4"
} 

collection.insert_one(post)

collection.create_index({"name" : 1})