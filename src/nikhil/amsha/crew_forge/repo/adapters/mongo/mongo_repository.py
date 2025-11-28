# src/nikhil/amsha/toolkit/crew_forge/adapters/mongo/task_repo.py
import pymongo

from nikhil.amsha.crew_forge.domain.models.repo_data import RepoData
from nikhil.amsha.crew_forge.repo.interfaces.i_repository import IRepository


class MongoRepository(IRepository):
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

    def create_unique_compound_index(self, keys: list[str]):
        if not keys:
            raise ValueError("List of keys cannot be empty.")
        index_keys = [(key, pymongo.ASCENDING) for key in keys]
        try:
            self.collection.create_index(index_keys, unique=True)
            print(f"Unique compound index created on: {keys}")
        except Exception as e:
            print(f"Error creating unique compound index on {keys}: {e}")