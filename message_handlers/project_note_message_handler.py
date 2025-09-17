from enum import Enum
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    CommandHandler, MessageHandler, ConversationHandler,
    ContextTypes, filters
)
from services.excel.excel import ProjectNote, Projects
from functools import partial
from enums.settings import BotCommandType


class ProjectNoteState(str, Enum):
    PROJECT_CHOICE = "project_choice"
    PROJECT_NOTE_TYPING = "project_note_typing"


class ProjectNoteMessageHandler:
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
        await update.message.reply_text("Choose a project:", reply_markup=markup)
        return ProjectNoteState.PROJECT_CHOICE

    @classmethod
    async def choose_project(
        cls,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ):
        project = update.message.text
        if not Projects().has_project(project):
            await update.message.reply_text("No such project, try again")
            return ProjectNoteState.PROJECT_CHOICE

        context.user_data["project"] = project
        await update.message.reply_text(
            f"Write the note for the project: {project}",
            reply_markup=ReplyKeyboardRemove(),
        )
        return ProjectNoteState.PROJECT_NOTE_TYPING

    @classmethod
    async def add_note(
        cls,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        multiple_notes_mode: bool = False,
    ):
        project = context.user_data["project"]
        note = update.message.text
        try:
            Projects().add_note(
                ticket=project,
                note=note,
            )
        except Exception as e:
            print(e)
            await update.message.reply_text(f"Something went wrong")
            return ConversationHandler.END
        await update.message.reply_text(f"Note for project *{project}* saved ✅", parse_mode="Markdown")
        return ConversationHandler.END if not multiple_notes_mode else ProjectNoteState.PROJECT_NOTE_TYPING

    @classmethod
    def __pending_notes_to_text(
        cls,
        notes: list[ProjectNote],
    ):
        text = "Current pending notes\n\n"
        text += "\n\n".join([
            f"*Note*: {note.note}\n"
            f"*Created At*: {note.created_at}"
            for note in notes
        ])
        return text

    @classmethod
    async def get_pending_notes(
        cls,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ):
        project = update.message.text
        if not Projects().has_project(project):
            await update.message.reply_text("No such project, try again")
            return ProjectNoteState.PROJECT_CHOICE

        try:
            pending_notes = Projects().get_pending_notes(
                project_name=project,
            )
        except Exception as e:
            print(e)
            await update.message.reply_text(f"Something went wrong")
            return ProjectNoteState.PROJECT_CHOICE

        await update.message.reply_text(
            cls.__pending_notes_to_text(notes=pending_notes),
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

    # TODO: split into two classes to not overcomplicate this class
    @classmethod
    def get_handlers(cls) -> list:
        return [
            ConversationHandler(
                entry_points=[CommandHandler(BotCommandType.ADD_NOTE, cls.start_conversation)],
                states={
                    ProjectNoteState.PROJECT_CHOICE: [
                        MessageHandler(filters.TEXT & ~filters.COMMAND, cls.choose_project),
                    ],
                    ProjectNoteState.PROJECT_NOTE_TYPING: [
                        MessageHandler(filters.TEXT & ~filters.COMMAND, cls.add_note),
                    ],
                },
                fallbacks=[CommandHandler(BotCommandType.CANCEL, cls.cancel)],
            ),
            ConversationHandler(
                entry_points=[CommandHandler(BotCommandType.ADD_MULTIPLE_NOTES, cls.start_conversation)],
                states={
                    ProjectNoteState.PROJECT_CHOICE: [
                        MessageHandler(filters.TEXT & ~filters.COMMAND, cls.choose_project),
                    ],
                    ProjectNoteState.PROJECT_NOTE_TYPING: [
                        MessageHandler(filters.TEXT & ~filters.COMMAND, partial(cls.add_note, multiple_notes_mode=True)),
                    ],
                },
                fallbacks=[CommandHandler(BotCommandType.CANCEL, cls.cancel)],
            ),
            ConversationHandler(
                entry_points=[CommandHandler(BotCommandType.PENDING_NOTES, cls.start_conversation)],
                states={
                    ProjectNoteState.PROJECT_CHOICE: [
                        MessageHandler(filters.TEXT & ~filters.COMMAND, cls.get_pending_notes),
                    ],
                },
                fallbacks=[CommandHandler(BotCommandType.CANCEL, cls.cancel)],
            ),
        ]
