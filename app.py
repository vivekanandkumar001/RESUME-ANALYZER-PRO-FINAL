<<<<<<< HEAD
# app.py
import streamlit as st
import os
import urllib.parse
from utils import extract_text_from_file, save_edited_resume, load_json, save_json # JSON functions added
from model import get_job_matches, analyze_with_jd, get_recommendations
from chatbot_rag import get_rag_response, initialize_interview # Import chatbot functions
from pathlib import Path # Path ko import karein

# -------------------- PAGE CONFIG --------------------
st.set_page_config(
    page_title="Progeni - Smart Resume Analyzer",
    layout="wide",
    page_icon="https://raw.githubusercontent.com/vivekanandkumar001/RESUME-ANALYZER-PRO-FINAL/main/logo.png"
)

# --- GOOGLE SEARCH CONSOLE VERIFICATION ---
# Replace with your actual verification code
google_verification_tag = """
<meta name="google-site-verification" content="KOI_NAYA_SA_CODE_YAHAN_HOGA" />
"""
st.markdown(google_verification_tag, unsafe_allow_html=True)

# -------------------- CUSTOM CSS (HYDRANGEA TWILIGHT THEME) --------------------
st.markdown(
    """
    <style>
    /* Base Body Styling (Hydrangea Dark Gradient) */
    body {
        background: linear-gradient(135deg, #0f0c29 0%, #302b63 70%, #24243e 100%);
        background-attachment: fixed;
        color: #d1d1d1; /* Soft light grey text */
        font-family: 'Segoe UI', 'Roboto', sans-serif;
    }
    /* Main app container */
    .st-emotion-cache-16txtl3 { padding: 2rem 3rem; background: none; }
    [data-testid="stAppViewContainer"] > .main { background: none; }
    /* Card-like containers (Floating) */
    .card { background-color: #1e1c3a; border-radius: 12px; padding: 25px; box-shadow: 0 8px 24px rgba(0, 0, 0, 0.5); margin-bottom: 25px; border: 1px solid #4a476a; }
    /* Hide default Streamlit title/subheader */
    .st-emotion-cache-10trblm { display: none; }
    .st-emotion-cache-1q8du0e { display: none; }
    /* Progress Bar */
    .stProgress > div > div > div > div { background-color: #e5b2ca; }
    /* Text Area */
    .stTextArea textarea { background-color: #0f0c29; border-radius: 8px; border: 1px solid #4a476a; padding: 10px; color: #d1d1d1; }
    .stTextArea textarea:focus { border-color: #e5b2ca; box-shadow: 0 0 0 2px #5c4a55; outline: none; }
    /* Button Styling */
    .stButton>button { border-radius: 8px; background-color: #e5b2ca; color: #000000; padding: 0.6em 1.2em; font-weight: 700; border: none; transition: all 0.3s ease; box-shadow: 0 2px 4px rgba(0,0,0,0.4); width: 100%; }
    .stButton>button:hover { background-color: #ffffff; color: #cf9eb5; box-shadow: 0 4px 10px rgba(0,0,0,0.6); transform: translateY(-2px); }
    /* File Uploader */
    .stFileUploader { border: 2px dashed #e5b2ca; border-radius: 10px; padding: 1.5rem; background-color: #1e1c3a; }
    .stFileUploader label p { color: #adb5bd; }
    .stFileUploader [data-testid="stFileUploadDropzone"] button { color: #e5b2ca; border-color: #e5b2ca; }
    .stFileUploader [data-testid="stFileUploadDropzone"] button:hover { color: #000000; border-color: #e5b2ca; background-color: #e5b2ca; }
    /* Headers */
    h2 { border-bottom: 2px solid #4a476a; padding-bottom: 10px; color: #e5b2ca; font-weight: 600; }
    h3 { color: #ffffff; font-weight: 600; }
    /* Text */
    .card p, .card li, .stMarkdown p, .stMarkdown li, .card span { color: #d1d1d1; font-size: 1.05rem; line-height: 1.6; }
    .card strong, .stMarkdown strong { color: #ffffff; font-weight: 600; }
    /* Links */
    .card a { color: #e5b2ca; text-decoration: none; font-weight: 600; }
    .card a:hover { text-decoration: underline; color: #f0c9de; }
    /* Success Message */
    [data-testid="stAlert"][data-baseweb="alert"] > div:first-child { background-color: rgba(229, 178, 202, 0.1); color: #e5b2ca; border: 1px solid #e5b2ca; border-radius: 8px; }
    /* Style for chat messages */
    .stChatMessage { background-color: #1e1c3a; border: 1px solid #4a476a; border-radius: 8px; margin-bottom: 10px; padding: 10px 15px;}
    </style>
    """, unsafe_allow_html=True
)

# -------------------- APP TITLE (CUSTOM HTML) --------------------
LOGO_URL = "https://raw.githubusercontent.com/vivekanandkumar001/RESUME-ANALYZER-PRO-FINAL/main/logo.png"
st.markdown(
    f"""
    <div style="display: flex; align-items: center; justify-content: center; margin-bottom: 0px;">
        <img src="{LOGO_URL}" style="height: 60px; margin-right: 15px; border-radius: 50%;">
        <h1 style="font-size: 2.75rem; color: #ffffff; font-weight: 700; margin: 0;">
            Progeni: Smart Resume Analyzer
        </h1>
    </div>
    <p style="font-size: 1.15rem; color: #adb5bd; text-align: center; margin-bottom: 2rem;">
        Analyze resumes, practice interviews, and enhance your career readiness.
    </p>
    """,
    unsafe_allow_html=True
)

# -------------------- TAB SYSTEM --------------------
tab1, tab2 = st.tabs(["📊 Resume Analyzer", "🤖 AI Mock Interview"])

# -------------------------------------------------
# ----- TAB 1: RESUME ANALYZER -----
# -------------------------------------------------
with tab1:
    uploaded_resume_analyzer = st.file_uploader("📄 **Upload your Resume** (PDF, DOCX, or TXT)", type=["pdf", "docx", "txt"], key="resume_uploader_tab1")

    # Initialize specific_jd_text to None at the start of the tab
    specific_jd_text = None

    if uploaded_resume_analyzer:
        with st.spinner("Analyzing your resume... Please wait."):
            resume_text = extract_text_from_file(uploaded_resume_analyzer)
            job_matches = get_job_matches(resume_text) # Reads data_resume/jobs.json

            # Store resume text in session state for the interview tab
            st.session_state.resume_text_for_interview = resume_text

            if not job_matches:
                st.error("Error: Could not load job data. The 'data_resume/jobs.json' file might be empty or missing. Please ensure `scraper.py` ran successfully and generated the file.")
                st.stop()

            top_3_jobs = job_matches[:3]
            top_match = job_matches[0]
            top_match_title = top_match.get('title', 'N/A')
            top_match_description = top_match.get('description', '')

            # Analyze against the top match for General ATS score
            score, overlap, suggestions, missing_keywords = analyze_with_jd(resume_text, top_match_description)
            recommendations = get_recommendations(missing_keywords)

        st.progress(100)
        st.success("Analysis complete! See your results below.")

        # --- Card 1: Top 3 Job Matches ---
        with st.container(border=False):
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.write("## 🏆 Top 3 Job Matches")
            st.write("Based on your resume, these are the best matching job categories from our current data.")
            for i, job in enumerate(top_3_jobs):
                job_title = job.get('title', 'N/A')
                job_score = job.get('score', 0.0)
                st.subheader(f"{i+1}. {job_title} ({job_score*100:.2f}% Match)")
                query = urllib.parse.quote_plus(job_title)
                links = f"**Find this job on:** [LinkedIn](https://www.linkedin.com/jobs/search/?keywords={query}) | [Indeed](https://www.indeed.com/jobs?q={query}) | [Naukri](https://www.naukri.com/jobs-for-{job_title.lower().replace(' ', '-')}) | [Internshala](https://internshala.com/internships/keywords-{job_title.lower().replace(' ', '-')})"
                st.markdown(links)
                job_keywords = job.get('keywords', [])
                if job_keywords:
                    st.markdown(f"**Keywords:** {', '.join(job_keywords)}")
                if i < len(top_3_jobs) - 1: st.markdown("---")
            st.markdown('</div>', unsafe_allow_html=True)

        # --- CARD 2: GENERAL ATS ANALYSIS ---
        with st.container(border=False):
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.write(f"## 📊 General ATS Analysis (vs. '{top_match_title}')")
            st.info(f"Since no specific JD was uploaded, we analyzed your resume against your top match ('{top_match_title}').")
            st.write(f"### 🎯 General ATS Score: **{score*100:.2f}%**")
            st.progress(int(score * 100))
            if recommendations:
                st.write("### 🚀 ATS Enhancement Suggestions")
                st.write("Consider adding these skills/experiences to improve your match:")
                for reco in recommendations:
                    st.markdown(reco, unsafe_allow_html=True)
            else:
                st.success("Your resume seems well-aligned with this role type based on keywords!")
            with st.expander("📌 ATS Formatting Tips"):
                 st.markdown("""
                * **Fonts:** Use standard fonts (Arial, Calibri, Times New Roman). Size 10-12pt.
                * **Layout:** Use a single-column format. Avoid tables, columns, headers/footers.
                * **Headings:** Use standard section titles (e.g., "Work Experience", "Education", "Skills").
                * **Bullets:** Use simple round or square bullets.
                * **Keywords:** Naturally include keywords from job descriptions relevant to your target roles.
                * **File Type:** Save as PDF or DOCX, unless specified otherwise.
                """)
            st.markdown('</div>', unsafe_allow_html=True)

        # --- CARD 3: SPECIFIC JD COMPARISON ---
        with st.container(border=False):
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.write("## 📑 Compare with a Specific Job Description")
            st.write("Upload or paste a specific JD to get a precise match score and tailored suggestions.")
            jd_file = st.file_uploader("📋 Upload Specific Job Description", type=["pdf", "docx", "txt"], key="jd_uploader")
            jd_text_input = st.text_area("...or paste specific job description here:", height=200, key="jd_text")

            # Process JD only if uploaded or pasted
            if jd_file or jd_text_input:
                specific_jd_text = jd_text_input or extract_text_from_file(jd_file)
                if specific_jd_text: # Check if text was successfully extracted
                    with st.spinner("Comparing resume with specific JD..."):
                        s_score, s_overlap, s_suggestions, s_missing_keywords = analyze_with_jd(resume_text, specific_jd_text)
                        s_recommendations = get_recommendations(s_missing_keywords)

                    st.write(f"### 🎯 Specific Match Score: **{s_score*100:.2f}%**")
                    st.progress(int(s_score * 100))
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write("### ✅ Common Keywords Found:")
                        if s_overlap: st.markdown("<ul>" + "".join([f"<li>{kw}</li>" for kw in s_overlap]) + "</ul>", unsafe_allow_html=True)
                        else: st.write("None found.")
                    with col2:
                        st.write("### 💡 Keywords Missing/Not Prominent:")
                        if s_suggestions: st.markdown("<ul>" + "".join([f"<li>{s}</li>" for s in s_suggestions]) + "</ul>", unsafe_allow_html=True)
                        else: st.write("None found.")
                    if s_recommendations:
                        st.write("### 🚀 Enhancement Suggestions for This JD:")
                        for reco in s_recommendations:
                            st.markdown(reco, unsafe_allow_html=True)
                else:
                    st.warning("Could not extract text from the provided Job Description.")
            st.markdown('</div>', unsafe_allow_html=True)

        # --- CARD 4: RESUME EDITOR ---
        # Only show if a specific JD was provided and text was extracted
        if specific_jd_text:
            with st.container(border=False):
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.write("## ✏️ Resume Editor (Optimize for Specific JD)")
                st.write("Edit your resume text below to better match the specific job description, then re-analyze.")

                # Use a unique key for the text area if needed, otherwise rely on Streamlit's default handling
                edited_resume = st.text_area("Edit your resume text:", value=resume_text, height=350, key="resume_editor_area")

                col1, col2, col3 = st.columns(3)
                with col1:
                    reanalyze = st.button("🔁 Re-Analyze Edited Resume", key="reanalyze_button")
                with col2:
                    download_docx = st.button("💾 Download as DOCX", key="docx_button")
                with col3:
                    download_pdf = st.button("📥 Download as PDF", key="pdf_button")

                # Handle re-analysis button click
                if reanalyze:
                    with st.spinner("Reanalyzing edited resume..."):
                        # Use the text currently in the text_area for re-analysis
                        current_edited_text = st.session_state.resume_editor_area # Access text via key
                        new_score, new_overlap, new_suggestions, new_missing = analyze_with_jd(current_edited_text, specific_jd_text)
                    st.success(f"✅ New Match Score (Edited): **{new_score*100:.2f}%**")
                    st.progress(int(new_score * 100))
                    # Optionally display updated overlap/suggestions for the edited resume here

                # Handle download buttons (use text from session state)
                current_edited_text_for_download = st.session_state.resume_editor_area

                if download_docx:
                    file_path_docx = save_edited_resume(current_edited_text_for_download, format="docx")
                    if file_path_docx and os.path.exists(file_path_docx):
                        with open(file_path_docx, "rb") as fp_docx:
                            st.download_button(
                                label="⬇️ Download DOCX",
                                data=fp_docx,
                                file_name="updated_resume.docx",
                                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                            )
                        # Clean up the temp file after download button is generated
                        # os.remove(file_path_docx) # Be careful with cleanup, might interfere with download
                    else:
                        st.error("Failed to create DOCX file for download.")

                if download_pdf:
                    file_path_pdf = save_edited_resume(current_edited_text_for_download, format="pdf")
                    if file_path_pdf and os.path.exists(file_path_pdf):
                        with open(file_path_pdf, "rb") as fp_pdf:
                            st.download_button(
                                label="⬇️ Download PDF",
                                data=fp_pdf,
                                file_name="updated_resume.pdf",
                                mime="application/pdf"
                            )
                        # Clean up the temp file
                        # os.remove(file_path_pdf)
                    else:
                        st.error("Failed to create PDF file for download.")

                st.markdown('</div>', unsafe_allow_html=True)


# -------------------------------------------------
# ----- TAB 2: AI MOCK INTERVIEW -----
# -------------------------------------------------
with tab2:
    st.write("## 🤖 AI Mock Interview")

    # Check if resume text is available from Tab 1
    if 'resume_text_for_interview' not in st.session_state or not st.session_state.resume_text_for_interview:
        st.warning("Please upload your resume in the 'Resume Analyzer' tab first to start the interview.")
        st.stop() # Stop execution of this tab if no resume

    # Initialize chat history for the interview if it doesn't exist
    if "interview_messages" not in st.session_state:
        st.session_state.interview_messages = []
        print("Initializing interview message history.") # Debug print

    # Start interview only if history is empty (first time visiting tab after resume upload)
    if not st.session_state.interview_messages:
        print("Interview history empty, initializing...") # Debug print
        with st.spinner("Progeni AI is preparing your first question based on your resume..."):
            try:
                # Call the initialization function from chatbot_rag
                first_ai_message = initialize_interview(st.session_state.resume_text_for_interview)
                if first_ai_message:
                    st.session_state.interview_messages.append({"role": "assistant", "content": first_ai_message})
                    print("First AI message added to history.") # Debug print
                    # Use st.rerun() to immediately display the first message
                    st.rerun()
                else:
                    st.error("Could not start interview. AI failed to generate the first question.")
                    st.stop()
            except Exception as e:
                st.error(f"Error starting interview. Is Ollama running and model '{os.getenv('OLLAMA_MODEL', 'llama3')}' pulled? Details: {e}")
                st.stop()

    # Display chat messages from history
    # print(f"Displaying {len(st.session_state.interview_messages)} messages.") # Debug print
    for message in st.session_state.interview_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Get user input using chat_input
    if prompt := st.chat_input("Your Answer..."):
        print(f"User input received: {prompt}") # Debug print
        # Append and display user message immediately
        st.session_state.interview_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get AI response
        with st.chat_message("assistant"):
            message_placeholder = st.empty() # Placeholder for streaming/waiting
            message_placeholder.markdown("Thinking...")
            try:
                # Get response from chatbot logic
                # Pass only the latest prompt for simple context handling by Ollama
                ai_response = get_rag_response(prompt, "Candidate")

                if ai_response:
                     message_placeholder.markdown(ai_response) # Update placeholder with response
                     # Add AI response to history
                     st.session_state.interview_messages.append({"role": "assistant", "content": ai_response})
                     print("AI response added to history.") # Debug print
                else:
                     message_placeholder.error("AI failed to generate a response.")
                     # Optionally add an error message to history
                     # st.session_state.interview_messages.append({"role": "assistant", "content": "Sorry, I couldn't generate a response."})

            except Exception as e:
                error_msg = f"Error getting response. Is Ollama running? Details: {e}"
                print(error_msg) # Debug print
                message_placeholder.error(error_msg)
                # Optionally add error to history
                # st.session_state.interview_messages.append({"role": "assistant", "content": "Sorry, an error occurred."})

        # Rerun to clear the input box after processing
        # Note: Rerun can sometimes cause loops if not handled carefully, but useful here.
        # Consider removing if it causes issues.
        # st.rerun()
=======
import streamlit as st
from utils import extract_text_from_file, save_edited_resume
from model import get_job_matches, analyze_with_jd, get_course_suggestions
import os
import urllib.parse # Import for creating safe URL links

# -------------------- PAGE CONFIG --------------------
st.set_page_config(
    page_title="Progeni - Smart Resume Analyzer", 
    layout="wide",
    page_icon="https://raw.githubusercontent.com/vivekanandkumar001/RESUME-ANALYZER-PRO-FINAL/main/logo.png" 
)
# ---------------------------------------------------


# --- GOOGLE SEARCH CONSOLE VERIFICATION ---
# Google se copy kiya hua apna poora meta tag yahaan paste karein
google_verification_tag = """
<meta name="google-site-verification" content="KOI_NAYA_SA_CODE_YAHAN_HOGA" />
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
    
    /* Hide default Streamlit title */
    .st-emotion-cache-10trblm {
        display: none;
    }
    /* Hide default Streamlit subheader */
    .st-emotion-cache-1q8du0e {
        display: none;
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

# -------------------- APP TITLE (CUSTOM HTML) --------------------
LOGO_URL = "https://raw.githubusercontent.com/vivekanandkumar001/RESUME-ANALYZER-PRO-FINAL/main/logo.png"

st.markdown(
    f"""
    <div style="display: flex; align-items: center; justify-content: center; margin-bottom: 0px;">
        <img src="{LOGO_URL}" style="height: 60px; margin-right: 15px;">
        <h1 style="font-size: 2.75rem; color: #ffffff; font-weight: 700; margin: 0;">
            Progeni: Smart Resume Analyzer
        </h1>
    </div>
    <p style="font-size: 1.15rem; color: #adb5bd; text-align: center; margin-bottom: 2rem;">
        Upload your resume to instantly find matching jobs, get improvement tips, and edit your resume.
    </p>
    """,
    unsafe_allow_html=True
)
# ---------------------------------------------------


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
>>>>>>> 1513229e212edae69176b12f7d1ef905a471d922
