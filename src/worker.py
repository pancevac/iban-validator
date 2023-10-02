from arq.connections import RedisSettings

from src.config import config
from src.db import sessionmanager
from src.iban.models import StatusTypes
from src.iban.services import IBANValidationHistoryService
from src.iban.utils import Task


async def on_startup(_):
    if not config.TESTING:
        sessionmanager.init(host=str(config.DB_URI))
        print('DB connection initialized!')


async def on_shutdown(_):
    if sessionmanager.engine is not None:
        await sessionmanager.close()
        print('Closing DB connections!')


async def process_iban_validation_result(_, task: Task):
    async with sessionmanager.session() as db:
        service = IBANValidationHistoryService(db)
        await service.save(
            iban_code=task.iban,
            status=task.status,
            error_msg=task.error.errors()[0]['msg'] if task.status == StatusTypes.failed else None
        )


class WorkerSettings:
    functions = [process_iban_validation_result]
    redis_settings = RedisSettings().from_dsn(str(config.REDIS_URI))
    on_startup = on_startup
    on_shutdown = on_shutdown
