from sqlalchemy import Boolean, Column, Integer, String, Text, JSON
from db.base_model import Base


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    ticket = Column(String(20), nullable=False)
    comment = Column(Text)
    extra_info = Column(JSON)
    is_deleted = Column(Boolean, default=False)

    @property
    def project_label(self):
        return f"[{self.ticket}]: {self.name}"
