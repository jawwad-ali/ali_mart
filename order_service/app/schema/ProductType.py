from sqlmodel import Field, SQLModel
from typing import Optional

class Product(SQLModel,table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    productName: str = Field(index=True)
    productPrice: int = Field(index=True)
    productDesc: str = Field(index=True)
    inStock: int = Field(index=True)