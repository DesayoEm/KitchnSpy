@echo off
REM Activate your virtual environment
call venv\Scripts\activate

REM Set project root so Celery can find the app module
set PYTHONPATH=%cd%

REM Run the Celery worker with Windows-compatible settings
celery -A app.infra.queues.celery_app worker --loglevel=info --pool=solo


pause
