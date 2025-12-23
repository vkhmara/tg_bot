from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.constants import ParseMode
from telegram.ext import (
    CommandHandler,
    ConversationHandler,
    ContextTypes,
)
from enums.message_handlers.project import ProjectState
from enums.settings import BotCommandType
from exceptions.finish_conversation import FinishConversation
from message_handlers.base import BaseMessageHandler, state_handler
from services.project.project import get_all_project_labels, get_project


class DeleteProjectMessageHandler(BaseMessageHandler):
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
        return ProjectState.PROJECT_CHOICE

    @classmethod
    @state_handler
    async def __delete_project(
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
            return ProjectState.PROJECT_CHOICE

        db_project.is_deleted = True
        db_project.save_to_db()
        await update.message.reply_text(
            f"Project *{db_project.project_label}* was deleted",
            reply_markup=ReplyKeyboardRemove(),
            parse_mode=ParseMode.MARKDOWN,
        )
        return ConversationHandler.END

    @classmethod
    def get_handlers(cls) -> list:
        return [
            ConversationHandler(
                entry_points=[
                    CommandHandler(
                        BotCommandType.DELETE_PROJECT,
                        cls.__start_conversation,
                    )
                ],
                states={
                    ProjectState.PROJECT_CHOICE: [
                        cls._get_message_handler(cls.__delete_project),
                    ],
                },
                fallbacks=[CommandHandler(BotCommandType.CANCEL, cls._cancel)],
            ),
        ]
