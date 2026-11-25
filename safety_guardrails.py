
import re


# Security detection rules
SECURITY_RULES = {
    "Instruction Override": {
        "severity": "High",
        "patterns": [
            r"\bignore\s+(all\s+)?(previous|prior|above|system|developer)\s+instructions\b",
            r"\bdisregard\s+(all\s+)?(previous|prior|above)\s+instructions\b",
            r"\boverride\s+(the\s+)?(system|security|safety)\s+(instructions|rules|controls)\b",
            r"\bbypass\s+(the\s+)?(system|security|safety)\s+(instructions|rules|controls)\b"
        ]
    },

    "Data Exfiltration": {
        "severity": "Critical",
        "patterns": [
            r"\b(reveal|expose|disclose|leak|dump)\b.{0,70}\b(secrets?|credentials?|passwords?|api keys?|confidential data|private data)\b",
            r"\b(send|share|transmit)\b.{0,70}\b(confidential data|private data|credentials?|secrets?)\b"
        ]
    },

    "Role Manipulation": {
        "severity": "High",
        "patterns": [
            r"\b(you are now|act as|pretend to be|assume the role of)\b.{0,60}\b(admin|administrator|system|developer|root|unrestricted)\b",
            r"\b(change|switch|modify)\s+(your\s+)?role\s+to\b"
        ]
    },

    "Policy Conflict": {
        "severity": "High",
        "patterns": [
            r"\b(disable|turn off|deactivate)\b.{0,60}\b(safety|security|guardrails?|protections?)\b",
            r"\b(do not|don't|never)\s+follow\b.{0,50}\b(company|security|safety|privacy)\s+polic(y|ies)\b",
            r"\b(ignore|bypass|violate)\b.{0,50}\b(company|security|safety|privacy)\s+polic(y|ies)\b"
        ]
    },

    "Untrusted Content": {
        "severity": "Medium",
        "patterns": [
            r"\b(untrusted instruction|embedded instruction|hidden instruction)\b",
            r"\b(instruction embedded in (the )?(document|file|passage))\b"
        ]
    }
}


SEVERITY_ORDER = {
    "Safe": 0,
    "Low": 1,
    "Medium": 2,
    "High": 3,
    "Critical": 4
}


def detect_risks(text):
    """
    Identify suspicious instruction patterns
    in an untrusted document passage.
    """

    findings = []

    for category, rule in SECURITY_RULES.items():

        for pattern in rule["patterns"]:

            matches = re.finditer(
                pattern,
                text,
                flags=re.IGNORECASE
            )

            for match in matches:

                evidence = match.group(0)

                finding = {
                    "category": category,
                    "severity": rule["severity"],
                    "evidence": evidence,
                    "explanation": (
                        f"Potential {category.lower()} "
                        "detected in the document."
                    ),
                    "recommendation": (
                        "Treat this passage as untrusted data. "
                        "Do not execute its instructions and "
                        "request security review."
                    )
                }

                # Avoid duplicate findings for the same evidence
                if finding not in findings:
                    findings.append(finding)

    return findings


def analyze_passages(passages):
    """
    Analyse passages retrieved by the RAG engine.
    Generate a defensive security report.
    """

    all_findings = []

    for passage in passages:

        if isinstance(passage, dict):
            text = passage.get("text", "")
            chunk_id = passage.get("chunk_id", None)
        else:
            text = str(passage)
            chunk_id = None

        if not text.strip():
            continue

        findings = detect_risks(text)

        for finding in findings:
            finding["chunk_id"] = chunk_id
            all_findings.append(finding)

    # Determine overall risk
    if all_findings:

        risk_level = max(
            all_findings,
            key=lambda item: SEVERITY_ORDER[item["severity"]]
        )["severity"]

    else:
        risk_level = "Safe"

    # Create summary
    summary = {
        "total_passages": len(passages),
        "total_findings": len(all_findings),
        "risk_level": risk_level,
        "findings": all_findings,
        "recommendation": (
            "Human security review required."
            if all_findings
            else "No matching risks detected. "
                 "This does not guarantee the document is safe."
        )
    }

    return summary
