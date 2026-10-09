from typing import Optional
import models
import schemas
from database import Base, engine, get_db
from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.orm import Session

# Create database tables automatically
Base.metadata.create_all(bind=engine)

app = FastAPI(title="GIPHCO Book Library API")

# ==================== 1. CATEGORIES MANAGEMENT ====================
# POST /categories/ - Create a new category
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
        # 400 Bad Request for duplicate category name
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category name already exists",
        )

    new_category = models.Category(**category.model_dump())
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    return new_category

# GET /categories/ - Retrieve a list of all categories
@app.get("/categories/", response_model=list[schemas.CategoryResponse])
def list_categories(db: Session = Depends(get_db)):
    return db.query(models.Category).all()

# GET /categories/{category_id} - Retrieve a single category by ID
@app.get("/categories/{category_id}", response_model=schemas.CategoryResponse)
def get_category(category_id: int, db: Session = Depends(get_db)):
    category = (
        db.query(models.Category)
        .filter(models.Category.id == category_id)
        .first()
    )
    if not category:
        # 404 Not Found if category_id does not exist
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
        )
    return category

# ==================== 2. BOOKS MANAGEMENT ====================
# POST /books/ - Add a new book
@app.post(
    "/books/",
    response_model=schemas.BookResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_book(book: schemas.BookCreate, db: Session = Depends(get_db)):
    # 400 Bad Request if linked category_id does not exist
    category = (
        db.query(models.Category)
        .filter(models.Category.id == book.category_id)
        .first()
    )
    if not category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot create book: Category ID does not exist",
        )

    # 400 Bad Request if duplicate ISBN
    if db.query(models.Book).filter(models.Book.isbn == book.isbn).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot create book: ISBN already exists",
        )

    new_book = models.Book(**book.model_dump())
    db.add(new_book)
    db.commit()
    db.refresh(new_book)
    return new_book

# GET /books/ - Retrieve all books (Supports optional query filtering by category_id)
@app.get("/books/", response_model=list[schemas.BookResponse])
def list_books(
    category_id: Optional[int] = None, db: Session = Depends(get_db)
):
    if category_id is not None:
        # Check if the requested category_id actually exists
        category = (
            db.query(models.Category)
            .filter(models.Category.id == category_id)
            .first()
        )
        if not category:
            # 404 Not Found if queried category_id does not exist
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category ID not found",
            )
        return (
            db.query(models.Book)
            .filter(models.Book.category_id == category_id)
            .all()
        )

    return db.query(models.Book).all()

# GET /books/{book_id} - Retrieve details of a specific book by ID
@app.get("/books/{book_id}", response_model=schemas.BookResponse)
def get_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not book:
        # 404 Not Found if queried book_id does not exist
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Book not found"
        )
    return book

# PUT /books/{book_id} - Update book information
@app.put("/books/{book_id}", response_model=schemas.BookResponse)
def update_book(
    book_id: int,
    updated_data: schemas.BookCreate,
    db: Session = Depends(get_db),
):
    book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not book:
        # 404 Not Found if queried book_id does not exist
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Book not found"
        )

    # 400 Bad Request if the updated category_id does not exist
    category = (
        db.query(models.Category)
        .filter(models.Category.id == updated_data.category_id)
        .first()
    )
    if not category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot update book: Category ID does not exist",
        )

    # 400 Bad Request if changing to an ISBN that belongs to another book
    existing_isbn = (
        db.query(models.Book)
        .filter(
            models.Book.isbn == updated_data.isbn, models.Book.id != book_id
        )
        .first()
    )
    if existing_isbn:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot update book: ISBN already in use by another book",
        )

    for key, value in updated_data.model_dump().items():
        setattr(book, key, value)

    db.commit()
    db.refresh(book)
    return book

# DELETE /books/{book_id} - Remove a book from inventory
@app.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not book:
        # 404 Not Found if queried book_id does not exist
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Book not found"
        )

    db.delete(book)
    db.commit()