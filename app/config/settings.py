from dotenv import load_dotenv
import os

load_dotenv()


class Settings:

    SECRET_KEY = os.getenv(
        "SECRET_KEY",
        "inventory-secret-key"
    )

    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "sqlite:///./inventory.db"
    )

    POC_ID = os.getenv(
        "POC_ID",
        "POC-07"
    )

    PHASE = os.getenv(
        "PHASE",
        "P1"
    )

    ASSOCIATE_ID = os.getenv(
        "ASSOCIATE_ID",
        "PO20695814"
    )


settings = Settings()