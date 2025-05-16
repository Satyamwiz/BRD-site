from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import models, schemas, auth

router = APIRouter()

@router.post("/", response_model=schemas.GroupOut)
def create_group(group: schemas.GroupCreate, db: Session = Depends(auth.get_db), current_user: models.User = Depends(auth.get_current_user)):
    new_group = models.Group(name=group.name, created_by=current_user.id)
    new_group.members.append(current_user)  # auto-add creator as member
    db.add(new_group)
    db.commit()
    db.refresh(new_group)
    return new_group

@router.post("/{group_id}/join")
def join_group(group_id: int, db: Session = Depends(auth.get_db), current_user: models.User = Depends(auth.get_current_user)):
    group = db.query(models.Group).filter(models.Group.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    if current_user in group.members:
        raise HTTPException(status_code=400, detail="Already a member")

    group.members.append(current_user)
    db.commit()
    return {"message": "Joined group successfully"}

@router.get("/my", response_model=list[schemas.GroupOut])
def my_groups(db: Session = Depends(auth.get_db), current_user: models.User = Depends(auth.get_current_user)):
    return current_user.groups


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
