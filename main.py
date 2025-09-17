import asyncio
from telegram.ext import Application
from message_handlers.project_message_handler import ProjectMessageHandler
from message_handlers.project_note_message_handler import ProjectNoteMessageHandler
from message_handlers.resolve_project_note_message_handler import ResolveProjectNoteMessageHandler
from message_handlers.bot_handler import GeneralBotHandler


def main(token: str):
    app: Application = Application.builder().token(token).build()

    app.add_handlers(
        [
            *GeneralBotHandler.get_handlers(),
            *ProjectNoteMessageHandler.get_handlers(),
            *ProjectMessageHandler.get_handlers(),
            *ResolveProjectNoteMessageHandler.get_handlers(),
        ]
    )
    asyncio.get_event_loop().run_until_complete(GeneralBotHandler.set_commands(app))
    # TODO: investigate why this causes the error
    # asyncio.run(GeneralBotHandler.set_commands(app))

    app.run_polling()


if __name__ == "__main__":
    with open("tg_token.txt", "r") as f:
        token = f.read().strip()
    main(token=token)
