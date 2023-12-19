from langchain.pydantic_v1 import BaseModel, Field


class ResponseModel(BaseModel):
       reward :int =Field(...,description="On the scale of 1 to 100, On the basis of the provided context rate the report,how much does it aligns to it ")
       lacking_areas :str = Field(...,description="List the points where it lacks, as per the context provided")
       improving_areas :str = Field(...,description="List the points where it has edge and how it can be improved")
