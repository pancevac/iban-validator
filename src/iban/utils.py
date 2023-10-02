from typing import Callable, Coroutine, Any, Union

from fastapi import Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.routing import APIRoute

from src.iban.models import StatusTypes
from src.iban.validator.exceptions import BaseIBANException
from src.queue import get_redis


class IBANValidationErrorLoggingRoute(APIRoute):
    def get_route_handler(self) -> Callable[[Request], Coroutine[Any, Any, Response]]:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            try:
                return await original_route_handler(request)
            except RequestValidationError as exc:

                # ensure to apply logging only on route "validate"
                if request.scope.get('route').name != 'validate' or request.method != 'POST':
                    raise exc

                task = Task(
                    iban=str(exc.body.get('code')),
                    status=StatusTypes.failed,
                    error=exc
                )

                async with get_redis() as redis:
                    await redis.enqueue_job('process_iban_validation_result', task)

                raise exc

        return custom_route_handler


class Task:
    def __init__(
            self,
            iban: str,
            status: StatusTypes, error: Union[BaseIBANException, RequestValidationError, None] = None
    ):
        self.iban = iban
        self.status = status
        self.error = error
