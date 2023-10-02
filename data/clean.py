import csv
from bson import ObjectId
import bcrypt

from pymongo import MongoClient

def user_doc(row):
    hashed_password = row['password'].strip("b'").strip("'")
    document = {
        "_id": ObjectId(),
        "userId": row['userId'],
        "username": row["userName"],
        "password": hashed_password,
        "preferences": row['preferences'].strip("[]").replace("'", "").split(", ")
        # Add more fields as needed
    }
    return document

def users_csv(csv_file_path):
    users = []
    with open(csv_file_path, "r") as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for _, row in enumerate(csv_reader):
            document = user_doc(row)
            users.append(document)
                # print(document)
            # collection.insert_one(document)
    return users

def product_doc(row):
    doc = {
        "_id": ObjectId(),
        "productId": row['productId'],
        "productName": row['productName'],
        "category": row['category'],
        "description": row['description'],
        "rating": int(row['rating']),
        "popularity": int(row['popularity'])
    }
    return doc

def products_csv(csv_file_path):
    users = []
    with open(csv_file_path, "r") as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            document = product_doc(row)
            users.append(document)
    return users

def inter_doc(row, users, z):
    x = ''
    for user in users: 
        if user['userId'] == row['userId']:
            x = user['_id']
            break
    # print(x)
    y = ''
    for pro in z:
        # print(pro['_id'])
        if pro['productId'] == row['productId']:
            y = pro['_id']
            break

    doc = {
        'userId': x,
        'productId': y,
        'score': int(row['score'])
    }
    return doc

def inter_csv(x, users, products):
    inter = []
    with open(x, "r") as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for _, row in enumerate(csv_reader):
            # if (_ < 5):
            document = inter_doc(row, users, products)
            inter.append(document)
    return inter


users = users_csv('users.csv')
products = products_csv('products.csv')
interactions = inter_csv('interactions.csv', users, products)

def remove(data, keys_to_remove):
    for item in data:
        for key in keys_to_remove:
            if key in item:
                del item[key]

remove(users, ['userId'])
remove(products, ['productId'])


# Write the list of dictionaries to a JSON file
import json
def saveJSON(data, path):
    for item in data:
        item["_id"] = {"$oid":str(item["_id"])}

    with open(path, "w") as json_file:
        json.dump(data, json_file, indent=4)

def saveJSONINT(data, path):
    for item in data:
        item["productId"] = {"$oid":str(item["productId"])}
        item["userId"] = {"$oid":str(item["userId"])}

    with open(path, "w") as json_file:
        json.dump(data, json_file, indent=4)

saveJSON(users, 'users.json')
saveJSON(products, 'products.json')
saveJSONINT(interactions, 'interactions.json')

# # MongoDB Atlas connection settings
# mongo_uri = "mongodb+srv://admin:passWORD@cluster0.4iif9cc.mongodb.net/?retryWrites=true&w=majority"

# # Establish MongoDB Atlas connection
# client = MongoClient(mongo_uri)
# db = client.get_database('data')  # Use the default database or specify the database name

# print('MongoConnected')

# def toMongo(data, collection_name):
#     collection = db[collection_name]
#     for x in data:
#         collection.insert_one(x)
#     print('Completed', users, sep=' ')

# toMongo(users, 'users')
# toMongo(products, 'products')
# toMongo(interactions, 'interactions')
