import os
import sys
import time

from fastapi import Depends, FastAPI, HTTPException
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


class UserProfileRecord(BaseModelRecord):
    __tablename__ = "user_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=False)
    department: Mapped[str] = mapped_column(String(100), nullable=False)


seed_user_profiles = [
    {"username": "asylbek", "full_name": "Asylbek Abdibay", "email": "asylbek@qadamretail.com", "department": "Sales"},
    {"username": "bigali", "full_name": "Bigali Omarov", "email": "bigali@qadamretail.com", "department": "Operations"},
    {"username": "miras", "full_name": "Miras Saparov", "email": "miras@qadamretail.com", "department": "Support"}
]


application = FastAPI(title="User Service")
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
        existing_user_profiles = database_session.execute(select(UserProfileRecord)).scalars().all()
        if existing_user_profiles:
            return
        for user_profile_payload in seed_user_profiles:
            database_session.add(UserProfileRecord(**user_profile_payload))
        database_session.commit()


@application.get("/health")
def read_health_status():
    try:
        with database_engine.connect():
            database_status = "ok"
    except Exception:
        database_status = "unreachable"
    return {"service": "user_service", "status": "ok", "database": database_status}


@application.get("/users")
def read_user_profiles(database_session: Session = Depends(get_database_session)):
    user_profile_records = database_session.execute(select(UserProfileRecord).order_by(UserProfileRecord.id)).scalars().all()
    return [
        {
            "id": user_profile_record.id,
            "username": user_profile_record.username,
            "full_name": user_profile_record.full_name,
            "email": user_profile_record.email,
            "department": user_profile_record.department
        }
        for user_profile_record in user_profile_records
    ]


@application.get("/users/{user_identifier}")
def read_user_profile(user_identifier: int, database_session: Session = Depends(get_database_session)):
    user_profile_record = database_session.get(UserProfileRecord, user_identifier)
    if not user_profile_record:
        raise HTTPException(status_code=404, detail="User profile was not found")

    return {
        "id": user_profile_record.id,
        "username": user_profile_record.username,
        "full_name": user_profile_record.full_name,
        "email": user_profile_record.email,
        "department": user_profile_record.department
    }
