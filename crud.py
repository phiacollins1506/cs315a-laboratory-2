from typing import List
import models
import schemas
from database import Base, engine, get_db
from fastapi import Depends, FastAPI, HTTPException, Response, status
from sqlalchemy.orm import Session

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="GIPHCO Book Library API",
    description="Full CRUD backend service for managing book inventory and categories.",
)


@app.get("/")
def read_root():
    return {
        "message": "Welcome to the GIPHCO Book Library API",
        "docs": "/docs",
    }

@app.post(
    "/categories/",
    response_model=schemas.CategoryResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_category(
    category: schemas.CategoryCreate, db: Session = Depends(get_db)
):
    if (
        db.query(models.Category)
        .filter(models.Category.name == category.name)
        .first()
    ):
        raise HTTPException(
            status_code=400, detail="Category name already exists"
        )

    new_category = models.Category(**category.model_dump())
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    return new_category

@app.get("/categories/", response_model=List[schemas.CategoryResponse])
def list_categories(db: Session = Depends(get_db)):
    return db.query(models.Category).all()

@app.get("/categories/{category_id}", response_model=schemas.CategoryResponse)
def get_category(category_id: int, db: Session = Depends(get_db)):
    category = (
        db.query(models.Category)
        .filter(models.Category.id == category_id)
        .first()
    )
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category

@app.put("/categories/{category_id}", response_model=schemas.CategoryResponse)
def update_category(
    category_id: int,
    updated_data: schemas.CategoryCreate,
    db: Session = Depends(get_db),
):
    query = db.query(models.Category).filter(models.Category.id == category_id)
    category = query.first()

    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    query.update(updated_data.model_dump(), synchronize_session=False)
    db.commit()
    db.refresh(category)
    return category

@app.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(category_id: int, db: Session = Depends(get_db)):
    category = (
        db.query(models.Category)
        .filter(models.Category.id == category_id)
        .first()
    )
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    db.delete(category)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.post(
    "/books/",
    response_model=schemas.BookResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_book(book: schemas.BookCreate, db: Session = Depends(get_db)):
    if not (
        db.query(models.Category)
        .filter(models.Category.id == book.category_id)
        .first()
    ):
        raise HTTPException(
            status_code=404, detail="Category ID does not exist"
        )

    if db.query(models.Book).filter(models.Book.isbn == book.isbn).first():
        raise HTTPException(
            status_code=400, detail="Book with this ISBN already exists"
        )

    new_book = models.Book(**book.model_dump())
    db.add(new_book)
    db.commit()
    db.refresh(new_book)
    return new_book

@app.get("/books/", response_model=List[schemas.BookResponse])
def list_books(db: Session = Depends(get_db)):
    return db.query(models.Book).all()

@app.get("/books/{book_id}", response_model=schemas.BookResponse)
def get_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book

@app.put("/books/{book_id}", response_model=schemas.BookResponse)
def update_book(
    book_id: int,
    updated_data: schemas.BookCreate,
    db: Session = Depends(get_db),
):
    query = db.query(models.Book).filter(models.Book.id == book_id)
    book = query.first()

    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    if not (
        db.query(models.Category)
        .filter(models.Category.id == updated_data.category_id)
        .first()
    ):
        raise HTTPException(
            status_code=404, detail="Category ID does not exist"
        )

    query.update(updated_data.model_dump(), synchronize_session=False)
    db.commit()
    db.refresh(book)
    return book

@app.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    db.delete(book)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)