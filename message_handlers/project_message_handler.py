from enum import Enum
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application, CommandHandler, MessageHandler, ConversationHandler,
    ContextTypes, filters
)
from services.excel.excel import Projects


class State(Enum):
	TICKET_NUMBER = "ticket_number"
	TICKET_NAME = "ticket_name"


class ProjectMessageHandler:
	async def start_conversation(
		self,
		update: Update,
		context: ContextTypes.DEFAULT_TYPE,
	):
		await update.message.reply_text("Enter ticket:")
		return State.TICKET_NUMBER

	async def enter_ticket_number(
		self,
		update: Update,
		context: ContextTypes.DEFAULT_TYPE,
	):
		ticket_number = update.message.text
		context.user_data["ticket_number"] = ticket_number
		await update.message.reply_text("Enter ticket name:")
		return State.TICKET_NAME

	async def enter_ticket_name(
		self,
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
			await update.message.reply_text(f"Something went wrong")
			return ConversationHandler.END
		await update.message.reply_text(
			f"New project *{ticket_name}* with ticket *{ticket_number}* saved ✅",
			parse_mode="Markdown",
		)
		return ConversationHandler.END

	async def cancel(
		self,
		update: Update,
		context: ContextTypes.DEFAULT_TYPE,
	):
	    await update.message.reply_text("Operation cancelled", reply_markup=ReplyKeyboardRemove())
	    return ConversationHandler.END
