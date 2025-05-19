import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.infra.queues.celery_app import celery_app


if __name__ == '__main__':
    if os.name == 'nt':
        os.environ.setdefault('FORKED_BY_MULTIPROCESSING', '1')
        sys.argv.extend(['--pool=solo'])

    celery_app.worker_main(sys.argv)