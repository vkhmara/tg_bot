from enum import Enum
from telegram import Update, ReplyKeyboardRemove
from telegram.ext import (
    CommandHandler, MessageHandler, ConversationHandler,
    ContextTypes, filters
)
from services.excel.excel import Projects
from enums.settings import BotCommandType


class ProjectState(str, Enum):
    TICKET_NUMBER = "ticket_number"
    TICKET_NAME = "ticket_name"


class ProjectMessageHandler:
    @classmethod
    async def start_conversation(
        cls,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ):
        await update.message.reply_text("Enter ticket:")
        return ProjectState.TICKET_NUMBER

    @classmethod
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
    async def enter_ticket_name(
        cls,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ):
        ticket_number = context.user_data["ticket_number"]
        ticket_name = update.message.text
        try:
            Projects().add_project(
                ticket=ticket_number,
                ticket_name=ticket_name,
            )
        except Exception as e:
            print(e)
            await update.message.reply_text("Something went wrong")
            return ConversationHandler.END
        await update.message.reply_text(
            f"New project *{ticket_name}* with ticket *{ticket_number}* saved ✅",
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
                entry_points=[CommandHandler(BotCommandType.ADD_PROJECT, cls.start_conversation)],
                states={
                    ProjectState.TICKET_NUMBER: [
                        MessageHandler(filters.TEXT & ~filters.COMMAND, cls.enter_ticket_number),
                    ],
                    ProjectState.TICKET_NAME: [
                        MessageHandler(filters.TEXT & ~filters.COMMAND, cls.enter_ticket_name),
                    ],
                },
                fallbacks=[CommandHandler(BotCommandType.CANCEL, cls.cancel)],
            ),
        ]
