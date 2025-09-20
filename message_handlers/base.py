from telegram import Update, ReplyKeyboardRemove
from telegram.ext import (
    ConversationHandler,
    ContextTypes,
    MessageHandler,
    filters,
)
from functools import wraps
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
            print(e)
            await update.message.reply_text(
                f"Something went wrong",
                reply_markup=ReplyKeyboardRemove(),
            )
            return ConversationHandler.END

    return wrapped


class BaseMessageHandler:
    @classmethod
    def get_message_handler(
        cls,
        state_handler,
    ):
        return MessageHandler(
            filters=filters.TEXT & ~filters.COMMAND,
            callback=state_handler,
        )

    @classmethod
    async def cancel(
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
