from flask import Flask, render_template, request
import PyPDF2
import re

app = Flask(__name__)

# Master skill bank (ATS skills)
SKILLS = [
    "python", "java", "html", "css", "javascript",
    "sql", "flask", "django", "react",
    "machine learning", "data analysis"
]

# Mandatory skills
MANDATORY_SKILLS = ["python", "sql"]


def clean_text(text):
    """
    Normalize text for better matching
    """
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return text


def extract_text_from_pdf(pdf_file):
    """
    Extract text from PDF safely
    """
    text = ""
    reader = PyPDF2.PdfReader(pdf_file)
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + " "
    return clean_text(text)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload():
    jd_text = clean_text(request.form["jd"])

    # Skills found in JD
    jd_skills = [skill for skill in SKILLS if skill in jd_text]

    results = []
    resumes = request.files.getlist("resume")

    for resume in resumes:
        resume_text = extract_text_from_pdf(resume)

        # Skill matching
        matched_skills = [skill for skill in jd_skills if skill in resume_text]

        # Match percentage
        if jd_skills:
            percentage = round((len(matched_skills) / len(jd_skills)) * 100)
        else:
            percentage = 0

        # Mandatory skill check
        mandatory_ok = all(skill in resume_text for skill in MANDATORY_SKILLS)

        # Decision logic (FIXED)
        if mandatory_ok and percentage >= 60:
            decision = "Shortlisted for Interview ✅"
        elif mandatory_ok and percentage >= 40:
            decision = "Potential Candidate ⚠️"
        else:
            decision = "Rejected ❌"

        results.append({
            "name": resume.filename,
            "percentage": percentage,
            "decision": decision,
            "matched": matched_skills
        })

    return render_template("result.html", results=results)


if __name__ == "__main__":
    app.run(debug=True)