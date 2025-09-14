from enum import Enum
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application, CommandHandler, MessageHandler, ConversationHandler,
    ContextTypes, filters
)
from services.excel.excel import Projects


class State(Enum):
	PROJECT_CHOICE = "project_choice"
	PROJECT_NOTE_TYPING = "project_note_typing"


class ProjectNoteMessageHandler:
	async def start_conversation(
		self,
		update: Update,
		context: ContextTypes.DEFAULT_TYPE,
	):
		all_projects_names = Projects().get_all_project_sheetnames()
		if not all_projects_names:
			await update.message.reply_text("Project list is empty")
			return ConversationHandler.END
		markup = ReplyKeyboardMarkup(
			[
				[project_name]
				for project_name in all_projects_names
			],
			resize_keyboard=True,
			one_time_keyboard=True,
		)
		await update.message.reply_text("Choose a project:", reply_markup=markup)
		return State.PROJECT_CHOICE

	async def choose_project(
		self,
		update: Update,
		context: ContextTypes.DEFAULT_TYPE,
	):
		project = update.message.text
		if not Projects().has_project(project):
			await update.message.reply_text("No such project, try again")
			return State.PROJECT_CHOICE

		context.user_data["project"] = project
		await update.message.reply_text(
			f"Write the note for the project: {project}",
			reply_markup=ReplyKeyboardRemove(),
		)
		return State.PROJECT_NOTE_TYPING

	async def add_note(
		self,
		update: Update,
		context: ContextTypes.DEFAULT_TYPE,
	):
		project = context.user_data["project"]
		note = update.message.text
		try:
			Projects().add_note(
		        ticket=project,
		        note=note,
			)
		except Exception as e:
			print(e)
			await update.message.reply_text(f"Something went wrong")
			return ConversationHandler.END
		await update.message.reply_text(f"Note for project *{project}* saved ✅", parse_mode="Markdown")
		return ConversationHandler.END

	async def cancel(
		self,
		update: Update,
		context: ContextTypes.DEFAULT_TYPE,
	):
	    await update.message.reply_text("Operation cancelled", reply_markup=ReplyKeyboardRemove())
	    return ConversationHandler.END
