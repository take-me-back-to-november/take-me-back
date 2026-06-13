import os


def get_database_url() -> str:
    user = os.getenv("POSTGRES_USER", "postgres")
    password = os.getenv("POSTGRES_PASSWORD", "postgres")
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    database = os.getenv("POSTGRES_DB", "take_me_back")
    return f"postgres://{user}:{password}@{host}:{port}/{database}"


def get_models() -> list[str]:
    files = os.listdir(os.path.join(os.path.dirname(__file__), "..", "models"))
    model_names = [file.removesuffix(".py") for file in files if file.endswith(".py")]
    return [f"models.{model_name}" for model_name in model_names]


TORTOISE_ORM = {
    "connections": {
        "default": get_database_url(),
    },
    "apps": {
        "models": {
            "models": get_models(),
            "default_connection": "default",
        },
    },
}
