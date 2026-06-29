import io
import pypdf

def extract_text_from_pdf(file_bytes: bytes) -> str:
    """
    Extracts text content cleanly from raw document upload bytes.
    """
    try:
        pdf_file = io.BytesIO(file_bytes)
        reader = pypdf.PdfReader(pdf_file)
        text_accumulator = []
        
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text_accumulator.append(page_text)
                
        return "\n".join(text_accumulator).strip()
    except Exception as e:
        raise ValueError(f"Failed to parse PDF document payload matrix: {str(e)}")