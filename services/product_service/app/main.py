import os
import sys
import time

from fastapi import Depends, FastAPI, HTTPException
from prometheus_fastapi_instrumentator import Instrumentator
from sqlalchemy import Float, Integer, String, create_engine, select
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker


def read_required_env_variable(variable_name: str) -> str:
    variable_value = os.getenv(variable_name)
    if not variable_value:
        print(f"STARTUP ERROR: required environment variable '{variable_name}' is missing or empty")
        sys.exit(1)
    return variable_value


def build_database_url_from_env() -> str:
    database_host = read_required_env_variable("DATABASE_HOST")
    database_port = read_required_env_variable("DATABASE_PORT")
    database_name = read_required_env_variable("DATABASE_NAME")
    database_user = read_required_env_variable("DATABASE_USER")
    database_password = read_required_env_variable("DATABASE_PASSWORD")
    return f"postgresql+psycopg://{database_user}:{database_password}@{database_host}:{database_port}/{database_name}"


database_url = build_database_url_from_env()
database_engine = create_engine(database_url, pool_pre_ping=True)
database_session_factory = sessionmaker(bind=database_engine)


class BaseModelRecord(DeclarativeBase):
    pass


class ProductRecord(BaseModelRecord):
    __tablename__ = "product_catalog"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    stock_quantity: Mapped[int] = mapped_column(Integer, nullable=False)


seed_products = [
    {"name": "Monitoring Keyboard", "description": "Mechanical keyboard for operations teams", "price": 120.0, "stock_quantity": 14},
    {"name": "Cloud Mouse", "description": "Wireless mouse for daily admin work", "price": 45.0, "stock_quantity": 30},
    {"name": "Status Screen", "description": "Compact dashboard display", "price": 220.0, "stock_quantity": 8},
    {"name": "Incident Notebook", "description": "Notebook for runbooks and notes", "price": 15.0, "stock_quantity": 50}
]


application = FastAPI(title="Product Service")
Instrumentator().instrument(application).expose(application)


def wait_for_database() -> None:
    last_error = None
    for _ in range(30):
        try:
            with database_engine.connect():
                return
        except OperationalError as connection_error:
            last_error = connection_error
            time.sleep(2)
    raise last_error


def get_database_session():
    database_session = database_session_factory()
    try:
        yield database_session
    finally:
        database_session.close()


@application.on_event("startup")
def start_application() -> None:
    wait_for_database()
    BaseModelRecord.metadata.create_all(bind=database_engine)
    with database_session_factory() as database_session:
        existing_products = database_session.execute(select(ProductRecord)).scalars().all()
        if existing_products:
            return
        for product_payload in seed_products:
            database_session.add(ProductRecord(**product_payload))
        database_session.commit()


@application.get("/health")
def read_health_status():
    try:
        with database_engine.connect():
            database_status = "ok"
    except Exception:
        database_status = "unreachable"
    return {"service": "product_service", "status": "ok", "database": database_status}


@application.get("/products")
def read_products(database_session: Session = Depends(get_database_session)):
    product_records = database_session.execute(select(ProductRecord).order_by(ProductRecord.id)).scalars().all()
    return [
        {
            "id": product_record.id,
            "name": product_record.name,
            "description": product_record.description,
            "price": product_record.price,
            "stock_quantity": product_record.stock_quantity
        }
        for product_record in product_records
    ]


@application.get("/products/{product_identifier}")
def read_product(product_identifier: int, database_session: Session = Depends(get_database_session)):
    product_record = database_session.get(ProductRecord, product_identifier)
    if not product_record:
        raise HTTPException(status_code=404, detail="Product was not found")

    return {
        "id": product_record.id,
        "name": product_record.name,
        "description": product_record.description,
        "price": product_record.price,
        "stock_quantity": product_record.stock_quantity
    }
