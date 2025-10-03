from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.constants import ParseMode
from telegram.ext import (
    CommandHandler,
    ConversationHandler,
    ContextTypes,
)
from enums.message_handlers.add_project_note import ProjectNoteState
from exceptions.finish_conversation import FinishConversation
from functools import partial
from enums.settings import BotCommandType
from message_handlers.base import BaseMessageHandler, state_handler
from services.project.project import get_all_project_labels, get_project
from services.project.project_note import add_project_note


class AddProjectNoteMessageHandler(BaseMessageHandler):
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
            [[project_label] for project_label in all_projects_labels],
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
    async def __choose_project(
        cls,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ):
        project = update.message.text
        db_project = get_project(
            name=project,
            optional=True,
        )
        if not db_project:
            await update.message.reply_text("No such project🔪, try again")
            return ProjectNoteState.PROJECT_CHOICE

        context.user_data["project"] = {
            "id": db_project.id,
            "project_label": db_project.project_label,
        }
        await update.message.reply_text(
            f"Write the note for the project\n*{db_project.project_label}*",
            reply_markup=ReplyKeyboardRemove(),
            parse_mode=ParseMode.MARKDOWN,
        )
        return ProjectNoteState.PROJECT_NOTE_TYPING

    @classmethod
    @state_handler
    async def __add_note(
        cls,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        multiple_notes_mode: bool = False,
    ):
        project = context.user_data["project"]
        project_id = project.get("id")
        project_label = project.get("project_label")

        note = update.message.text
        add_project_note(
            project_id=project_id,
            note=note,
        )
        await update.message.reply_text(
            f"Note for project *{project_label}* saved ✅",
            parse_mode=ParseMode.MARKDOWN,
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
                        cls.__start_conversation,
                    )
                ],
                states={
                    ProjectNoteState.PROJECT_CHOICE: [
                        cls._get_message_handler(cls.__choose_project),
                    ],
                    ProjectNoteState.PROJECT_NOTE_TYPING: [
                        cls._get_message_handler(cls.__add_note),
                    ],
                },
                fallbacks=[CommandHandler(BotCommandType.CANCEL, cls._cancel)],
            ),
            ConversationHandler(
                entry_points=[
                    CommandHandler(
                        BotCommandType.ADD_MULTIPLE_NOTES,
                        cls.__start_conversation,
                    )
                ],
                states={
                    ProjectNoteState.PROJECT_CHOICE: [
                        cls._get_message_handler(cls.__choose_project),
                    ],
                    ProjectNoteState.PROJECT_NOTE_TYPING: [
                        cls._get_message_handler(
                            partial(
                                cls.__add_note,
                                multiple_notes_mode=True,
                            ),
                        ),
                    ],
                },
                fallbacks=[CommandHandler(BotCommandType.CANCEL, cls._cancel)],
            ),
        ]
