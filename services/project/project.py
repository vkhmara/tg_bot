from sqlalchemy import select
from sqlalchemy.orm import Session
from databases.base import db_decorator
from databases.models.project import Project
from enums.project import ProjectFields


@db_decorator
def add_project(
    db: Session,
    name: str,
    ticket: str,
):
    Project(
        name=name,
        ticket=ticket,
    ).save_to_db(db=db)


@db_decorator
def get_project(
    db: Session,
    name: str,
    optional: bool = False,
) -> Project:
    return Project.filter(
        db=db,
        optional=optional,
        custom_criterion=[
            ProjectFields.PROJECT_LABEL.contains(name),
        ],
    )


@db_decorator
def get_all_project_labels(db: Session) -> list[str]:
    select_query = select(
        ProjectFields.PROJECT_LABEL.label("project_label"),
    ).select_from(Project)
    result = db.execute(select_query).all()
    return [x.project_label for x in result]
