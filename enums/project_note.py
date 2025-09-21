from enum import Enum


class ProjectNoteStatus(str, Enum):
    PENDING = "pending"
    RESOLVED = "resolved"
