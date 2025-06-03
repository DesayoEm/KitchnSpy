from celery import Celery
from app.infra.config import settings


celery_app = Celery('app')
celery_app.conf.update(
    broker_url = settings.REDIS_URL,
    result_backend=settings.DB_URI,
    mongodb_backend_settings={
        "database": "kitchnspy",
        "taskmeta_collection": "celery_results"
    },
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_store_eager_result=True,
    task_track_started=True,
    result_extended=True,
    include=['app.domain.products.services.notification_service.tasks',
             'app.domain.price_logs.services.notification_service.tasks',
             'app.domain.subscribers.services.notification_service.tasks']
)


celery_app.conf.task_routes = {
    "send_product_email_notification": {"queue": "default"},
    "send_price_email_notification": {"queue": "default"},
    "send_subscription_email_notification": {"queue": "default"}

}



