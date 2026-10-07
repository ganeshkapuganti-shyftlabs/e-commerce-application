from sqlalchemy import (
    Column, BigInteger, Integer, DateTime, ForeignKey, CheckConstraint, UniqueConstraint, func
)
from sqlalchemy.orm import relationship
from database import Base


class CartItem(Base):
    __tablename__ = "cart_items"
    id = Column(BigInteger, primary_key=True, index=True)
    cart_id = Column(BigInteger, ForeignKey("carts.id", ondelete="CASCADE"), nullable=False, index=True)
    product_id = Column(BigInteger, ForeignKey("products.id"), nullable=False, index=True)
    quantity = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    cart = relationship("Cart", back_populates="items")
    product = relationship("Product")

    __table_args__ = (
        UniqueConstraint("cart_id", "product_id", name="uq_cart_items_cart_product"),
        CheckConstraint("quantity >= 1", name="check_cart_item_quantity"),
    )
