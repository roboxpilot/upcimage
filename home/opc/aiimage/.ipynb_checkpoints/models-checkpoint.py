from pydantic import BaseModel

class Plan(BaseModel):
    price: int
    validity: int
    validity_time_period: str
    daily_limit: str
