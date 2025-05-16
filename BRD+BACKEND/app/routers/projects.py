from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models, schemas, auth

router = APIRouter()

@router.post("/group/{group_id}", response_model=schemas.ProjectOut)
def create_project(group_id: int, project: schemas.ProjectCreate, db: Session = Depends(auth.get_db), current_user: models.User = Depends(auth.get_current_user)):
    group = db.query(models.Group).filter(models.Group.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    if current_user not in group.members:
        raise HTTPException(status_code=403, detail="Not a member of this group")

    new_project = models.Project(
        name=project.name,
        description=project.description,
        group_id=group_id,
        created_by=current_user.id
    )
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    return new_project

@router.get("/group/{group_id}", response_model=list[schemas.ProjectOut])
def list_projects(group_id: int, db: Session = Depends(auth.get_db), current_user: models.User = Depends(auth.get_current_user)):
    group = db.query(models.Group).filter(models.Group.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    if current_user not in group.members:
        raise HTTPException(status_code=403, detail="Not a member of this group")

    projects = db.query(models.Project).filter(models.Project.group_id == group_id).all()
    return projects

@router.delete("/{project_id}")
def delete_project(project_id: int, db: Session = Depends(auth.get_db), current_user: models.User = Depends(auth.get_current_user)):
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this project")

    db.delete(project)
    db.commit()
    return {"message": "Project deleted successfully"}
