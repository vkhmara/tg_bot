from enum import Enum
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    CommandHandler, MessageHandler, ConversationHandler,
    ContextTypes, filters
)
from services.excel.excel import Projects
from enums.settings import BotCommandType


class ResolveProjectNoteState(str, Enum):
    PROJECT_CHOICE = "project_choice"
    PROJECT_NOTE_SELECTING = "project_note_selecting"


class ResolveProjectNoteMessageHandler:
    @classmethod
    async def start_conversation(
        cls,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ):
        all_projects_names = Projects().get_all_project_sheetnames()
        if not all_projects_names:
            await update.message.reply_text("Project list is empty")
            return ConversationHandler.END
        markup = ReplyKeyboardMarkup(
            [
                [project_name]
                for project_name in all_projects_names
            ],
            resize_keyboard=True,
            one_time_keyboard=True,
        )
        await update.message.reply_text("Choose a note:", reply_markup=markup)
        return ResolveProjectNoteState.PROJECT_CHOICE

    @classmethod
    async def choose_project(
        cls,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ):
        project = update.message.text
        if not Projects().has_project(project):
            await update.message.reply_text("No such project, try again")
            return ResolveProjectNoteState.PROJECT_CHOICE

        try:
            pending_notes = Projects().get_pending_notes(
                project_name=project,
            )
        except Exception as e:
            print(e)
            await update.message.reply_text(f"Something went wrong")
            return ConversationHandler.END

        context.user_data["project"] = project
        markup = ReplyKeyboardMarkup(
            [
                [note.cut_note]
                for note in pending_notes
            ],
            resize_keyboard=True,
            one_time_keyboard=True,
        )
        await update.message.reply_text(
            f"Choose the note for the project: {project}",
            reply_markup=markup,
        )
        return ResolveProjectNoteState.PROJECT_NOTE_SELECTING

    @classmethod
    async def resolve_note(
        cls,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ):
        note_row, note = update.message.text.split(": ", maxsplit=1)
        note_row = int(note_row)

        try:
            Projects().resolve_note(
                project_name=context.user_data.get("project"),
                note=note,
                note_row=note_row,
            )
        except Exception as e:
            print(e)
            await update.message.reply_text(f"Something went wrong")
            return ConversationHandler.END

        await update.message.reply_text(
            "The note was marked as completed ✅",
            parse_mode="Markdown",
        )
        return ConversationHandler.END

    @classmethod
    async def cancel(
        cls,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ):
        await update.message.reply_text("Operation cancelled", reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END

    @classmethod
    def get_handlers(cls) -> list:
        return [
            ConversationHandler(
                entry_points=[CommandHandler(BotCommandType.RESOLVE_NOTE, cls.start_conversation)],
                states={
                    ResolveProjectNoteState.PROJECT_CHOICE: [
                        MessageHandler(filters.TEXT & ~filters.COMMAND, cls.choose_project),
                    ],
                    ResolveProjectNoteState.PROJECT_NOTE_SELECTING: [
                        MessageHandler(filters.TEXT & ~filters.COMMAND, cls.resolve_note),
                    ],
                },
                fallbacks=[CommandHandler(BotCommandType.CANCEL, cls.cancel)],
            ),
        ]
