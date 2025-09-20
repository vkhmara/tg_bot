from enum import Enum
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    CommandHandler,
    ConversationHandler,
    ContextTypes,
)
from exceptions.finish_conversation import FinishConversation
from services.excel.excel import ProjectNote, Projects
from enums.settings import BotCommandType
from message_handlers.base import BaseMessageHandler, state_handler


class ProjectNoteState(str, Enum):
    PROJECT_CHOICE = "project_choice"


class PendingProjectNoteMessageHandler(BaseMessageHandler):
    @classmethod
    @state_handler
    async def start_conversation(
        cls,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ):
        all_projects_names = Projects().get_all_project_sheetnames()
        if not all_projects_names:
            raise FinishConversation("Project list is empty")
        markup = ReplyKeyboardMarkup(
            [[project_name] for project_name in all_projects_names],
            resize_keyboard=True,
            one_time_keyboard=True,
        )
        await update.message.reply_text(
            "Choose a project:",
            reply_markup=markup,
        )
        return ProjectNoteState.PROJECT_CHOICE

    @classmethod
    def __pending_note_to_text(cls, note: ProjectNote):
        return f"*Note*: {note.note}\n*Created At*: {note.created_at}"

    @classmethod
    def __pending_notes_to_text(cls, notes: list[ProjectNote]):
        if not notes:
            return "No pending notes, enjoy for now 😈"
        text = "Current pending notes\n\n"
        text += "\n\n".join([cls.__pending_note_to_text(note) for note in notes])
        return text

    @classmethod
    @state_handler
    async def get_pending_notes(
        cls,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ):
        project = update.message.text
        if not Projects().has_project(project):
            await update.message.reply_text("No such project🔪, try again")
            return ProjectNoteState.PROJECT_CHOICE

        pending_notes = Projects().get_pending_notes(
            project_name=project,
        )

        await update.message.reply_text(
            cls.__pending_notes_to_text(notes=pending_notes),
            parse_mode="Markdown",
        )
        return ConversationHandler.END

    @classmethod
    def get_handlers(cls) -> list:
        return [
            ConversationHandler(
                entry_points=[
                    CommandHandler(
                        BotCommandType.PENDING_NOTES,
                        cls.start_conversation,
                    )
                ],
                states={
                    ProjectNoteState.PROJECT_CHOICE: [
                        cls.get_message_handler(cls.get_pending_notes),
                    ],
                },
                fallbacks=[CommandHandler(BotCommandType.CANCEL, cls.cancel)],
            ),
        ]
