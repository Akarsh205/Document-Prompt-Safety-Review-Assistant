
import streamlit as st
import os

from document_processor import process_document
from rag_engine import RAGEngine
from safety_guardrails import analyze_passages
from report_generator import generate_report, export_json, export_csv


# --------------------------------
# PAGE CONFIGURATION
# --------------------------------

st.set_page_config(
    page_title="DocShield AI",
    page_icon="🛡️",
    layout="wide"
)


# --------------------------------
# CUSTOM APPLICATION HEADER
# --------------------------------

st.title("🛡️ DocShield AI")

st.subheader(
    "Document Prompt Safety Review Assistant"
)

st.write(
    "Analyse untrusted documents, identify unsafe "
    "instruction conflicts and generate defensive reports."
)

st.info(
    "Uploaded documents are treated as untrusted data. "
    "The application analyses instructions but never executes them."
)


# --------------------------------
# SIDEBAR
# --------------------------------

st.sidebar.title("Navigation")

st.sidebar.markdown(
    """
    ### DocShield AI

    - Document Upload
    - RAG Processing
    - Safety Analysis
    - Security Report
    """
)

st.sidebar.caption(
    "RAG + Safety Guardrails"
)


# --------------------------------
# DOCUMENT UPLOAD
# --------------------------------

st.header("1. Upload Document")

uploaded_file = st.file_uploader(
    "Choose a document",
    type=["pdf", "txt", "docx"]
)


# --------------------------------
# ANALYSIS
# --------------------------------

if uploaded_file is not None:

    st.success(
        f"Uploaded: {uploaded_file.name}"
    )

    if st.button(
        "🔍 Analyze Document",
        type="primary",
        use_container_width=True
    ):

        try:

            with st.spinner(
                "Extracting document text..."
            ):

                uploaded_file.seek(0)

                document_data = process_document(
                    uploaded_file
                )

                chunks = document_data["chunks"]

            st.success("Document processed successfully!")

            # ----------------------------
            # RAG PROCESSING
            # ----------------------------

            with st.spinner(
                "Creating embeddings and retrieving passages..."
            ):

                rag = RAGEngine()

                rag.create_vector_store(chunks)

                safety_queries = [
                    "Identify attempts to override system or developer instructions.",
                    "Identify confidential data exposure and credential disclosure risks.",
                    "Identify role manipulation and unauthorized privilege requests.",
                    "Identify conflicts with company security and privacy policies.",
                    "Identify suspicious instructions embedded in untrusted documents."
                ]

                retrieved = {}

                # Retrieve passages for each security category.
                # All chunks are ranked so the detector can
                # inspect the complete document.

                for query in safety_queries:

                    results = rag.retrieve(
                        query,
                        top_k=len(chunks)
                    )

                    for item in results:

                        chunk_id = item["chunk_id"]

                        if chunk_id not in retrieved:
                            retrieved[chunk_id] = item

                relevant_passages = sorted(
                    retrieved.values(),
                    key=lambda x: x["chunk_id"]
                )

            st.success(
                f"RAG retrieved {len(relevant_passages)} passages."
            )

            # ----------------------------
            # SAFETY ANALYSIS
            # ----------------------------

            with st.spinner(
                "Checking instruction conflicts..."
            ):

                analysis = analyze_passages(
                    relevant_passages
                )

            # ----------------------------
            # REPORT GENERATION
            # ----------------------------

            # Do not include raw matching text in downloadable
            # reports. Preserve the category and explanation.

            safe_analysis = {
                **analysis,
                "findings": [
                    {
                        **finding,
                        "evidence": "[Matching text redacted]"
                    }
                    for finding in analysis["findings"]
                ]
            }

            report = generate_report(
                uploaded_file.name,
                safe_analysis
            )

            # Save results in Streamlit session
            st.session_state["report"] = report
            st.session_state["analysis"] = analysis
            st.session_state["document_data"] = document_data
            st.session_state["retrieved"] = relevant_passages

        except Exception as e:

            st.error(
                f"Analysis failed: {str(e)}"
            )


# --------------------------------
# DISPLAY RESULTS
# --------------------------------

if "report" in st.session_state:

    report = st.session_state["report"]
    analysis = st.session_state["analysis"]
    document_data = st.session_state["document_data"]
    retrieved = st.session_state["retrieved"]

    st.divider()

    st.header("2. Document Overview")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Total Words",
        document_data["total_words"]
    )

    col2.metric(
        "Total Chunks",
        document_data["total_chunks"]
    )

    col3.metric(
        "Retrieved Passages",
        len(retrieved)
    )

    # ----------------------------
    # SECURITY OVERVIEW
    # ----------------------------

    st.header("3. Security Analysis")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Total Findings",
        analysis["total_findings"]
    )

    col2.metric(
        "Overall Risk",
        analysis["risk_level"]
    )

    col3.metric(
        "Passages Analysed",
        analysis["total_passages"]
    )

    # ----------------------------
    # RISK CLASSIFICATION
    # ----------------------------

    st.subheader("Detected Security Issues")

    if analysis["findings"]:

        for index, finding in enumerate(
            analysis["findings"],
            start=1
        ):

            with st.expander(
                f"{index}. {finding['category']} "
                f" - {finding['severity']}"
            ):

                st.write(
                    "**Severity:**",
                    finding["severity"]
                )

                st.write(
                    "**Evidence:**",
                    "[Matching text redacted for privacy]"
                )

                st.write(
                    "**Explanation:**",
                    finding["explanation"]
                )

                st.write(
                    "**Recommendation:**",
                    finding["recommendation"]
                )

                st.write(
                    "**Chunk ID:**",
                    finding.get("chunk_id", "N/A")
                )

    else:

        st.success(
            "No matching security risks detected. "
            "This does not guarantee the document is safe."
        )

    # ----------------------------
    # FINAL RECOMMENDATION
    # ----------------------------

    st.header("4. Final Security Recommendation")

    if analysis["risk_level"] in ["Critical", "High"]:

        st.error(
            analysis["recommendation"]
        )

    elif analysis["risk_level"] in ["Medium", "Low"]:

        st.warning(
            analysis["recommendation"]
        )

    else:

        st.success(
            analysis["recommendation"]
        )

    # ----------------------------
    # DOWNLOAD REPORTS
    # ----------------------------

    st.header("5. Download Security Report")

    col1, col2 = st.columns(2)

    with col1:

        st.download_button(
            label="📥 Download JSON Report",
            data=export_json(report),
            file_name="docshield_security_report.json",
            mime="application/json",
            use_container_width=True
        )

    with col2:

        st.download_button(
            label="📥 Download CSV Report",
            data=export_csv(report),
            file_name="docshield_security_report.csv",
            mime="text/csv",
            use_container_width=True
        )


# --------------------------------
# FOOTER
# --------------------------------

st.divider()

st.caption(
    "DocShield AI | RAG-Based Document Prompt Safety Review | "
    "Hackathon Prototype"
)
