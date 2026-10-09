from pydantic import BaseModel
from typing import Optional, List

# Category Schemas
class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None

class CategoryCreate(CategoryBase):
                    pass

class CategoryResponse(CategoryBase):
    id: int

    class Config:
        from_attributes = True

    # Book Schemas
    class BookBase(BaseModel):
        title: str
        isbn: str
        publication_year: Optional[int] = None
        stock_quantity: Optional[int] = 1
        category_id: int

    class BookCreate(BookBase):
        pass

    class BookUpdate(BaseModel):
        title: Optional[str] = None
        isbn: Optional[str] = None
        publication_year: Optional[int] = None
        stock_quantity: Optional[int] = None
        category_id: Optional[int] = None

    class BookResponse(BookBase):
        id: int

    class Config:
        from_attributes = True
