from flask import Flask, render_template, request
import PyPDF2
import re

app = Flask(__name__)

# ATS Skill Bank
SKILLS = [
    "python", "java", "html", "css", "javascript",
    "sql", "flask", "django", "react",
    "machine learning", "data analysis"
]

MANDATORY_SKILLS = ["python", "sql"]

# Interview Question Bank
INTERVIEW_QUESTIONS = {
    "python": [
        "Explain Python decorators with an example.",
        "Difference between list and tuple?",
        "Describe a Python project you built and challenges faced."
    ],
    "sql": [
        "Difference between WHERE and HAVING clause.",
        "What is normalization in databases?",
        "Write a SQL query to find the second highest salary."
    ],
    "flask": [
        "What is Flask Blueprint?",
        "How does Flask handle routing?",
        "Explain a Flask project you developed."
    ],
    "html": [
        "Difference between block and inline elements.",
        "What is semantic HTML?",
        "How did you structure HTML in your project?"
    ],
    "css": [
        "Difference between class and id selectors.",
        "What is Flexbox?",
        "How did you make your UI responsive?"
    ],
    "javascript": [
        "Difference between var, let and const.",
        "What is event bubbling?",
        "Explain a JavaScript feature used in your project."
    ]
}


def clean_text(text):
    text = text.lower()
    return re.sub(r"[^a-z0-9\s]", " ", text)


def extract_text_from_pdf(pdf_file):
    text = ""
    reader = PyPDF2.PdfReader(pdf_file)
    for page in reader.pages:
        if page.extract_text():
            text += page.extract_text() + " "
    return clean_text(text)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload():
    jd_text = clean_text(request.form["jd"])
    jd_skills = [skill for skill in SKILLS if skill in jd_text]

    results = []
    resumes = request.files.getlist("resume")

    for resume in resumes:
        resume_text = extract_text_from_pdf(resume)
        matched_skills = [skill for skill in jd_skills if skill in resume_text]

        percentage = round((len(matched_skills) / len(jd_skills)) * 100) if jd_skills else 0
        mandatory_ok = all(skill in resume_text for skill in MANDATORY_SKILLS)

        if mandatory_ok and percentage >= 60:
            decision = "Shortlisted for Interview ✅"
        elif mandatory_ok and percentage >= 40:
            decision = "Potential Candidate ⚠️"
        else:
            decision = "Rejected ❌"

        # Interview questions only for non-rejected candidates
        interview_questions = {}
        if decision != "Rejected ❌":
            for skill in matched_skills:
                if skill in INTERVIEW_QUESTIONS:
                    interview_questions[skill] = INTERVIEW_QUESTIONS[skill]

        results.append({
            "name": resume.filename,
            "percentage": percentage,
            "decision": decision,
            "matched": matched_skills,
            "questions": interview_questions
        })

    return render_template("result.html", results=results)


if __name__ == "__main__":
    app.run(debug=True)