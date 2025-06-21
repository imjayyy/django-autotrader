
from mongoengine import connect
from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017")  # update with your connection URI
db = client["AutoAuctionsHistory"]
collection = db["vin_car_record"]

from mongoengine import connect
from pymongo import MongoClient

# Connect via MongoEngine and PyMongo (needed for aggregation)
connect("AutoAuctionsHistory")  # or use host/port if needed
client = MongoClient()  # update with connection string if needed
db = client["AutoAuctionsHistory"]

# -------------------------------
# Remove duplicates from VinCarRecord
# -------------------------------
vin_car_collection = db["vin_car_record"]

pipeline = [
    {
        "$group": {
            "_id": "$vin",
            "ids": {"$push": "$_id"},
            "count": {"$sum": 1}
        }
    },
    {
        "$match": {
            "count": {"$gt": 1}
        }
    }
]

duplicates = list(vin_car_collection.aggregate(pipeline))

for doc in duplicates:
    ids_to_delete = doc["ids"][1:]  # keep first
    vin_car_collection.delete_many({"_id": {"$in": ids_to_delete}})

print(f"[VinCarRecord] Removed {sum(len(doc['ids']) - 1 for doc in duplicates)} duplicates.")

# -------------------------------
# Remove duplicates from CopartCarRecord using raw_response.vin
# -------------------------------
copart_collection = db["copart_car_record"]

# Only if raw_response contains VINs
pipeline = [
    {
        "$group": {
            "_id": "$raw_response.vin",
            "ids": {"$push": "$_id"},
            "count": {"$sum": 1}
        }
    },
    {
        "$match": {
            "_id": {"$ne": None},
            "count": {"$gt": 1}
        }
    }
]

duplicates = list(copart_collection.aggregate(pipeline))

for doc in duplicates:
    ids_to_delete = doc["ids"][1:]  # keep first
    copart_collection.delete_many({"_id": {"$in": ids_to_delete}})

print(f"[CopartCarRecord] Removed {sum(len(doc['ids']) - 1 for doc in duplicates)} duplicates.")



# Step 2a: Remove all documents where vin is explicitly null
deleted_nulls = collection.delete_many({"vin": None})
print(f"Deleted {deleted_nulls.deleted_count} docs where vin == null")

# Step 2b: Remove documents missing the vin field entirely
deleted_missing = collection.delete_many({"vin": {"$exists": False}})
print(f"Deleted {deleted_missing.deleted_count} docs where vin was missing")

# Step 2c (optional): Fix existing docs by extracting vin from raw_response
fixed = 0
for doc in collection.find({"vin": {"$exists": False}, "raw_response.vin": {"$exists": True}}):
    vin = doc["raw_response"].get("vin")
    if vin:
        collection.update_one({"_id": doc["_id"]}, {"$set": {"vin": vin}})
        fixed += 1

print(f"Backfilled {fixed} documents with vin from raw_response")

count_missing = db["copart_car_record"].count_documents({"vin": {"$exists": False}})
print(f"Documents missing top-level vin: {count_missing}")

count_null = db["copart_car_record"].count_documents({"vin": None})
print(f"Documents with vin = null: {count_null}")
result = copart_collection.delete_many({
    "$or": [
        {"vin": None},
        {"vin": {"$exists": False}},
        {"raw_response.vin": {"$exists": False}},
        {"raw_response.vin": None}
    ]
})
print(f"🗑 Deleted {result.deleted_count} documents with missing VINs")
