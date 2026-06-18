import pdfplumber
import re
import os


# STEP 1 → Extract text from PDF
def extract_text(pdf_path):
    text = ""

    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()

                if page_text:
                    text += page_text + "\n"

        return text

    except Exception as e:
        print("Error reading PDF:", e)
        return None


# STEP 2 → Clean extracted text
def clean_text(text):

    # remove extra spaces only
    text = re.sub(r' +', ' ', text)

    # preserve line breaks
    text = re.sub(r'\n+', '\n', text)

    text = re.sub(r'[^\x00-\x7F]+', ' ', text)

    return text.strip()


# STEP 3 → Detect important resume sections
def extract_section_content(text):

    headings = [
        "Academic Details",
        "Major Projects",
        "Other Projects",
        "Scholastic Achievements",
        "Computer Skills",
        "Relevant Courses",
        "Extra Curricular Activities"
    ]

    extracted = {}

    for i in range(len(headings)):

        start = headings[i]

        if i < len(headings) - 1:
            end = headings[i + 1]

            pattern = start + r"(.*?)" + end

        else:
            pattern = start + r"(.*)"

        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)

        if match:
            extracted[start] = match.group(1).strip()

    return extracted


# STEP 4 → Save output files
def save_output(cleaned_text, sections):

    os.makedirs("output", exist_ok=True)

    # Full cleaned resume
    with open("output/resume_cleaned.txt", "w", encoding="utf-8") as file:
        file.write(cleaned_text)

    # Structured sections
    with open("output/sections_extracted.txt", "w", encoding="utf-8") as file:

        for section, content in sections.items():

            file.write(f"{section}\n")
            file.write("-" * 40 + "\n")
            file.write(content)
            file.write("\n\n")


# STEP 5 → Main pipeline
def parse_resume(pdf_path):
    print("Reading PDF...")

    raw_text = extract_text(pdf_path)

    if raw_text is None:
        return

    print("Cleaning text...")

    cleaned_text = clean_text(raw_text)

    print("Detecting sections...")

    sections_data = extract_section_content(cleaned_text)

    save_output(cleaned_text, sections_data)

    for section, content in sections_data.items():
        print("\n", section)
        print(content[:300])   # show first 300 characters
      
   


# RUN PROGRAM
parse_resume("saurabhgupta.pdf")