import time
from fastapi import Request, status, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.exceptions import *
from app.infra.log_service import logger


class ExceptionMiddleware(BaseHTTPMiddleware):
    error_map = {
        DBInsertionError: status.HTTP_500_INTERNAL_SERVER_ERROR,
        ParsingError: status.HTTP_500_INTERNAL_SERVER_ERROR,
        PriceLoggingError: status.HTTP_500_INTERNAL_SERVER_ERROR,
        FailedRequestError: status.HTTP_500_INTERNAL_SERVER_ERROR,
        URLNotFoundError: status.HTTP_500_INTERNAL_SERVER_ERROR,
        IDNotFoundError: status.HTTP_500_INTERNAL_SERVER_ERROR

    }

    async def dispatch(self, request: Request, call_next):
        logger.info(f"Request started | {request.method} {request.url.path}")
        start_time = time.time()

        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            logger.info(f"Request completed | Status: {response.status_code} | Time: {process_time:.3f}s")
            return response

        except Exception as e:
            process_time = time.time() - start_time
            logger.error(f"Exception | {str(e)}", exc_info=True)
            return self.handle_exception(e)


    def handle_exception(self, e):
        if isinstance(e, HTTPException):
            logger.warning(f"HTTPException | {e.detail}")
            return JSONResponse(
                status_code=e.status_code,
                content={"detail": e.detail}
            )

        for error, status_code in self.error_map.items():
            if isinstance(e, error):
                log_level = logger.warning if status_code < 500 else logger.error
                log_level(f"{error.__name__} | {e.log}")
                return self.create_json_response(e, status_code)


        log_message = f"Unhandled exception | {str(e)}"

        logger.error(log_message, exc_info = True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": "An unexpected error occurred.",
            }
        )

    @staticmethod
    def create_json_response(e, status_code):
        return JSONResponse(
            status_code=status_code,
            content={"detail": e.display}
        )








