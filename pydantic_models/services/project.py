from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
from enums.project_note import ProjectNoteStatus
from utilities.datetime import datetime_to_text


class ProjectNoteResult(BaseModel):
    id: int
    note: Optional[str]
    status: ProjectNoteStatus
    project_label: Optional[str]
    created_date: datetime

    class Config:
        validate_by_name = True
        from_attributes = True
        arbitrary_types_allowed = True

    # TODO: probably move to another file/class/method to store
    #  all such methods in one place without spreading
    @property
    def tg_text(self):
        return (
            f"<u>{self.note}</u>\n"
            f"⏰ <code>{datetime_to_text(self.created_date)}</code>\n"
            "--------"
        )


class ProjectNotesResult(BaseModel):
    data: List[ProjectNoteResult]
