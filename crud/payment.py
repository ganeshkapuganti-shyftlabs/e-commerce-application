from sqlalchemy.orm import Session
from models.payment import Payment

def get_by_id(db: Session, payment_id: int):
    return db.query(Payment).filter(Payment.id == payment_id).first()

def get_by_id_for_update(db: Session, payment_id: int):
    return db.query(Payment).filter(Payment.id == payment_id).populate_existing().with_for_update().first()

def get_by_transaction_id(db: Session, transaction_id: str):
    return db.query(Payment).filter(Payment.transaction_id == transaction_id).first()

def get_multi(db: Session, limit: int, offset: int, order_id: int | None = None):
    query = db.query(Payment)
    if order_id is not None:
        query = query.filter(Payment.order_id == order_id)
    total = query.count()
    items = query.order_by(Payment.id.desc()).offset(offset).limit(limit).all()
    return total, items

def create(db:Session,order_id: int,amount: float,payment_method: str,status: str,transaction_id: str,commit: bool = True):
    payment = Payment(order_id=order_id,amount=amount,payment_method=payment_method,status=status,transaction_id=transaction_id,)
    db.add(payment)
    if commit:
        db.commit()
        db.refresh(payment)
    else:
        db.flush()
    return payment
