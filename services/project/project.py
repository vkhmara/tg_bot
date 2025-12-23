from sqlalchemy import select
from sqlalchemy.orm import Session
from db.base import db_decorator
from db.models.project import Project
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
    is_deleted: bool = False,
    optional: bool = False,
) -> Project:
    custom_criterion = [
        ProjectFields.PROJECT_LABEL.contains(name),
    ]
    if is_deleted is not None:
        custom_criterion.append(
            Project.is_deleted.is_(True)
            if is_deleted
            else Project.is_deleted.isnot(True)
        )
    return Project.filter(
        db=db,
        optional=optional,
        custom_criterion=custom_criterion,
    )


@db_decorator
def get_all_project_labels(db: Session) -> list[str]:
    select_query = (
        select(
            ProjectFields.PROJECT_LABEL.label("project_label"),
        )
        .select_from(Project)
        .filter(Project.is_deleted.is_not(True))
        .order_by(Project.created_date.desc())
    )
    result = db.execute(select_query).all()
    return [x.project_label for x in result]
