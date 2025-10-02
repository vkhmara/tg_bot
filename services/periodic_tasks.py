import datetime
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from enums.project_note import ProjectNoteStatus
from pydantic_models.services.project import ProjectNoteResult
from services.project.project_note import get_project_notes_result


class BaseJob:
    @classmethod
    async def handler(cls, context):
        raise NotImplementedError


class OldReminderJob(BaseJob):
    TIMES = [
        datetime.time(hour=5, minute=15, tzinfo=datetime.timezone.utc),
        datetime.time(hour=8, minute=30, tzinfo=datetime.timezone.utc),
        datetime.time(hour=13, minute=30, tzinfo=datetime.timezone.utc),
    ]

    @classmethod
    def __all_pending_notes_to_text(
        cls,
        project_note_results: list[ProjectNoteResult],
    ) -> str:
        if not project_note_results:
            return "No pending notes for any project, enjoy for now 😈"
        text = "Current pending notes\n\n"
        text += "\n".join(
            [
                f"🚧 <b>{project_note_result.project_label}</b>\n"
                f"{project_note_result.tg_text}"
                for project_note_result in project_note_results
            ]
        )
        return text

    @classmethod
    async def handler(
        cls,
        context: ContextTypes.DEFAULT_TYPE,
    ):
        bot = context.bot
        job = context.job
        pending_project_notes = get_project_notes_result(
            project_note_status=ProjectNoteStatus.PENDING,
        )

        await bot.send_message(
            chat_id=job.chat_id,
            text="PENDING NOTES NOTIFICATION:\n\n"
            + cls.__all_pending_notes_to_text(
                project_note_results=pending_project_notes.data,
            ),
            parse_mode=ParseMode.HTML,
        )
