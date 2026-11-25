
from report_generator import (
    generate_report,
    export_json,
    export_csv
)

# Sample security analysis
analysis = {
    "total_passages": 10,
    "total_findings": 2,
    "risk_level": "High",

    "findings": [
        {
            "chunk_id": 2,
            "category": "Instruction Override",
            "severity": "High",
            "evidence": "Ignore previous instructions",
            "explanation": "Potential instruction conflict.",
            "recommendation": "Treat as untrusted data."
        },
        {
            "chunk_id": 5,
            "category": "Policy Conflict",
            "severity": "High",
            "evidence": "Disable security protections",
            "explanation": "Potential security policy conflict.",
            "recommendation": "Request human security review."
        }
    ],

    "recommendation": "Human security review required."
}

# Generate report
report = generate_report(
    "sample_policy.pdf",
    analysis
)

# Export JSON
json_report = export_json(report)

# Export CSV
csv_report = export_csv(report)

# Save reports
with open(
    "reports/security_report.json",
    "w",
    encoding="utf-8"
) as file:
    file.write(json_report)

with open(
    "reports/security_report.csv",
    "w",
    encoding="utf-8",
    newline=""
) as file:
    file.write(csv_report)

print("DOCSHIELD AI REPORT GENERATED")
print("=" * 40)

print("Document:", report["document_name"])
print("Total Passages:", report["total_passages"])
print("Total Findings:", report["total_findings"])
print("Risk Level:", report["risk_level"])

print("\nReports saved successfully!")
