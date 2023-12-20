from langchain.pydantic_v1 import BaseModel, Field


class ResponseModel(BaseModel):
       markdownContent :str =Field(...,description="This will store the markdown content of the built report")
       