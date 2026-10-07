from fastapi import Depends, FastAPI
from auth import get_current_user
from routers import auth, categories, orders, users, products,payments, order_items

app = FastAPI()

app.include_router(auth.router)
app.include_router(categories.router, dependencies=[Depends(get_current_user)])
app.include_router(users.router)
app.include_router(orders.router, dependencies=[Depends(get_current_user)])
app.include_router(products.router, dependencies=[Depends(get_current_user)])
app.include_router(order_items.router, dependencies=[Depends(get_current_user)])
app.include_router(payments.router, dependencies=[Depends(get_current_user)])




