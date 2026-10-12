from sqlalchemy.orm import Session
from models.product import Product

def get_by_id(db: Session, product_id: int):
    return db.query(Product).filter(Product.id == product_id).first()

def get_many_for_update(db: Session, product_ids: list[int]):
    # lock in id order so two checkouts touching the same products can't deadlock
    return (
        db.query(Product)
        .filter(Product.id.in_(product_ids))
        .order_by(Product.id)
        .populate_existing()
        .with_for_update()
        .all()
    )

def get_multi(db: Session,limit: int,offset: int,category_id: int | None = None,search: str | None = None,min_price: float | None = None,max_price: float | None = None,):
    query = db.query(Product)
    if category_id is not None:
        query = query.filter(Product.category_id == category_id)
    if search is not None:
        query = query.filter(Product.name.ilike(f"%{search}%"))
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    if max_price is not None:
        query = query.filter(Product.price <= max_price)
    total = query.count()
    items = query.order_by(Product.id).offset(offset).limit(limit).all()
    return total, items

def create(db: Session,category_id: int,name: str,description: str,price: float,stock_quantity: int,):
    product = Product(category_id=category_id,name=name,description=description,price=price,stock_quantity=stock_quantity,)
    db.add(product)
    db.commit()
    db.refresh(product)
    return product

def update(db: Session,product: Product,category_id: int,name: str,description: str,price: float,stock_quantity: int,):
    product.category_id = category_id
    product.name = name
    product.description = description
    product.price = price
    product.stock_quantity = stock_quantity
    db.commit()
    db.refresh(product)
    return product

def delete(db: Session, product: Product):
    db.delete(product)
    db.commit()
