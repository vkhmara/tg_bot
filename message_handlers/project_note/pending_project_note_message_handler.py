from telegram import Update, ReplyKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import (
    CommandHandler,
    ConversationHandler,
    ContextTypes,
)
from enums.message_handlers.pending_project_note import ProjectNoteState
from enums.project_note import ProjectNoteStatus
from enums.settings import BotCommandType
from pydantic_models.services.project import ProjectNoteResult
from exceptions.finish_conversation import FinishConversation
from message_handlers.base import BaseMessageHandler, state_handler
from services.project.project import get_all_project_labels, get_project
from services.project.project_note import get_project_notes_result


ALL_PROJECTS_OPTION = "All Projects"


class PendingProjectNoteMessageHandler(BaseMessageHandler):
    @classmethod
    @state_handler
    async def __start_conversation(
        cls,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ):
        all_projects_labels = get_all_project_labels()
        if not all_projects_labels:
            raise FinishConversation("Project list is empty")
        markup = ReplyKeyboardMarkup(
            [[ALL_PROJECTS_OPTION]]
            + [[project_label] for project_label in all_projects_labels],
            resize_keyboard=True,
            one_time_keyboard=True,
        )
        await update.message.reply_text(
            "Choose a project:",
            reply_markup=markup,
        )
        return ProjectNoteState.PROJECT_CHOICE

    @classmethod
    def __pending_notes_to_text(cls, project_note_results: list[ProjectNoteResult]):
        if not project_note_results:
            return "No pending notes, enjoy for now 😈"
        text = "Current pending notes\n\n"
        text += "\n".join(
            [
                f"📝\n{project_note_result.tg_text}"
                for project_note_result in project_note_results
            ]
        )
        return text

    @classmethod
    def __all_pending_notes_to_text(
        cls,
        project_note_results: list[ProjectNoteResult],
    ):
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
    async def __handle_all_pending_notes(cls, update: Update):
        pending_project_notes = get_project_notes_result(
            project_note_status=ProjectNoteStatus.PENDING,
        )

        await update.message.reply_text(
            cls.__all_pending_notes_to_text(
                project_note_results=pending_project_notes.data,
            ),
            parse_mode=ParseMode.HTML,
        )
        return ConversationHandler.END

    @classmethod
    async def __handle_project_pending_notes(
        cls,
        update: Update,
        project: str,
    ):
        db_project = get_project(
            name=project,
            optional=True,
        )
        if not db_project:
            await update.message.reply_text("No such project🔪, try again")
            return ProjectNoteState.PROJECT_CHOICE

        project_note_results = get_project_notes_result(
            project_id=db_project.id,
            project_note_status=ProjectNoteStatus.PENDING,
        )

        await update.message.reply_text(
            cls.__pending_notes_to_text(
                project_note_results=project_note_results.data,
            ),
            parse_mode=ParseMode.HTML,
        )
        return ConversationHandler.END

    @classmethod
    @state_handler
    async def __get_pending_notes(
        cls,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ):
        project = update.message.text
        if project == ALL_PROJECTS_OPTION:
            return await cls.__handle_all_pending_notes(
                update=update,
            )
        return await cls.__handle_project_pending_notes(
            update=update,
            project=project,
        )

    @classmethod
    def get_handlers(cls) -> list:
        return [
            ConversationHandler(
                entry_points=[
                    CommandHandler(
                        BotCommandType.PENDING_NOTES,
                        cls.__start_conversation,
                    ),
                ],
                states={
                    ProjectNoteState.PROJECT_CHOICE: [
                        cls._get_message_handler(cls.__get_pending_notes),
                    ],
                },
                fallbacks=[CommandHandler(BotCommandType.CANCEL, cls._cancel)],
            ),
        ]
