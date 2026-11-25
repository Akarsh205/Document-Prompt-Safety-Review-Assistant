
import json
import csv
import io
from datetime import datetime


def generate_report(file_name, analysis):
    """
    Generate a structured defensive security report.
    """

    report = {
        "project": "DocShield AI",
        "report_type": "Document Prompt Safety Review",
        "document_name": file_name,
        "generated_at": datetime.now().isoformat(
            timespec="seconds"
        ),
        "total_passages": analysis.get(
            "total_passages", 0
        ),
        "total_findings": analysis.get(
            "total_findings", 0
        ),
        "risk_level": analysis.get(
            "risk_level", "Unknown"
        ),
        "findings": analysis.get(
            "findings", []
        ),
        "recommendation": analysis.get(
            "recommendation",
            "Manual security review recommended."
        )
    }

    return report


def export_json(report):
    """
    Convert report into JSON format.
    """

    return json.dumps(
        report,
        indent=4,
        ensure_ascii=False
    )


def export_csv(report):
    """
    Convert detected security findings into CSV.
    """

    output = io.StringIO()

    fieldnames = [
        "chunk_id",
        "category",
        "severity",
        "evidence",
        "explanation",
        "recommendation"
    ]

    writer = csv.DictWriter(
        output,
        fieldnames=fieldnames
    )

    writer.writeheader()

    for finding in report.get("findings", []):

        writer.writerow({
            "chunk_id": finding.get("chunk_id", ""),
            "category": finding.get("category", ""),
            "severity": finding.get("severity", ""),
            "evidence": finding.get("evidence", ""),
            "explanation": finding.get("explanation", ""),
            "recommendation": finding.get("recommendation", "")
        })

    return output.getvalue()
