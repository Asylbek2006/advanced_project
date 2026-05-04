import os
import sys
import time

from fastapi import Depends, FastAPI, Header, HTTPException
from pydantic import BaseModel
from prometheus_fastapi_instrumentator import Instrumentator
from sqlalchemy import Integer, String, create_engine, select
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


class AccountRecord(BaseModelRecord):
    __tablename__ = "auth_accounts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(100), nullable=False)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    role: Mapped[str] = mapped_column(String(50), nullable=False)


seed_accounts = [
    {"username": "asylbek", "password": "asylbek123", "full_name": "Asylbek Abdibay", "role": "customer"},
    {"username": "bigali", "password": "bigali123", "full_name": "Bigali Omarov", "role": "operator"},
    {"username": "miras", "password": "miras123", "full_name": "Miras Saparov", "role": "customer"}
]


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    user_id: int
    full_name: str
    role: str


application = FastAPI(title="Authentication Service")
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
        existing_accounts = database_session.execute(select(AccountRecord)).scalars().all()
        if existing_accounts:
            return
        for account_payload in seed_accounts:
            database_session.add(AccountRecord(**account_payload))
        database_session.commit()


def build_token_value(user_identifier: int) -> str:
    return f"token-user-{user_identifier}"


def read_account_by_token(authorization_header: str | None, database_session: Session) -> AccountRecord:
    if not authorization_header or not authorization_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authorization header is required")

    token_value = authorization_header.replace("Bearer ", "", 1)
    if not token_value.startswith("token-user-"):
        raise HTTPException(status_code=401, detail="Invalid token format")

    user_identifier_text = token_value.replace("token-user-", "", 1)
    if not user_identifier_text.isdigit():
        raise HTTPException(status_code=401, detail="Invalid token value")

    account_record = database_session.get(AccountRecord, int(user_identifier_text))
    if not account_record:
        raise HTTPException(status_code=401, detail="Account was not found")

    return account_record


@application.get("/health")
def read_health_status():
    try:
        with database_engine.connect():
            database_status = "ok"
    except Exception:
        database_status = "unreachable"
    return {"service": "auth_service", "status": "ok", "database": database_status}


@application.post("/login", response_model=LoginResponse)
def login_user(login_request: LoginRequest, database_session: Session = Depends(get_database_session)):
    account_record = database_session.execute(
        select(AccountRecord).where(AccountRecord.username == login_request.username)
    ).scalar_one_or_none()

    if not account_record or account_record.password != login_request.password:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    return LoginResponse(
        access_token=build_token_value(account_record.id),
        user_id=account_record.id,
        full_name=account_record.full_name,
        role=account_record.role
    )


@application.get("/validate")
def validate_user_token(
    authorization: str | None = Header(default=None),
    database_session: Session = Depends(get_database_session)
):
    account_record = read_account_by_token(authorization, database_session)
    return {
        "user_id": account_record.id,
        "username": account_record.username,
        "full_name": account_record.full_name,
        "role": account_record.role
    }
