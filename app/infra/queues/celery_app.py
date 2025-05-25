from celery import Celery
from app.infra.config import settings


celery_app = Celery('app')
celery_app.conf.update(
    broker_url = settings.REDIS_URL,
    result_backend=settings.DB_URI,
    mongodb_backend_settings={
        "database": "kitchnspy",
        "taskmeta_collection": "tasks"
    },
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)
celery_app.autodiscover_tasks([
    "app.domain.products",
    "app.domain.price_logs",
    "app.domain.subscribers",
])

celery_app.conf.task_routes = {
    "send_email_notification": {"queue": "default"},
}



