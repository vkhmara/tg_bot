from enum import Enum
from telegram import Update
from telegram.ext import (
    CommandHandler,
    ConversationHandler,
    ContextTypes,
)
from services.excel.excel import Projects
from enums.settings import BotCommandType
from message_handlers.base import BaseMessageHandler, state_handler


class ProjectState(str, Enum):
    TICKET_NUMBER = "ticket_number"
    TICKET_NAME = "ticket_name"


class ProjectMessageHandler(BaseMessageHandler):
    @classmethod
    @state_handler
    async def start_conversation(
        cls,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ):
        await update.message.reply_text("Enter ticket:")
        return ProjectState.TICKET_NUMBER

    @classmethod
    @state_handler
    async def enter_ticket_number(
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
    async def enter_ticket_name(
        cls,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ):
        ticket_number = context.user_data["ticket_number"]
        ticket_name = update.message.text
        Projects().add_project(
            ticket=ticket_number,
            ticket_name=ticket_name,
        )
        await update.message.reply_text(
            f"New project *{ticket_name}* with ticket *{ticket_number}* saved ✅",
            parse_mode="Markdown",
        )
        return ConversationHandler.END

    @classmethod
    def get_handlers(cls) -> list:
        return [
            ConversationHandler(
                entry_points=[
                    CommandHandler(
                        BotCommandType.ADD_PROJECT,
                        cls.start_conversation,
                    )
                ],
                states={
                    ProjectState.TICKET_NUMBER: [
                        cls.get_message_handler(cls.enter_ticket_number),
                    ],
                    ProjectState.TICKET_NAME: [
                        cls.get_message_handler(cls.enter_ticket_name),
                    ],
                },
                fallbacks=[CommandHandler(BotCommandType.CANCEL, cls.cancel)],
            ),
        ]
