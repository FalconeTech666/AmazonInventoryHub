import os


def required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


DB_CONFIG = {
    "host": required_env("AMAZON_DB_HOST"),
    "port": os.getenv("AMAZON_DB_PORT", "5432"),
    "database": os.getenv("AMAZON_DB_NAME", "postgres"),
    "user": required_env("AMAZON_DB_USER"),
    "password": required_env("AMAZON_DB_PASSWORD"),
    "pool_mode": os.getenv("AMAZON_DB_POOL_MODE", "session"),
}
