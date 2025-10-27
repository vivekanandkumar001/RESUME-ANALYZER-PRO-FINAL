# app.py
import streamlit as st
import os
import urllib.parse
from pathlib import Path

# --- NOW Import other modules ---
# Ensure these files are clean and present
from utils import extract_text_from_file, save_edited_resume, load_json, save_json
from model import get_job_matches, analyze_with_jd, get_recommendations
from chatbot_rag import get_rag_response, initialize_interview 
# ------------------------------

# -------------------- PAGE CONFIG (MUST BE FIRST ST COMMAND) --------------------
st.set_page_config(
    page_title="Progeni - Smart Resume Analyzer",
    layout="wide",
    page_icon="https://raw.githubusercontent.com/vivekanandkumar001/RESUME-ANALYZER-PRO-FINAL/main/logo.png"
)
# --------------------------------------------------------------------------------

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

    specific_jd_text = None
    
    # Initialize flag for interview readiness
    if 'resume_ready' not in st.session_state:
        st.session_state.resume_ready = False

    if uploaded_resume_analyzer:
        with st.spinner("Analyzing your resume... Please wait."):
            resume_text = extract_text_from_file(uploaded_resume_analyzer)
            
            # --- VALIDATION CHECK (Crucial for interview start) ---
            if not resume_text or len(resume_text.strip()) < 50:
                 st.error("Could not read enough text from the resume (file might be image-based or empty). Please check file format.")
                 st.session_state.resume_ready = False # Set flag to False if validation fails
                 st.stop() # Stop execution after error display
            
            job_matches = get_job_matches(resume_text) # Reads data_resume/jobs.json

            # Store resume text and set flag to True
            st.session_state.resume_text_for_interview = resume_text
            st.session_state.resume_ready = True # Set flag to True only on successful read

            if not job_matches:
                st.error("Error: Could not load job data. The 'data_resume/jobs.json' file might be empty or missing. Please ensure `scraper.py` ran successfully and generated the file.")
                st.stop()

            top_3_jobs = job_matches[:3]
            top_match = job_matches[0]
            top_match_title = top_match.get('title', 'N/A')
            top_match_description = top_match.get('description', '')

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
                        current_edited_text = st.session_state.resume_editor_area
                        new_score, new_overlap, new_suggestions, new_missing = analyze_with_jd(current_edited_text, specific_jd_text)
                    st.success(f"✅ New Match Score (Edited): **{new_score*100:.2f}%**")
                    st.progress(int(new_score * 100))

                # Handle download buttons (use text from session state)
                current_edited_text_for_download = st.session_state.get("resume_editor_area", resume_text)

                if download_docx:
                    file_path_docx = save_edited_resume(current_edited_text_for_download, format="docx")
                    if file_path_docx and os.path.exists(file_path_docx):
                        with open(file_path_docx, "rb") as fp_docx:
                            st.download_button(
                                label="⬇️ Download DOCX",
                                data=fp_docx,
                                file_name="updated_resume.docx",
                                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                key="download_docx_btn"
                            )
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
                                mime="application/pdf",
                                key="download_pdf_btn"
                            )
                    else:
                        st.error("Failed to create PDF file for download.")

                st.markdown('</div>', unsafe_allow_html=True)


# -------------------------------------------------
# ----- TAB 2: AI MOCK INTERVIEW -----
# -------------------------------------------------
with tab2:
    st.write("## 🤖 AI Mock Interview")

    # Check if resume text is available AND VALID from Tab 1
    if not st.session_state.get('resume_ready', False):
        st.warning("Please upload a valid, readable resume in the 'Resume Analyzer' tab first to start the interview.")
        st.stop()

    # Initialize chat history for the interview if it doesn't exist
    if "interview_messages" not in st.session_state:
        st.session_state.interview_messages = []

    # Start interview only if history is empty
    if not st.session_state.interview_messages:
        # Add a placeholder while the first question is generated
        st.session_state.interview_messages.append({"role": "assistant", "content": "Initializing interview..."})
        try:
            # Call the initialization function from chatbot_rag
            resume_text = st.session_state.resume_text_for_interview
            first_ai_message = initialize_interview(resume_text)
            
            if first_ai_message:
                # Replace placeholder with actual first message
                st.session_state.interview_messages[0] = {"role": "assistant", "content": first_ai_message}
                st.rerun()
            else:
                st.session_state.interview_messages[0] = {"role": "assistant", "content": "Error: AI failed to generate the first question (Empty Response)."}
                st.error("Could not start interview. AI failed to generate the first question.")
        except Exception as e:
            # This handles errors from load_llm_model (missing key)
            st.error(f"Error starting interview. Please check your GitHub Secrets for the GEMINI_API_KEY. Details: {e}")
            st.stop()


    # Display chat messages from history
    for message in st.session_state.interview_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Get user input using chat_input
    if prompt := st.chat_input("Your Answer..."):
        # Append user message immediately
        st.session_state.interview_messages.append({"role": "user", "content": prompt})
        st.rerun() # Rerun to display user message and trigger AI response logic

    # If the last message is from the user, get AI response
    if st.session_state.interview_messages and st.session_state.interview_messages[-1]["role"] == "user":
        user_prompt_for_ai = st.session_state.interview_messages[-1]["content"]
        with st.chat_message("assistant"):
            message_placeholder = st.empty() # Placeholder for streaming/waiting
            message_placeholder.markdown("Thinking...")
            try:
                # Get response from chatbot logic
                ai_response = get_rag_response(user_prompt_for_ai, "Candidate")

                if ai_response:
                     message_placeholder.markdown(ai_response) # Update placeholder with response
                     # Add AI response to history
                     st.session_state.interview_messages.append({"role": "assistant", "content": ai_response})
                     st.rerun() # Rerun to clear the input box and update display cleanly
                else:
                     message_placeholder.error("AI failed to generate a response.")
                     st.session_state.interview_messages.append({"role": "assistant", "content": "Sorry, I couldn't generate a response."})

            except Exception as e:
                error_msg = f"Error getting response: {e}"
                print(error_msg)
                message_placeholder.error(error_msg)
                st.session_state.interview_messages.append({"role": "assistant", "content": "Sorry, an error occurred while getting the response."})