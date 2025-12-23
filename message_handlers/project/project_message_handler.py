from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import (
    CommandHandler,
    ConversationHandler,
    ContextTypes,
)
from enums.message_handlers.project import ProjectState
from enums.settings import BotCommandType
from message_handlers.base import BaseMessageHandler, state_handler
from services.project.project import add_project


class ProjectMessageHandler(BaseMessageHandler):
    @classmethod
    @state_handler
    async def __start_conversation(
        cls,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ):
        await update.message.reply_text("Enter ticket:")
        return ProjectState.TICKET_NUMBER

    @classmethod
    @state_handler
    async def __enter_ticket_number(
        cls,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ):
        ticket_number = update.message.text
        context.user_data["ticket_number"] = ticket_number
        await update.message.reply_text("Enter ticket name:")
        return ProjectState.TICKET_NAME

    @classmethod
    @state_handler
    async def __enter_ticket_name(
        cls,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ):
        ticket_number = context.user_data["ticket_number"]
        ticket_name = update.message.text
        add_project(
            name=ticket_name,
            ticket=ticket_number,
        )
        await update.message.reply_text(
            f"New project *{ticket_name}* with ticket *{ticket_number}* saved ✅",
            parse_mode=ParseMode.MARKDOWN,
        )
        return ConversationHandler.END

    @classmethod
    def get_handlers(cls) -> list:
        return [
            ConversationHandler(
                entry_points=[
                    CommandHandler(
                        BotCommandType.ADD_PROJECT,
                        cls.__start_conversation,
                    )
                ],
                states={
                    ProjectState.TICKET_NUMBER: [
                        cls._get_message_handler(cls.__enter_ticket_number),
                    ],
                    ProjectState.TICKET_NAME: [
                        cls._get_message_handler(cls.__enter_ticket_name),
                    ],
                },
                fallbacks=[CommandHandler(BotCommandType.CANCEL, cls._cancel)],
            ),
        ]
