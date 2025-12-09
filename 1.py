from pymongo import MongoClient

def get_db():
    client = MongoClient("mongodb://localhost:27017/")
    db = client["ecotrack"]
    return db

# Test
if __name__ == "__main__":
    db = get_db()
    print("Connected!")
    print("Collections:", db.list_collection_names())

