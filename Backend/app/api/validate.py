from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from database import get_db
import models
from app.services.agents import run_mavs_pipeline
from pydantic import BaseModel
import json

router = APIRouter(prefix="/api", tags=["Validation"])

class ValidationPayload(BaseModel):
    candidate_name: str
    jd_title: str
    resume_text: str
    jd_text: str

@router.post("/validate")
def process_mavs_agents(payload: ValidationPayload, db: Session = Depends(get_db)):
    try:
        db_jd = models.JobDescription(
            title=payload.jd_title,
            jd_text=payload.jd_text
        )
        db_candidate = models.Candidate(
            name=payload.candidate_name,
            resume_text=payload.resume_text
        )
        db.add(db_jd)
        db.add(db_candidate)
        db.commit()
        
        ai_report = run_mavs_pipeline(
            resume_content=payload.resume_text,
            jd_content=payload.jd_text
        )
        
        if ai_report["status"] == "Success":
            db_candidate.generated_questions = json.dumps(ai_report["mavs_report"])
            db.commit()
            return ai_report
        else:
            db.rollback()
            raise HTTPException(status_code=500, detail=ai_report)
            
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"MAVS Pipeline Error: {str(e)}")