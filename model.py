
from sentence_transformers import SentenceTransformer, util
import json
import os

model = SentenceTransformer("all-MiniLM-L6-v2")

# ----- NEW SUPERCHARGED RECOMMENDATIONS -----
skill_recommendations = {
    "python": {
        "course": "Coursera: Python for Everybody",
        "certificate": "Google's Python Automation Certificate",
        "project": "Ek 'Personal Expense Tracker' CLI app banayein."
    },
    "machine learning": {
        "course": "Coursera: Machine Learning by Andrew Ng",
        "certificate": "TensorFlow Developer Certificate",
        "project": "Titanic dataset par prediction model banayein."
    },
    "deep learning": {
        "course": "DeepLearning.AI TensorFlow Developer",
        "certificate": "DeepLearning.AI Specialization",
        "project": "Ek 'Image Classifier' (Cat vs Dog) banayein."
    },
    "react": {
        "course": "Udemy: React - The Complete Guide",
        "certificate": "Meta Front-End Developer Certificate",
        "project": "Ek 'To-Do List' app banayein React ka istemaal karke."
    },
    "data analysis": {
        "course": "Google Data Analytics Professional Certificate",
        "certificate": "Google Data Analytics Professional Certificate",
        "project": "Ek COVID-19 dataset ka analysis karein aur charts banayein."
    },
    "aws": {
        "course": "AWS Certified Solutions Architect - Associate",
        "certificate": "AWS Certified Solutions Architect - Associate",
        "project": "Ek simple web app ko AWS (S3, EC2) par deploy karein."
    },
    "sql": {
        "course": "Udemy: The Complete SQL Bootcamp",
        "certificate": "Oracle SQL (1Z0-071) ya Microsoft's MTA 98-364",
        "project": "Ek online store ka sample database design karein."
    }
}
# -----------------------------------------------

def get_job_matches(resume_text):
    """
    Calculates cosine similarity for all jobs and returns a sorted list.
    """
    jobs_path = os.path.join("data_resume", "jobs.json")
    
    try:
        with open(jobs_path, "r", encoding="utf-8") as f:
            jobs = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return [] # Agar file na mile ya khaali ho toh empty list return karein

    job_scores = []
    resume_emb = model.encode(resume_text, convert_to_tensor=True)

    for job in jobs:
        desc = job.get("description", "")
        job_emb = model.encode(desc, convert_to_tensor=True)
        score = float(util.pytorch_cos_sim(resume_emb, job_emb))
        
        job_scores.append({
            "title": job.get("title", "No Title"),
            "score": score,
            "keywords": job.get("keywords", []),
            "description": desc
        })

    # Sort jobs by score in descending order
    sorted_jobs = sorted(job_scores, key=lambda x: x["score"], reverse=True)
    return sorted_jobs

def analyze_with_jd(resume_text, jd_text):
    resume_emb = model.encode(resume_text, convert_to_tensor=True)
    jd_emb = model.encode(jd_text, convert_to_tensor=True)
    score = float(util.pytorch_cos_sim(resume_emb, jd_emb))

    resume_words = set(resume_text.lower().split())
    jd_words = set(jd_text.lower().split())
    overlap = list(jd_words.intersection(resume_words))
    
    # These are the "missing skills"
    missing_keywords = [word for word in jd_words - resume_words if len(word) > 3 and word.isalpha()]
    suggestions = [f"Consider adding or highlighting experience with: '{word}'" for word in missing_keywords]

    return score, overlap[:10], suggestions[:10], missing_keywords

# ----- NEW FUNCTION -----
def get_recommendations(missing_keywords):
    """
    Maps missing keywords to courses, certificates, and projects.
    """
    mapped = []
    found_skills = set()
    
    for keyword in missing_keywords:
        keyword = keyword.lower()
        if keyword in skill_recommendations and keyword not in found_skills:
            reco = skill_recommendations[keyword]
            mapped.append(f"""
            **{keyword.title()}** (Yeh skill aapke resume mein missing hai):
            * **🎓 Course:** {reco['course']}
            * **📜 Certificate:** {reco['certificate']}
            * **💡 Project Idea:** {reco['project']}
            """)
            found_skills.add(keyword)
    
    return mapped
# ------------------------

from sentence_transformers import SentenceTransformer, util
import json
import os

model = SentenceTransformer("all-MiniLM-L6-v2")

# Map skills to recommended courses
# You can expand this list with more skills and certificates!
skill_courses = {
    "python": "Coursera Python for Everybody",
    "machine learning": "Coursera Machine learning by Andrew Ng",
    "deep learning": "DeepLearning.AI TensorFlow Developer",
    "react": "Udemy React - The Complete Guide",
    "data analysis": "Google Data Analytics Professional Certificate",
    "cloud": "AWS Certified Solutions Architect",
    "ai": "IBM AI Engineering Professional Certificate",
    "aws": "AWS Certified Solutions Architect",
    "sql": "Udemy The Complete SQL Bootcamp",
    "project management": "Google Project Management Professional Certificate"
}

def get_job_matches(resume_text):
    """
    Calculates cosine similarity for all jobs and returns a sorted list.
    """
    jobs_path = os.path.join("data", "jobs.json")
    with open(jobs_path, "r", encoding="utf-8") as f:
        jobs = json.load(f)

    job_scores = []
    resume_emb = model.encode(resume_text, convert_to_tensor=True)

    for job in jobs:
        desc = job["description"]
        job_emb = model.encode(desc, convert_to_tensor=True)
        score = float(util.pytorch_cos_sim(resume_emb, job_emb))
        job_scores.append({
            "title": job["title"],
            "score": score,
            "keywords": job.get("keywords", [])
        })

    # Sort jobs by score in descending order
    sorted_jobs = sorted(job_scores, key=lambda x: x["score"], reverse=True)
    return sorted_jobs

def analyze_with_jd(resume_text, jd_text):
    resume_emb = model.encode(resume_text, convert_to_tensor=True)
    jd_emb = model.encode(jd_text, convert_to_tensor=True)
    score = float(util.pytorch_cos_sim(resume_emb, jd_emb))

    resume_words = set(resume_text.lower().split())
    jd_words = set(jd_text.lower().split())
    overlap = list(jd_words.intersection(resume_words))
    
    # These are the "missing skills"
    missing_keywords = [word for word in jd_words - resume_words if len(word) > 3 and word.isalpha()]
    suggestions = [f"Consider adding or highlighting experience with: '{word}'" for word in missing_keywords]

    return score, overlap[:10], suggestions[:10], missing_keywords

def get_course_suggestions(missing_keywords):
    """
    Maps missing keywords to courses and certificates.
    """
    mapped = []
    found_skills = set()
    
    for keyword in missing_keywords:
        for skill, course in skill_courses.items():
            if skill == keyword and skill not in found_skills:
                mapped.append(f"For **{skill}**: {course}")
                found_skills.add(skill)
    return mapped
