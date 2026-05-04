import os
import sys
import time
from datetime import datetime

import httpx
from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel, Field
from prometheus_fastapi_instrumentator import Instrumentator
from sqlalchemy import DateTime, Float, Integer, String, create_engine, select
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
auth_service_url = read_required_env_variable("AUTH_SERVICE_URL")
user_service_url = read_required_env_variable("USER_SERVICE_URL")
product_service_url = read_required_env_variable("PRODUCT_SERVICE_URL")

database_engine = create_engine(database_url, pool_pre_ping=True)
database_session_factory = sessionmaker(bind=database_engine)


class BaseModelRecord(DeclarativeBase):
    pass


class OrderRecord(BaseModelRecord):
    __tablename__ = "customer_orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    product_id: Mapped[int] = mapped_column(Integer, nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    total_price: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[str] = mapped_column(String(40), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)


class OrderCreateRequest(BaseModel):
    product_id: int
    quantity: int = Field(ge=1, le=20)


application = FastAPI(title="Order Service")
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


def require_authorization_header(authorization_header: str | None) -> str:
    if not authorization_header:
        raise HTTPException(status_code=401, detail="Authorization header is required")
    return authorization_header


def read_user_context(authorization_header: str) -> dict:
    try:
        with httpx.Client(timeout=5.0) as service_client:
            response = service_client.get(
                f"{auth_service_url}/validate",
                headers={"Authorization": authorization_header}
            )
    except httpx.HTTPError as request_error:
        raise HTTPException(status_code=503, detail=f"Authentication service error: {request_error}") from request_error

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.json().get("detail", "Token validation failed"))

    return response.json()


def read_user_profile(user_identifier: int) -> dict:
    try:
        with httpx.Client(timeout=5.0) as service_client:
            response = service_client.get(f"{user_service_url}/users/{user_identifier}")
    except httpx.HTTPError as request_error:
        raise HTTPException(status_code=503, detail=f"User service error: {request_error}") from request_error

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.json().get("detail", "User lookup failed"))

    return response.json()


def read_product(product_identifier: int) -> dict:
    try:
        with httpx.Client(timeout=5.0) as service_client:
            response = service_client.get(f"{product_service_url}/products/{product_identifier}")
    except httpx.HTTPError as request_error:
        raise HTTPException(status_code=503, detail=f"Product service error: {request_error}") from request_error

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.json().get("detail", "Product lookup failed"))

    return response.json()


@application.get("/health")
def read_health_status():
    try:
        with database_engine.connect():
            database_status = "ok"
    except Exception:
        database_status = "unreachable"
    return {"service": "order_service", "status": "ok", "database": database_status}


@application.get("/orders")
def read_orders(
    authorization: str | None = Header(default=None),
    database_session: Session = Depends(get_database_session)
):
    authorization_header = require_authorization_header(authorization)
    user_context = read_user_context(authorization_header)

    order_records = database_session.execute(
        select(OrderRecord).where(OrderRecord.user_id == user_context["user_id"]).order_by(OrderRecord.id.desc())
    ).scalars().all()

    return [
        {
            "id": order_record.id,
            "user_id": order_record.user_id,
            "product_id": order_record.product_id,
            "quantity": order_record.quantity,
            "total_price": order_record.total_price,
            "status": order_record.status,
            "created_at": order_record.created_at.isoformat()
        }
        for order_record in order_records
    ]


@application.post("/orders")
def create_order(
    order_create_request: OrderCreateRequest,
    authorization: str | None = Header(default=None),
    database_session: Session = Depends(get_database_session)
):
    authorization_header = require_authorization_header(authorization)
    user_context = read_user_context(authorization_header)
    read_user_profile(user_context["user_id"])
    product_payload = read_product(order_create_request.product_id)

    total_price = product_payload["price"] * order_create_request.quantity
    order_record = OrderRecord(
        user_id=user_context["user_id"],
        product_id=product_payload["id"],
        quantity=order_create_request.quantity,
        total_price=total_price,
        status="created"
    )
    database_session.add(order_record)
    database_session.commit()
    database_session.refresh(order_record)

    return {
        "id": order_record.id,
        "user_id": order_record.user_id,
        "product_id": order_record.product_id,
        "quantity": order_record.quantity,
        "total_price": order_record.total_price,
        "status": order_record.status,
        "created_at": order_record.created_at.isoformat()
    }
