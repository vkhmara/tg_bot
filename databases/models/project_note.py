from sqlalchemy import Column, Integer, String, Text, ForeignKey, JSON
from databases.base_model import Base
from enums.project_note import ProjectNoteStatus


class ProjectNote(Base):
    __tablename__ = "project_notes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    note = Column(Text)
    status = Column(String(30), default=ProjectNoteStatus.PENDING)
    extra_info = Column(JSON)
