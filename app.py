import streamlit as st
from utils import extract_text_from_file, save_edited_resume
from model import get_job_matches, analyze_with_jd, get_course_suggestions
import os
import urllib.parse # Import for creating safe URL links

# -------------------- PAGE CONFIG --------------------
st.set_page_config(
    page_title="Smart Resume Analyzer 🧠",
    layout="wide",
    page_icon="🧠"
)

# --- GOOGLE SEARCH CONSOLE VERIFICATION ---
# Google se copy kiya hua apna poora meta tag yahaan paste karein
google_verification_tag = """
<meta name="google-site-verification" content="_hMaRXQjxX-9p5fcd2fXqq0pnZgI8J-1U3j29avVOgE" />
"""
st.markdown(google_verification_tag, unsafe_allow_html=True)
# ------------------------------------------


# -------------------- CUSTOM CSS (HYDRANGEA TWILIGHT THEME) --------------------
st.markdown(
    """
    <style>
    /* Base Body Styling (Hydrangea Dark Gradient) */
    body {
        /* Deep Blue to Dark Purple/Pink Gradient */
        background: linear-gradient(135deg, #0f0c29 0%, #302b63 70%, #24243e 100%);
        background-attachment: fixed;
        color: #d1d1d1; /* Soft light grey text */
        font-family: 'Segoe UI', 'Roboto', sans-serif;
    }
    
    /* Main app container */
    .st-emotion-cache-16txtl3 {
        padding: 2rem 3rem;
        background: none; 
    }
    
    /* Override Streamlit's main app background */
    [data-testid="stAppViewContainer"] > .main {
        background: none;
    }

    /* Card-like containers (Floating) */
    .card {
        background-color: #1e1c3a; /* Solid dark purple/blue */
        border-radius: 12px;
        padding: 25px;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.5);
        margin-bottom: 25px;
        border: 1px solid #4a476a; /* Lighter purple border */
    }
    
    /* Title and Subheader */
    .st-emotion-cache-10trblm { /* Main title */
        font-size: 2.75rem;
        color: #ffffff;
        font-weight: 700;
        text-align: center;
    }
    .st-emotion-cache-1q8du0e { /* Subheader */
        font-size: 1.15rem;
        color: #adb5bd;
        text-align: center;
        margin-bottom: 2rem;
    }

    /* Progress Bar */
    .stProgress > div > div > div > div {
        background-color: #e5b2ca; /* Hydrangea Pink/Lavender Accent */
    }

    /* Text Area */
    .stTextArea textarea {
        background-color: #0f0c29;
        border-radius: 8px;
        border: 1px solid #4a476a;
        padding: 10px;
        color: #d1d1d1;
    }
    .stTextArea textarea:focus {
        border-color: #e5b2ca;
        box-shadow: 0 0 0 2px #5c4a55;
        outline: none;
    }

    /* Button Styling (Hydrangea Pink) */
    .stButton>button {
        border-radius: 8px;
        background-color: #e5b2ca; /* Pink Accent */
        color: #000000; /* Black text for high contrast */
        padding: 0.6em 1.2em;
        font-weight: 700;
        border: none;
        transition: all 0.3s ease;
        box-shadow: 0 2px 4px rgba(0,0,0,0.4);
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #ffffff; /* White on hover */
        color: #cf9eb5; /* Pink text on hover */
        box-shadow: 0 4px 10px rgba(0,0,0,0.6);
        transform: translateY(-2px);
    }
    .stButton>button:focus {
        outline: none;
        box-shadow: 0 0 0 3px #5c4a55;
    }

    /* File Uploader */
    .stFileUploader {
        border: 2px dashed #e5b2ca;
        border-radius: 10px;
        padding: 1.5rem;
        background-color: #1e1c3a;
    }
    .stFileUploader label p { color: #adb5bd; }
    .stFileUploader [data-testid="stFileUploadDropzone"] button {
        color: #e5b2ca;
        border-color: #e5b2ca;
    }
    .stFileUploader [data-testid="stFileUploadDropzone"] button:hover {
        color: #000000;
        border-color: #e5b2ca;
        background-color: #e5b2ca;
    }
    
    /* --- TEXT COLOR IMPROVEMENTS (INSIDE CARDS) --- */
    
    h2 { /* Card Headers */
        border-bottom: 2px solid #4a476a;
        padding-bottom: 10px;
        color: #e5b2ca; /* Pink Accent */
        font-weight: 600;
    }
    
    h3 { /* Sub-Headers */
        color: #ffffff;
        font-weight: 600;
    }
    
    .card p, .card li, .stMarkdown p, .stMarkdown li, .card span {
        color: #d1d1d1;
        font-size: 1.05rem;
        line-height: 1.6;
    }

    .card strong, .stMarkdown strong {
        color: #ffffff;
        font-weight: 600;
    }
    
    .card a { /* Links */
        color: #e5b2ca;
        text-decoration: none;
        font-weight: 600;
    }
    .card a:hover {
        text-decoration: underline;
        color: #f0c9de; /* Lighter on hover */
    }
    
    /* Theme-matched Success Message */
    [data-testid="stAlert"][data-baseweb="alert"] > div:first-child {
        background-color: rgba(229, 178, 202, 0.1); /* Transparent pink */
        color: #e5b2ca;
        border: 1px solid #e5b2ca;
        border-radius: 8px;
    }

    </style>
    """, unsafe_allow_html=True
)

# -------------------- APP TITLE --------------------
st.title("🧠 Smart Resume Analyzer & Job Matcher")
st.subheader("Upload your resume to instantly find matching jobs, get improvement tips, and edit your resume.")

# -------------------- FILE UPLOAD --------------------
uploaded_resume = st.file_uploader("📄 **Upload your Resume** (PDF, DOCX, or TXT)", type=["pdf", "docx", "txt"])

if uploaded_resume:
    with st.spinner("Analyzing your resume... Please wait."):
        resume_text = extract_text_from_file(uploaded_resume)
        job_matches = get_job_matches(resume_text)
        top_3_jobs = job_matches[:3]

    st.progress(100)
    st.success("Analysis complete! See your top job matches below.")

    # --- Card 1: Top 3 Job Matches ---
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.write("## 🏆 Top 3 Job Matches")
        st.write("Here are the best job categories from our database, with links to search for live roles.")
        
        for i, job in enumerate(top_3_jobs):
            st.subheader(f"{i+1}. {job['title']} ({job['score']*100:.2f}% Match)")
            
            query = urllib.parse.quote_plus(job['title'])
            links = f"""
            **Find this job on:**
            [LinkedIn](https://www.linkedin.com/jobs/search/?keywords={query}) | 
            [Indeed](https://www.indeed.com/jobs?q={query}) | 
            [Naukri](https://www.naukri.com/jobs-for-{job['title'].lower().replace(' ', '-')}) | 
            [Internshala](https://internshala.com/internships/keywords-{job['title'].lower().replace(' ', '-')})
            """
            st.markdown(links)
            
            st.markdown(f"**Keywords from this job:** {', '.join(job['keywords'])}")
            if i < 2: # Add a divider line
                st.markdown("---")
        
        st.markdown('</div>', unsafe_allow_html=True)


    # --- Card 2: Job Description Comparison ---
    with st.container():
        st.markdown('<div class="card">', unsafe_allow_html=True) 
        st.write("## 📑 Compare with a Specific Job Description")
        jd_file = st.file_uploader("📋 Upload Job Description", type=["pdf", "docx", "txt"], key="jd_uploader")
        jd_text_input = st.text_area("...or paste job description here:", height=200, key="jd_text")

        if jd_file or jd_text_input:
            jd_text = jd_text_input or extract_text_from_file(jd_file)

            with st.spinner("Comparing resume with job description..."):
                score, overlap, suggestions, missing_keywords = analyze_with_jd(resume_text, jd_text)

            st.write(f"### 🎯 Match Probability: **{score*100:.2f}%**")
            st.progress(int(score * 100))

            col1, col2 = st.columns(2)
            with col1:
                st.write("### 🧩 Common Keywords:")
                st.markdown("<ul>" + "".join([f"<li>{kw}</li>" for kw in overlap]) + "</ul>", unsafe_allow_html=True)
            
            with col2:
                st.write("### 💡 Missing Keywords/Skills Suggestions:")
                st.markdown("<ul>" + "".join([f"<li>{s}</li>" for s in suggestions]) + "</ul>", unsafe_allow_html=True)

            # --- Course Suggestions (Sub-section) ---
            course_suggestions = get_course_suggestions(missing_keywords)
            if course_suggestions:
                st.write("### 🎓 Suggested Courses & Certificates")
                st.markdown("<ul>" + "".join([f"<li>{s}</li>" for s in course_suggestions]) + "</ul>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # --- Card 3: Resume Editor & Templates ---
    if jd_file or jd_text_input: # Only show editor if a JD is provided
        with st.container():
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.write("## ✏️ Edit & Improve Your Resume")
            st.write("You can edit your resume text here and re-analyze it against the job description.")
            
            # --- Resume Templates (Sub-section) ---
            with st.expander("🎨 Looking for Professional Resume Templates?"):
                st.info("After editing your text, we recommend using a dedicated platform to make it look professional.")
                st.markdown("""
                * [Canva Resume Templates](https://www.canva.com/resumes/templates/)
                * [Zety Resume Builder](https://zety.com/)
                * [Resume.com](https://www.resume.com/resume-templates)
                """)
            
            edited_resume = st.text_area("Edit your resume text below:", resume_text, height=350, key="resume_editor")

            col1, col2, col3 = st.columns(3)
            with col1:
                reanalyze = st.button("🔁 Re-Analyze")
            with col2:
                download_docx = st.button("💾 Download as DOCX")
            with col3:
                download_pdf = st.button("📥 Download as PDF")

            if reanalyze:
                with st.spinner("Reanalyzing edited resume..."):
                    new_score, new_overlap, new_suggestions, new_missing = analyze_with_jd(edited_resume, jd_text)
                st.success(f"✅ New Match Probability: **{new_score*100:.2f}%**")
                st.progress(int(new_score * 100))
                
                col1_re, col2_re = st.columns(2)
                with col1_re:
                    st.write("### 🔍 Updated Keyword Overlap:")
                    st.markdown("<ul>" + "".join([f"<li>{kw}</li>" for kw in new_overlap]) + "</ul>", unsafe_allow_html=True)
                with col2_re:
                    st.write("### 💡 Updated Improvement Suggestions:")
                    st.markdown("<ul>" + "".join([f"<li>{s}</li>" for s in new_suggestions]) + "</ul>", unsafe_allow_html=True)

            if download_docx:
                file_path = save_edited_resume(edited_resume, format="docx")
                with open(file_path, "rb") as f:
                    st.download_button("⬇️ Download Updated Resume (DOCX)", f, file_name="updated_resume.docx")

            if download_pdf:
                file_path = save_edited_resume(edited_resume, format="pdf")
                with open(file_path, "rb") as f:
                    st.download_button("⬇️ Download Updated Resume (PDF)", f, file_name="updated_resume.pdf")
            
            st.markdown('</div>', unsafe_allow_html=True)