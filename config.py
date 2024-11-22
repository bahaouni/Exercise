import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "mysecret")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "postgresql://postgres:postgres@localhost/assignment")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "jwtsecret")
    # REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
    # CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL", REDIS_URL)
    # CELERY_RESULT_BACKEND = REDIS_URL
