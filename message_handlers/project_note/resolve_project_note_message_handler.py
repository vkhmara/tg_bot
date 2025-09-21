from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
    ReplyKeyboardMarkup,
)
from telegram.constants import ParseMode
from telegram.ext import (
    CommandHandler,
    ConversationHandler,
    ContextTypes,
    CallbackQueryHandler,
)
from enums.message_handlers.resolve_project_note import ResolveProjectNoteState
from enums.project_note import ProjectNoteStatus
from exceptions.finish_conversation import FinishConversation
from enums.settings import BotCommandType
from message_handlers.base import BaseMessageHandler, state_handler
from services.project.project import get_all_project_labels, get_project
from services.project.project_note import (
    get_project_notes,
    get_project_notes_result,
    update_project_note,
)


class ResolveProjectNoteMessageHandler(BaseMessageHandler):
    @classmethod
    @state_handler
    async def __start_conversation(
        cls,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ):
        all_projects_labels = get_all_project_labels()
        if not all_projects_labels:
            raise FinishConversation("Project list is empty")
        markup = ReplyKeyboardMarkup(
            [[project_label] for project_label in all_projects_labels],
            resize_keyboard=True,
            one_time_keyboard=True,
        )
        await update.message.reply_text(
            "Choose a project:",
            reply_markup=markup,
        )
        return ResolveProjectNoteState.PROJECT_CHOICE

    @classmethod
    @state_handler
    async def __choose_project(
        cls,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ):
        project = update.message.text
        db_project = get_project(
            name=project,
            optional=True,
        )
        if not db_project:
            await update.message.reply_text("No such project🔪, try again")
            return ResolveProjectNoteState.PROJECT_CHOICE

        pending_project_notes = get_project_notes(
            project_id=db_project.id,
            project_note_status=ProjectNoteStatus.PENDING,
        )
        if not pending_project_notes:
            raise FinishConversation("No notes for the project 🤲")

        context.user_data["project"] = project
        markup = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text=project_note.note,
                        callback_data=project_note.id,
                    )
                ]
                for project_note in pending_project_notes
            ],
        )
        await update.message.reply_text(
            f"Choose the note for the project: {project}",
            reply_markup=markup,
        )
        return ResolveProjectNoteState.PROJECT_NOTE_SELECTING

    @classmethod
    @state_handler
    async def __resolve_note(
        cls,
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
    ):
        query = update.callback_query
        await query.answer()
        await query.edit_message_reply_markup(reply_markup=None)

        project_note_id = query.data
        update_project_note(
            project_note_id=project_note_id,
            payload={
                "status": ProjectNoteStatus.RESOLVED,
            },
        )

        await query.message.reply_text(
            "The note was marked as resolved ✅",
            parse_mode=ParseMode.MARKDOWN_V2,
        )
        return ConversationHandler.END

    @classmethod
    def get_handlers(cls) -> list:
        return [
            ConversationHandler(
                entry_points=[
                    CommandHandler(
                        BotCommandType.RESOLVE_NOTE,
                        cls.__start_conversation,
                    )
                ],
                states={
                    ResolveProjectNoteState.PROJECT_CHOICE: [
                        cls._get_message_handler(cls.__choose_project),
                    ],
                    ResolveProjectNoteState.PROJECT_NOTE_SELECTING: [
                        # cls._get_message_handler(cls.__resolve_note),
                        CallbackQueryHandler(cls.__resolve_note)
                    ],
                },
                fallbacks=[CommandHandler(BotCommandType.CANCEL, cls._cancel)],
            ),
        ]
