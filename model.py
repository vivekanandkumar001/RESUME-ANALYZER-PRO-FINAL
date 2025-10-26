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