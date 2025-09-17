from telegram import Update, BotCommand
from telegram.ext import ContextTypes, CommandHandler
from enums.settings import BotCommandType


class GeneralBotHandler:
    @classmethod
    async def help_command(
        cls,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ):
        text = "\n".join([
            f"/{command_type} - {command_type.replace("_", " ")}"
            for command_type in BotCommandType
        ])
        await update.message.reply_text(text)

    # TODO: maybe move to another file/class
    @classmethod
    async def set_commands(cls, app):
        command_descriptions = {
            BotCommandType.ADD_PROJECT: "Add project",
            BotCommandType.ADD_NOTE: "Add project note",
            BotCommandType.ADD_MULTIPLE_NOTES: "Add multiple notes for a project",
            BotCommandType.HELP: "Help",
            BotCommandType.CANCEL: "Cancel conversation",
        }
        commands = [
            BotCommand(
                command=command_type,
                description=command_descriptions.get(command_type, "TODO: provide description")
            )
            for command_type in BotCommandType
        ]
        await app.bot.set_my_commands(commands)

    @classmethod
    def get_handlers(cls) -> list:
        return [
            CommandHandler(BotCommandType.HELP, cls.help_command),
        ]
