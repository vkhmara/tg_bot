from telegram import Update
from telegram.ext import (
    CommandHandler,
    ContextTypes,
)
from enums.settings import BotCommandType
from message_handlers.base import BaseMessageHandler, state_handler
from services.periodic_tasks import OldReminderJob


class JobSchedulerMessageHandler(BaseMessageHandler):
    @classmethod
    @state_handler
    async def __schedule_jobs(
        cls,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ):
        chat_id = update.effective_chat.id
        await update.message.reply_text(
            "Pending notification job was scheduled"
        )

        if not context.job_queue:
            print("context doesn't contain job_queue attribute")
            return

        current_jobs = context.job_queue.get_jobs_by_name(str(chat_id))
        for job in current_jobs:
            job.schedule_removal()

        for time in OldReminderJob.TIMES:
            context.job_queue.run_daily(
                callback=OldReminderJob.handler,
                time=time,
                days=tuple(range(1, 6)),  # Monday - Friday
                chat_id=chat_id,
            )

    @classmethod
    def get_handlers(cls) -> list:
        return [
            CommandHandler(
                BotCommandType.SCHEDULE_JOBS,
                cls.__schedule_jobs,
            ),
        ]
