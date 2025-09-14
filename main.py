import asyncio
import os
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, BotCommand
from telegram.ext import (
    Application, CommandHandler, MessageHandler, ConversationHandler,
    ContextTypes, filters
)
from message_handlers.project_message_handler import (
	ProjectMessageHandler,
	State as ProjectState,
)
from message_handlers.project_note_message_handler import (
	ProjectNoteMessageHandler,
	State as ProjectNoteState,
)


TOKEN = "8348316463:AAGd3hDSSkCIBz_y66erFlW3Br58CrXw9RI"


async def help_command(
	update: Update,
	context: ContextTypes.DEFAULT_TYPE,
):
    text = (
        "/add_project – add project\n"
        "/add_note – add project note\n"
        "/help – all the commands\n"
        "/cancel – cancel the current conversation"
    )
    await update.message.reply_text(text)


async def set_commands(app):
    commands = [
        BotCommand("add_project", "Add project"),
        BotCommand("add_note", "Add project note"),
        BotCommand("help", "Help"),
        BotCommand("cancel", "Cancel conversation"),
    ]
    await app.bot.set_my_commands(commands)


def main():
	app: Application = Application.builder().token(TOKEN).build()

	app.add_handler(CommandHandler("help", help_command))

	project_note_message_handler = ProjectNoteMessageHandler()
	app.add_handlers([
		ConversationHandler(
			entry_points=[CommandHandler("add_note", project_note_message_handler.start_conversation)],
			states={
				ProjectNoteState.PROJECT_CHOICE: [
					MessageHandler(filters.TEXT & ~filters.COMMAND, project_note_message_handler.choose_project),
				],
				ProjectNoteState.PROJECT_NOTE_TYPING: [
					MessageHandler(filters.TEXT & ~filters.COMMAND, project_note_message_handler.add_note),
				],
			},
			fallbacks=[CommandHandler("cancel", project_note_message_handler.cancel)],
		),
	])

	project_message_handler = ProjectMessageHandler()
	app.add_handlers([
		ConversationHandler(
			entry_points=[CommandHandler("add_project", project_message_handler.start_conversation)],
			states={
				ProjectState.TICKET_NUMBER: [
					MessageHandler(filters.TEXT & ~filters.COMMAND, project_message_handler.enter_ticket_number),
				],
				ProjectState.TICKET_NAME: [
					MessageHandler(filters.TEXT & ~filters.COMMAND, project_message_handler.enter_ticket_name),
				],
			},
			fallbacks=[CommandHandler("cancel", project_message_handler.cancel)],
		),
	])
	asyncio.get_event_loop().run_until_complete(set_commands(app))

	app.run_polling()

if __name__ == "__main__":
	main()
