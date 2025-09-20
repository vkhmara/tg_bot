from enum import Enum
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    CommandHandler,
    ConversationHandler,
    ContextTypes,
)
from exceptions.finish_conversation import FinishConversation
from services.excel.excel import Projects
from enums.settings import BotCommandType
from message_handlers.base import BaseMessageHandler, state_handler


class ResolveProjectNoteState(str, Enum):
    PROJECT_CHOICE = "project_choice"
    PROJECT_NOTE_SELECTING = "project_note_selecting"


class ResolveProjectNoteMessageHandler(BaseMessageHandler):
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
        return ResolveProjectNoteState.PROJECT_CHOICE

    @classmethod
    @state_handler
    async def choose_project(
        cls,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ):
        project = update.message.text
        if not Projects().has_project(project):
            await update.message.reply_text("No such project🔪, try again")
            return ResolveProjectNoteState.PROJECT_CHOICE

        pending_notes = Projects().get_pending_notes(
            project_name=project,
        )
        if not pending_notes:
            raise FinishConversation("No notes for the project 🤲")

        context.user_data["project"] = project
        markup = ReplyKeyboardMarkup(
            [[note.cut_note] for note in pending_notes],
            resize_keyboard=True,
            one_time_keyboard=True,
        )
        await update.message.reply_text(
            f"Choose the note for the project: {project}",
            reply_markup=markup,
        )
        return ResolveProjectNoteState.PROJECT_NOTE_SELECTING

    @classmethod
    @state_handler
    async def resolve_note(
        cls,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ):
        note_row, note = update.message.text.split(": ", maxsplit=1)
        note_row = int(note_row)

        Projects().resolve_note(
            project_name=context.user_data.get("project"),
            note=note,
            note_row=note_row,
        )

        await update.message.reply_text(
            "The note was marked as completed ✅",
            parse_mode="Markdown",
        )
        return ConversationHandler.END

    @classmethod
    def get_handlers(cls) -> list:
        return [
            ConversationHandler(
                entry_points=[
                    CommandHandler(
                        BotCommandType.RESOLVE_NOTE,
                        cls.start_conversation,
                    )
                ],
                states={
                    ResolveProjectNoteState.PROJECT_CHOICE: [
                        cls.get_message_handler(cls.choose_project),
                    ],
                    ResolveProjectNoteState.PROJECT_NOTE_SELECTING: [
                        cls.get_message_handler(cls.resolve_note),
                    ],
                },
                fallbacks=[CommandHandler(BotCommandType.CANCEL, cls.cancel)],
            ),
        ]
