from celery import Celery
from app.infra.config import settings


celery_app = Celery('app')
celery_app.conf.update(
    broker_url = settings.REDIS_URL,
    result_backend=settings.DB_URI,
    mongodb_backend_settings={
        "database": "kitchnspy",
        "taskmeta_collection": "celery_tasks"
    },
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    include=['app.domain.subscribers.services.notification_service.tasks']

)
celery_app.conf.task_routes = {
    "send_email_notification": {"queue": "default"},
}



