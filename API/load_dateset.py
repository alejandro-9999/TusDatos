import pymongo
import json

def main():
    load()

def load():
    client = pymongo.MongoClient("mongodb://mongodb:mongodb@localhost:27017/")
    db = client["api"]
    col = db["dataset"]

    # Leer el archivo JSON y almacenar su contenido en una variable
    with open("dataset.json", "r") as f:
        dataset = json.load(f)


    col.delete_many({})


    col.insert_many(dataset)

    print("Completed....")


if __name__ == "__main__":
    main()
