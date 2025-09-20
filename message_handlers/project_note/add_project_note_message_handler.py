from enum import Enum
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    CommandHandler,
    ConversationHandler,
    ContextTypes,
)
from exceptions.finish_conversation import FinishConversation
from services.excel.excel import Projects
from functools import partial
from enums.settings import BotCommandType
from message_handlers.base import BaseMessageHandler, state_handler


class ProjectNoteState(str, Enum):
    PROJECT_CHOICE = "project_choice"
    PROJECT_NOTE_TYPING = "project_note_typing"


class AddProjectNoteMessageHandler(BaseMessageHandler):
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
    @state_handler
    async def choose_project(
        cls,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ):
        project = update.message.text
        if not Projects().has_project(project):
            await update.message.reply_text("No such project🔪, try again")
            return ProjectNoteState.PROJECT_CHOICE

        context.user_data["project"] = project
        await update.message.reply_text(
            f"Write the note for the project: {project}",
            reply_markup=ReplyKeyboardRemove(),
        )
        return ProjectNoteState.PROJECT_NOTE_TYPING

    @classmethod
    @state_handler
    async def add_note(
        cls,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        multiple_notes_mode: bool = False,
    ):
        project = context.user_data["project"]
        note = update.message.text
        Projects().add_note(
            ticket=project,
            note=note,
        )
        await update.message.reply_text(
            f"Note for project *{project}* saved ✅", parse_mode="Markdown"
        )
        return (
            ConversationHandler.END
            if not multiple_notes_mode
            else ProjectNoteState.PROJECT_NOTE_TYPING
        )

    @classmethod
    def get_handlers(cls) -> list:
        return [
            ConversationHandler(
                entry_points=[
                    CommandHandler(
                        BotCommandType.ADD_NOTE,
                        cls.start_conversation,
                    )
                ],
                states={
                    ProjectNoteState.PROJECT_CHOICE: [
                        cls.get_message_handler(cls.choose_project),
                    ],
                    ProjectNoteState.PROJECT_NOTE_TYPING: [
                        cls.get_message_handler(cls.add_note),
                    ],
                },
                fallbacks=[CommandHandler(BotCommandType.CANCEL, cls.cancel)],
            ),
            ConversationHandler(
                entry_points=[
                    CommandHandler(
                        BotCommandType.ADD_MULTIPLE_NOTES,
                        cls.start_conversation,
                    )
                ],
                states={
                    ProjectNoteState.PROJECT_CHOICE: [
                        cls.get_message_handler(cls.choose_project),
                    ],
                    ProjectNoteState.PROJECT_NOTE_TYPING: [
                        cls.get_message_handler(
                            partial(
                                cls.add_note,
                                multiple_notes_mode=True,
                            ),
                        ),
                    ],
                },
                fallbacks=[CommandHandler(BotCommandType.CANCEL, cls.cancel)],
            ),
        ]
