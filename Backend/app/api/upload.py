from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.extract import extract_text_from_pdf

router = APIRouter(prefix="/api", tags=["Upload"])

@router.post("/upload-resume")
async def upload_resume(file: UploadFile = File(...)):
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF format is supported by MAVS Suite")
    
    try:
        contents = await file.read()
        extracted_text = extract_text_from_pdf(contents)
        
        if not extracted_text:
            raise HTTPException(status_code=422, detail="PDF file is empty or scannable image-only")
            
        return {
            "status": "Success",
            "filename": file.filename,
            "extracted_text": extracted_text
        }
    except ValueError as ve:
        raise HTTPException(status_code=422, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Parser Error: {str(e)}")