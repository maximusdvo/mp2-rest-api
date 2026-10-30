"""pydantic models for API requests and response"""

from pydantic import BaseModel

class HealthResponse(BaseModel):
    """response treutnred by health check enpoint"""

    status:str
    version: str

class DatasetInfo(BaseModel):
    """metadata returned after a dataset is uploaded"""

    id: int
    filename: str
    rows: int
    columns: int
    column_names: list[str]
