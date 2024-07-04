from settings import settings
from sqlalchemy import create_engine
from sqlalchemy import MetaData, Table, Column
from sqlalchemy import Integer, String, Boolean, Float, DateTime
import databases

print(settings.database_url)

database = databases.Database(settings.database_url)
engine = create_engine(settings.database_url)
metadata = MetaData()

user_registration = Table (
    "user_registration",
    metadata,
    Column("userid", String),
    Column("email", String),
    Column("federated_identity", String),
        # email-password
        # google
    Column("start_date", DateTime),
    Column("end_date", DateTime)
)

user_login = Table (
    "user_login",
    metadata,
    Column("userid", String),
    Column("status_code", String),
    Column("delay_ms", Integer),
)

user_block = Table (
    "user_block",
    metadata,
    Column("userid", String),
    Column("reason", String),
    Column("start_date", DateTime),
    Column("end_date", DateTime)
)

user_reset_password = Table (
    "user_reset_password",
    metadata,
    Column("userid", String),
    Column("token", String),
    Column("start_date", DateTime),
    Column("used_date", DateTime),
)

user_action = Table (
    "user_action",
    metadata,
    Column("userid", String),
    Column("action", String),
        # like
        # rewind
        # send_message
    Column("date", DateTime)
)


# region geografica:
    # hacer una grilla de lat y long

# tendencias de uso:
    # genero
    # tiempo de login
    # cantidad de login
    #

metadata.create_all(engine)

# Dependency
async def get_db():
    await database.connect()
    try:
        yield database
    finally:
        await database.disconnect()	