from enum import Enum


class BotCommandType(str, Enum):
    ADD_MULTIPLE_NOTES = "add_multiple_notes"
    ADD_NOTE = "add_note"
    ADD_PROJECT = "add_project"
    CANCEL = "cancel"
    HELP = "help"
    PENDING_NOTES = "pending_notes"
    RESOLVE_NOTE = "resolve_note"
