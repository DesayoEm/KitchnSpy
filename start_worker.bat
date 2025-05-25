@echo off
REM Activate your virtual environment
call venv\Scripts\activate

REM Set project root so Celery can find the app module
set PYTHONPATH=%cd%

REM Set environment variable for Windows multiprocessing
set FORKED_BY_MULTIPROCESSING=1

REM Run the Celery worker with Windows-compatible settings and debug mode
celery -A app.infra.queues.worker worker --loglevel=info --pool=solo --concurrency=1 -Q default

echo Worker started. Press Ctrl+C to stop.
pause