from databases.base import db_decorator
from databases.models.project import Project
from databases.models.project_note import ProjectNote
from enums.project import ProjectFields
from pydantic_models.services.project import ProjectNotesResult
from sqlalchemy import select, desc
from sqlalchemy.orm import Session
from services.project.project import get_project


@db_decorator
def get_project_notes(
    db: Session,
    project_id: int = None,
    project_note_status: str = None,
) -> list[ProjectNote]:
    return ProjectNote.filter(
        db=db,
        many=True,
        project_id=project_id,
        status=project_note_status,
    )


@db_decorator
def get_project_notes_result(
    db: Session,
    project_id: int = None,
    project_note_status: str = None,
) -> ProjectNotesResult:
    criterion = [ProjectNote.status == project_note_status]
    if project_id is not None:
        criterion.append(Project.id == project_id)

    select_query = (
        select(
            ProjectNote.id,
            ProjectNote.note,
            ProjectNote.status,
            ProjectFields.PROJECT_LABEL.label("project_label"),
            ProjectNote.created_date,
        )
        .select_from(ProjectNote)
        .join(
            Project,
            ProjectNote.project_id == Project.id,
        )
        .where(*criterion)
        .order_by(desc(ProjectNote.created_date))
    )
    result = db.execute(select_query).all()
    return ProjectNotesResult(data=result)


@db_decorator
def add_project_note(
    db: Session,
    note: str,
    project_id: int = None,
    project: str = None,
):
    if project_id is None:
        if project is None:
            raise Exception("Either proejct_id or project must be provided")
        db_project = get_project(
            db=db,
            name=project,
        )
        project_id = db_project.id
    ProjectNote(
        project_id=project_id,
        note=note,
    ).save_to_db(db=db)


@db_decorator
def update_project_note(
    db: Session,
    project_note_id: int,
    payload: dict,
):
    db_project_note = ProjectNote.filter(
        db=db,
        id=project_note_id,
    )
    for field, value in payload.items():
        setattr(db_project_note, field, value)
    db_project_note.save_to_db(db=db)
