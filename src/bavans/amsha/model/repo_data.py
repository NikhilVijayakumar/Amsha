from pydantic import BaseModel, Field


class RepoData(BaseModel):
    mongo_uri: str = Field(..., description="Mongo db URI")
    db_name: str = Field(..., description="The name of database")
    collection_name: str = Field(..., description="The name of collection")