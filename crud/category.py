from sqlalchemy.orm import Session
from models.category import Category

def get_by_id(db: Session, category_id: int):
    return db.query(Category).filter(Category.id == category_id).first()

def get_by_name(db: Session, name: str):
    return db.query(Category).filter(Category.name == name).first()


def get_multi(db: Session, limit: int, offset: int):
    query = db.query(Category)
    total = query.count()
    items = query.order_by(Category.id).offset(offset).limit(limit).all()
    return total, items


def create(db: Session, name: str, description: str):
    category = Category(name=name, description=description)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


def update(db: Session, category: Category, name: str, description: str):
    category.name = name
    category.description = description
    db.commit()
    db.refresh(category)
    return category


def delete(db: Session, category: Category):
    db.delete(category)
    db.commit()
