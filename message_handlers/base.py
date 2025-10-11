import traceback
from functools import wraps
from telegram import BotCommand, Update, ReplyKeyboardRemove
from telegram.constants import ParseMode
from telegram.ext import (
    ConversationHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
from enums.settings import BotCommandType
from exceptions.finish_conversation import FinishConversation


def state_handler(func):
    @wraps(func)
    async def wrapped(
        cls,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        *args,
        **kwargs,
    ):
        try:
            return await func(cls, update, context, *args, **kwargs)
        except FinishConversation as e:
            await update.message.reply_text(
                str(e),
                reply_markup=ReplyKeyboardRemove(),
            )
            return ConversationHandler.END
        except Exception as e:
            traceback.print_exc()
            await update.message.reply_text(
                f"Something went wrong||\n{e}||",
                reply_markup=ReplyKeyboardRemove(),
                parse_mode=ParseMode.MARKDOWN_V2,
            )
            return ConversationHandler.END

    return wrapped


class BaseMessageHandler:
    @classmethod
    def _get_message_handler(
        cls,
        state_handler,
    ):
        return MessageHandler(
            filters=filters.TEXT & ~filters.COMMAND,
            callback=state_handler,
        )

    @classmethod
    async def _cancel(
        cls,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ):
        await update.message.reply_text(
            "Operation cancelled",
            reply_markup=ReplyKeyboardRemove(),
        )
        return ConversationHandler.END

    @classmethod
    def get_handlers(cls) -> list:
        raise NotImplementedError


async def set_commands(app):
    command_descriptions = {
        BotCommandType.ADD_PROJECT: "Add project",
        BotCommandType.ADD_NOTE: "Add project note",
        BotCommandType.ADD_MULTIPLE_NOTES: "Add multiple notes for a project",
        BotCommandType.HELP: "Help",
        BotCommandType.CANCEL: "Cancel conversation",
        BotCommandType.PENDING_NOTES: "Pending project notes",
        BotCommandType.RESOLVE_NOTE: "Mark note as resolved",
        BotCommandType.SCHEDULE_JOBS: "Subscribe on pending notes notifications",
    }
    commands = [
        BotCommand(
            command=command_type,
            description=command_descriptions.get(
                command_type,
                "TODO: provide description",
            ),
        )
        for command_type in BotCommandType
    ]
    await app.bot.set_my_commands(commands)
