import os
import sys
import time
from datetime import datetime

import httpx
from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel, Field
from prometheus_fastapi_instrumentator import Instrumentator
from sqlalchemy import DateTime, Integer, String, Text, create_engine, or_, select
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

database_engine = create_engine(database_url, pool_pre_ping=True)
database_session_factory = sessionmaker(bind=database_engine)


class BaseModelRecord(DeclarativeBase):
    pass


class ChatMessageRecord(BaseModelRecord):
    __tablename__ = "chat_messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    sender_user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    receiver_user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    message_text: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)


class ChatMessageCreateRequest(BaseModel):
    receiver_user_id: int
    message_text: str = Field(min_length=1, max_length=400)


application = FastAPI(title="Chat Service")
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


def ensure_user_exists(user_identifier: int) -> None:
    try:
        with httpx.Client(timeout=5.0) as service_client:
            response = service_client.get(f"{user_service_url}/users/{user_identifier}")
    except httpx.HTTPError as request_error:
        raise HTTPException(status_code=503, detail=f"User service error: {request_error}") from request_error

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.json().get("detail", "User lookup failed"))


@application.get("/health")
def read_health_status():
    try:
        with database_engine.connect():
            database_status = "ok"
    except Exception:
        database_status = "unreachable"
    return {"service": "chat_service", "status": "ok", "database": database_status}


@application.get("/messages")
def read_messages(
    authorization: str | None = Header(default=None),
    database_session: Session = Depends(get_database_session)
):
    authorization_header = require_authorization_header(authorization)
    user_context = read_user_context(authorization_header)
    current_user_identifier = user_context["user_id"]

    message_records = database_session.execute(
        select(ChatMessageRecord)
        .where(
            or_(
                ChatMessageRecord.sender_user_id == current_user_identifier,
                ChatMessageRecord.receiver_user_id == current_user_identifier
            )
        )
        .order_by(ChatMessageRecord.id.desc())
    ).scalars().all()

    return [
        {
            "id": message_record.id,
            "sender_user_id": message_record.sender_user_id,
            "receiver_user_id": message_record.receiver_user_id,
            "message_text": message_record.message_text,
            "created_at": message_record.created_at.isoformat()
        }
        for message_record in message_records
    ]


@application.post("/messages")
def create_message(
    chat_message_create_request: ChatMessageCreateRequest,
    authorization: str | None = Header(default=None),
    database_session: Session = Depends(get_database_session)
):
    authorization_header = require_authorization_header(authorization)
    user_context = read_user_context(authorization_header)

    if user_context["user_id"] == chat_message_create_request.receiver_user_id:
        raise HTTPException(status_code=400, detail="Sender and receiver must be different users")

    ensure_user_exists(chat_message_create_request.receiver_user_id)

    chat_message_record = ChatMessageRecord(
        sender_user_id=user_context["user_id"],
        receiver_user_id=chat_message_create_request.receiver_user_id,
        message_text=chat_message_create_request.message_text.strip()
    )
    database_session.add(chat_message_record)
    database_session.commit()
    database_session.refresh(chat_message_record)

    return {
        "id": chat_message_record.id,
        "sender_user_id": chat_message_record.sender_user_id,
        "receiver_user_id": chat_message_record.receiver_user_id,
        "message_text": chat_message_record.message_text,
        "created_at": chat_message_record.created_at.isoformat()
    }
