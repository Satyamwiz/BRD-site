from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
import json
import tempfile
import os
from fastapi.responses import FileResponse
from app import models, auth
from app.v2_logic import (
    BRDInput,
    process_brd,
    generate_final_brd,
    create_brd_word_document
)

router = APIRouter()

@router.post("/generate-initial")
async def generate_initial_brd(
    project_id: int = Form(...),
    prompt: str = Form(...),
    template: Optional[UploadFile] = File(None),
    db: Session = Depends(auth.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if current_user not in project.group.members:
        raise HTTPException(status_code=403, detail="Access denied")

    docs = db.query(models.Document).filter(models.Document.project_id == project_id).all()
    combined_summary = "\n\n".join([
        f"Document: {doc.summary_title or doc.filename}\n{doc.summary_description or ''}"
        for doc in docs
    ])

    template_bytes = await template.read() if template else b""

    # Store template and prompt for reuse in final
    project.prompt = prompt
    project.template_bytes = template_bytes
    db.commit()

    brd_input = BRDInput(
        prompt=f"{prompt}\n\nAnalyze the following summaries:\n{combined_summary}",
        template=template_bytes,
        support_documents=[]
    )

    result = process_brd(brd_input)

    return {
        "reworded_summary": result["reworded_summary"],
        "completion_suggestions": result["completion_suggestions"],
        "brd_draft": result["brd_draft"]
    }
@router.post("/generate-final")
async def generate_brd_final(
    project_id: int = Form(...),
    prompt: str = Form(...),
    completion_answers: Optional[str] = Form("{}"),
    template: Optional[UploadFile] = File(None),  # Optional to allow reuse of previously uploaded
    db: Session = Depends(auth.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if current_user not in project.group.members:
        raise HTTPException(status_code=403, detail="Access denied")

    # Collect previously uploaded document summaries
    docs = db.query(models.Document).filter(models.Document.project_id == project_id).all()
    combined_summary = "\n\n".join([
        f"Document: {doc.summary_title or doc.filename}\n{doc.summary_description or ''}"
        for doc in docs
    ])

    # Read template if provided
    template_bytes = await template.read() if template else b""

    brd_input = BRDInput(
        prompt=f"{prompt}\n\nAnalyze the following summaries:\n{combined_summary}",
        template=template_bytes,
        support_documents=[]
    )

    final_result = generate_final_brd(
        brd_input=brd_input,
        completion_answers=json.loads(completion_answers),
        reworded_summary=f"{prompt}\n\n{combined_summary}"
    )

    return {
        "brd_document": final_result["brd_document"],
        "review_feedback": final_result["review_feedback"]
    }
    
@router.get("/download")
def download_brd_docx(
    project_id: int,
    db: Session = Depends(auth.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if current_user not in project.group.members:
        raise HTTPException(status_code=403, detail="Access denied")

    docs = db.query(models.Document).filter(models.Document.project_id == project_id).all()
    combined_summary = "\n\n".join([
        f"Document: {doc.summary_title or doc.filename}\n{doc.summary_description or ''}"
        for doc in docs
    ])

    docx_text = f"Business Requirements Document for Project: {project.name}\n\n{combined_summary}"

    with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
        create_brd_word_document(docx_text, tmp.name)
        temp_path = tmp.name

    filename = f"BRD_{project.name.replace(' ', '_')}.docx"
    return FileResponse(
        temp_path,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename=filename
    )
