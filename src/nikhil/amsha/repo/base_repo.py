import pymongo

from nikhil.amsha.model.repo_data import RepoData


class BaseRepository:
    def __init__(self, data:RepoData):
        self.client = pymongo.MongoClient(data.mongo_uri)
        self.db = self.client[data.db_name]
        self.collection = self.db[data.collection_name]

    def find_one(self, query: dict):
        return self.collection.find_one(query)

    def find_many(self, query=None):
        if query is None:
            query = {}
        return list(self.collection.find(query))

    def insert_one(self, data: dict):
        return self.collection.insert_one(data)

    def insert_many(self, data: list):
        return self.collection.insert_many(data)

    def update_one(self, query: dict, data: dict):
        return self.collection.update_one(query, {"$set": data})

    def delete_one(self, query: dict):
        return self.collection.delete_one(query)