import asyncio
from telegram.ext import Application
from message_handlers import get_all_message_handlers
from message_handlers.base import set_commands
from utilities.list import join_lists


def main(token: str):
    message_handlers = get_all_message_handlers()
    app: Application = Application.builder().token(token).build()

    app.add_handlers(
        join_lists(
            message_handler.get_handlers() for message_handler in message_handlers
        )
    )
    asyncio.get_event_loop().run_until_complete(set_commands(app))
    # TODO: investigate why this causes the error
    # asyncio.run(set_commands(app))

    app.run_polling()


if __name__ == "__main__":
    with open("tg_token.txt", "r") as f:
        token = f.read().strip()
    main(token=token)
