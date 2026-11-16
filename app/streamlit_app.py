import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import tempfile
import streamlit as st

from app.tools.pdf_reader import extract_pdf_text
from app.workflow.graph import paperpilot_workflow
from app.models.paper_analysis import PaperAnalysis, PaperReview
from app.services.report_generator import (
    generate_markdown_report,
    save_markdown_report,
)
from app.services.pdf_generator import generate_pdf_report


# =========================================================
# CONFIGURATION
# =========================================================

OUTPUT_DIR = Path(r"D:\PaperPilot-AI\outputs")

st.set_page_config(
    page_title="PaperPilot Atlas | Research Intelligence",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================
# SESSION STATE
# =========================================================

if "analysis" not in st.session_state:
    st.session_state.analysis = None

if "review" not in st.session_state:
    st.session_state.review = None

if "report" not in st.session_state:
    st.session_state.report = None

if "pdf_bytes" not in st.session_state:
    st.session_state.pdf_bytes = None

if "paper_name" not in st.session_state:
    st.session_state.paper_name = None


# =========================================================
# ADVANCED UI STYLING
# =========================================================

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: #080D18;
    color: #E8F0FC;
}

header[data-testid="stHeader"] {
    background: transparent;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1450px;
}

[data-testid="stSidebar"] {
    background: #0D1423;
    border-right: 1px solid #202C40;
}

[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color: #E8F0FC;
}

h1, h2, h3 {
    color: #F2F7FF !important;
    letter-spacing: -0.6px;
}

p, label, li {
    color: #A8B6CC;
}

.hero {
    background: linear-gradient(
        135deg,
        #121F36 0%,
        #10192B 45%,
        #102C36 100%
    );
    border: 1px solid #263B54;
    border-radius: 22px;
    padding: 38px 40px;
    margin-bottom: 25px;
    position: relative;
}

.hero-tag {
    color: #6DE5E0;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
}

.hero-title {
    font-size: 42px;
    font-weight: 800;
    color: #F4F8FF;
    margin-top: 12px;
    line-height: 1.15;
}

.hero-description {
    color: #A9BCD5;
    font-size: 15px;
    margin-top: 12px;
    max-width: 700px;
    line-height: 1.7;
}

.metric-card {
    background: #101929;
    border: 1px solid #233149;
    border-radius: 16px;
    padding: 22px;
    min-height: 125px;
}

.metric-label {
    color: #91A4BF;
    font-size: 12px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1px;
}

.metric-value {
    color: #F1F7FF;
    font-size: 27px;
    font-weight: 800;
    margin-top: 12px;
}

.metric-caption {
    color: #6DE5E0;
    font-size: 12px;
    margin-top: 5px;
}

.section-label {
    color: #6DE5E0;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 1.8px;
    text-transform: uppercase;
    margin-bottom: 8px;
}

.panel {
    background: #101929;
    border: 1px solid #25334A;
    border-radius: 16px;
    padding: 24px;
}

div[data-testid="stExpander"] {
    background: #101929;
    border: 1px solid #26344A;
    border-radius: 12px;
}

div[data-testid="stExpander"] summary {
    color: #EAF2FF;
}

div[data-testid="stFileUploader"] {
    background: #101929;
    border: 1px dashed #3B5878;
    border-radius: 16px;
    padding: 18px;
}

.stButton > button {
    border-radius: 10px;
    font-weight: 600;
    border: 1px solid #31566A;
    transition: 0.2s;
}

.stButton > button[kind="primary"] {
    background: linear-gradient(90deg, #22C8C7, #38A9D9);
    color: #06121D;
    border: none;
    font-weight: 800;
    min-height: 48px;
}

.stButton > button[kind="primary"]:hover {
    box-shadow: 0 0 24px #20C8C755;
    transform: translateY(-1px);
}

div[data-testid="stDownloadButton"] button {
    background: #15243A;
    color: #DDEEFF;
    border: 1px solid #30445F;
    border-radius: 10px;
}

div[data-testid="stTabs"] button {
    color: #AABCD3;
}

div[data-testid="stTabs"] button[aria-selected="true"] {
    color: #6DE5E0;
}

hr {
    border-color: #26334A;
}

.small-muted {
    color: #71839F;
    font-size: 12px;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.markdown("""
    <div style="padding: 10px 0 24px;">
        <div style="font-size:13px; color:#6DE5E0;
                    letter-spacing:2px;font-weight:800;">
            PAPERPILOT
        </div>
        <div style="font-size:25px;font-weight:800;
                    color:#F3F7FF;margin-top:4px;">
            ATLAS
        </div>
        <div style="font-size:11px;color:#71839F;">
            Research Intelligence
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    st.markdown("### Workspace")

    page = st.radio(
        "Navigation",
        [
            "Research Command Center",
            "Analysis Workspace",
            "Evidence Intelligence",
            "Research Insights",
            "Report Studio",
        ],
        label_visibility="collapsed",
    )

    st.divider()

    st.markdown("### AI Pipeline")

    st.markdown("""
    <div style="padding:10px 0;">
        <span style="color:#6DE5E0;">●</span>
        <span style="color:#E2ECF9;font-weight:600;">
        Paper Analyst
        </span>
        <div style="font-size:11px;color:#71839F;margin-left:16px;">
        Structured paper extraction
        </div>
    </div>
    <div style="padding:10px 0;">
        <span style="color:#A6BFFF;">●</span>
        <span style="color:#E2ECF9;font-weight:600;">
        Paper Reviewer
        </span>
        <div style="font-size:11px;color:#71839F;margin-left:16px;">
        Evidence and critical assessment
        </div>
    </div>
    <div style="padding:10px 0;">
        <span style="color:#6DE5E0;">●</span>
        <span style="color:#E2ECF9;font-weight:600;">
        Report Studio
        </span>
        <div style="font-size:11px;color:#71839F;margin-left:16px;">
        Markdown and PDF generation
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    st.markdown(
        '<div class="small-muted">PAPERPILOT ATLAS · V1.0</div>',
        unsafe_allow_html=True,
    )


# =========================================================
# HEADER
# =========================================================

st.markdown("""
<div class="hero">
    <div class="hero-tag">
        AI RESEARCH INTELLIGENCE PLATFORM
    </div>
    <div class="hero-title">
        Navigate Research.<br>
        Discover Intelligence.
    </div>
    <div class="hero-description">
        Transform research papers into structured knowledge,
        evidence-backed analysis, critical reviews, and
        actionable research insights.
    </div>
</div>
""", unsafe_allow_html=True)


# =========================================================
# HELPER: METRIC CARD
# =========================================================

def metric_card(label, value, caption):

    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        <div class="metric-caption">{caption}</div>
    </div>
    """, unsafe_allow_html=True)


# =========================================================
# RESEARCH COMMAND CENTER
# =========================================================

if page == "Research Command Center":

    st.markdown(
        '<div class="section-label">OVERVIEW</div>',
        unsafe_allow_html=True,
    )

    st.header("Research Command Center")

    c1, c2, c3 = st.columns(3)

    with c1:
        metric_card(
            "Research Papers",
            "01" if st.session_state.analysis else "00",
            "Papers analyzed in this session",
        )

    with c2:
        metric_card(
            "AI Agents",
            "02",
            "Analyst + Reviewer",
        )

    with c3:
        metric_card(
            "Report Formats",
            "02",
            "Markdown + PDF",
        )

    st.markdown("### Start a Research Analysis")

    uploaded_file = st.file_uploader(
        "Drop your research paper here",
        type=["pdf"],
        help="Upload a text-based PDF research paper.",
        key="main_pdf_upload",
    )

    if uploaded_file:

        st.markdown(
            f"""
            <div class="panel">
                <div style="color:#6DE5E0;font-weight:700;">
                    DOCUMENT READY
                </div>
                <div style="font-size:18px;color:#EAF2FF;
                            margin-top:8px;">
                    {uploaded_file.name}
                </div>
                <div class="small-muted">
                    PDF · {uploaded_file.size / 1024:.1f} KB
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.write("")

        if st.button(
            "Run AI Research Analysis →",
            type="primary",
            use_container_width=True,
        ):

            OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

            with tempfile.NamedTemporaryFile(
                suffix=".pdf",
                delete=False,
            ) as temp_file:

                temp_file.write(uploaded_file.getvalue())
                temp_pdf_path = Path(temp_file.name)

            try:

                progress = st.progress(0)

                with st.status(
                    "PaperPilot AI is processing your paper...",
                    expanded=True,
                ) as status:

                    st.write("Extracting document text...")
                    paper_text = extract_pdf_text(
                        str(temp_pdf_path)
                    )[:12000]

                    progress.progress(20)

                    st.write("Running Paper Analyst...")
                    progress.progress(35)

                    initial_state = {
                        "paper_text": paper_text,
                        "analysis": "",
                        "review": "",
                    }

                    result = paperpilot_workflow.invoke(
                        initial_state
                    )

                    progress.progress(80)

                    st.write("Validating analysis and review...")

                    analysis = PaperAnalysis.model_validate_json(
                        result["analysis"]
                    )

                    review = PaperReview.model_validate_json(
                        result["review"]
                    )

                    st.write("Generating downloadable reports...")

                    report = generate_markdown_report(
                        analysis=analysis,
                        review=review,
                    )

                    markdown_path = save_markdown_report(
                        report=report,
                        output_path=str(
                            OUTPUT_DIR / "Analysis_Report.md"
                        ),
                    )

                    pdf_path = generate_pdf_report(
                        markdown_path=str(markdown_path),
                        pdf_path=str(
                            OUTPUT_DIR / "Analysis_Report.pdf"
                        ),
                    )

                    progress.progress(100)
                    status.update(
                        label="Analysis completed successfully!",
                        state="complete",
                        expanded=False,
                    )

                st.session_state.analysis = analysis
                st.session_state.review = review
                st.session_state.report = report
                st.session_state.pdf_bytes = Path(
                    pdf_path
                ).read_bytes()
                st.session_state.paper_name = uploaded_file.name

                st.success(
                    "Your research analysis is ready."
                )

                st.rerun()

            except Exception as e:
                st.error(f"Analysis failed: {e}")

            finally:
                temp_pdf_path.unlink(missing_ok=True)

    else:

        st.info(
            "Upload a PDF above to begin your first research analysis."
        )


# =========================================================
# ANALYSIS WORKSPACE
# =========================================================

elif page == "Analysis Workspace":

    if not st.session_state.analysis:

        st.warning(
            "No analysis available. Start from Research Command Center."
        )

    else:

        analysis = st.session_state.analysis

        st.markdown(
            '<div class="section-label">PAPER INTELLIGENCE</div>',
            unsafe_allow_html=True,
        )

        st.header(analysis.metadata.title)

        st.caption(
            f"{', '.join(analysis.metadata.authors)}"
            f" · {analysis.metadata.publication}"
        )

        st.markdown("### Executive Summary")

        st.markdown(
            f'<div class="panel">{analysis.executive_summary}</div>',
            unsafe_allow_html=True,
        )

        st.markdown("### Structured Analysis")

        sections = {
            "Research Problem": analysis.research_problem,
            "Objectives": analysis.objectives,
            "Methodology": analysis.methodology,
            "Architecture": analysis.architecture,
            "Experimental Setup": analysis.experimental_setup,
            "Datasets": analysis.datasets,
            "Results": analysis.results,
            "Contributions": analysis.contributions,
            "Limitations": analysis.limitations,
        }

        for title, section in sections.items():

            with st.expander(title):

                st.write(section.content)

                st.caption(
                    "Source pages: "
                    + ", ".join(
                        map(str, section.page_references)
                    )
                )


# =========================================================
# EVIDENCE INTELLIGENCE
# =========================================================

elif page == "Evidence Intelligence":

    if not st.session_state.review:

        st.warning("Run a paper analysis first.")

    else:

        review = st.session_state.review

        st.markdown(
            '<div class="section-label">CLAIM VALIDATION</div>',
            unsafe_allow_html=True,
        )

        st.header("Evidence Intelligence")

        st.write(
            "Inspect how the reviewer evaluates claims "
            "against the available paper evidence."
        )

        supported = sum(
            1 for item in review.verification_results
            if "support" in item.assessment.lower()
            and "not supported" not in item.assessment.lower()
        )

        total = len(review.verification_results)

        c1, c2, c3 = st.columns(3)

        with c1:
            metric_card(
                "Verified Claims",
                supported,
                "Claims assessed as supported",
            )

        with c2:
            metric_card(
                "Reviewed Claims",
                total,
                "Total verification records",
            )

        with c3:
            metric_card(
                "Unsupported",
                len(review.unsupported_claims),
                "Claims flagged by reviewer",
            )

        st.markdown("### Claim Verification Records")

        for item in review.verification_results:

            with st.expander(item.claim):

                st.markdown(
                    f"**Assessment:** {item.assessment}"
                )

                st.markdown("**Evidence**")
                st.write(item.evidence)

                st.caption(
                    f"Pages: {item.page_references}"
                )

        st.markdown("### Unsupported Claims")

        if review.unsupported_claims:

            for claim in review.unsupported_claims:
                st.warning(claim)

        else:
            st.success("No unsupported claims were reported.")


# =========================================================
# RESEARCH INSIGHTS
# =========================================================

elif page == "Research Insights":

    if not st.session_state.review:

        st.warning("Run a paper analysis first.")

    else:

        review = st.session_state.review

        st.markdown(
            '<div class="section-label">DISCOVERY & CRITIQUE</div>',
            unsafe_allow_html=True,
        )

        st.header("Research Insights")

        tab1, tab2, tab3, tab4 = st.tabs(
            [
                "Insights",
                "Strengths",
                "Limitations",
                "Future Questions",
            ]
        )

        with tab1:

            for insight in review.research_insights:
                st.markdown(
                    f'<div class="panel">{insight}</div>',
                    unsafe_allow_html=True,
                )
                st.write("")

        with tab2:

            for item in review.strengths:
                st.success(item)

        with tab3:

            for item in review.limitations:
                st.warning(item)

        with tab4:

            for question in review.future_research_questions:
                st.markdown(
                    f'<div class="panel">{question}</div>',
                    unsafe_allow_html=True,
                )
                st.write("")

        st.markdown("### Methodology Assessment")

        st.write(review.methodology_assessment)

        st.markdown("### Overall Assessment")

        st.markdown(
            f'<div class="panel">{review.overall_assessment}</div>',
            unsafe_allow_html=True,
        )


# =========================================================
# REPORT STUDIO
# =========================================================

elif page == "Report Studio":

    st.markdown(
        '<div class="section-label">EXPORT & DOCUMENTATION</div>',
        unsafe_allow_html=True,
    )

    st.header("Report Studio")

    st.write(
        "Export your complete research analysis "
        "and reviewer assessment."
    )

    if not st.session_state.report:

        st.info(
            "Your reports will appear here after analysis."
        )

    else:

        st.markdown("### Report Ready")

        st.success(
            f"Report generated for "
            f"{st.session_state.paper_name}"
        )

        c1, c2 = st.columns(2)

        with c1:

            st.markdown("""
            <div class="panel">
                <div style="font-size:30px;">📄</div>
                <h3>Markdown Report</h3>
                <p>Structured and editable research documentation.</p>
            </div>
            """, unsafe_allow_html=True)

            st.download_button(
                "Download Markdown",
                data=st.session_state.report,
                file_name="PaperPilot_Atlas_Report.md",
                mime="text/markdown",
                use_container_width=True,
            )

        with c2:

            st.markdown("""
            <div class="panel">
                <div style="font-size:30px;">📕</div>
                <h3>PDF Report</h3>
                <p>Formatted research analysis for sharing and reading.</p>
            </div>
            """, unsafe_allow_html=True)

            st.download_button(
                "Download PDF",
                data=st.session_state.pdf_bytes,
                file_name="PaperPilot_Atlas_Report.pdf",
                mime="application/pdf",
                use_container_width=True,
            )

        st.divider()

        st.markdown("### Report Preview")

        st.text_area(
            "Markdown Source",
            value=st.session_state.report,
            height=350,
        )
