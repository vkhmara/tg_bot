from sqlalchemy import func
from db.models.project import Project


class ProjectFields:
    PROJECT_LABEL = func.concat("[", Project.ticket, "]: ", Project.name)
