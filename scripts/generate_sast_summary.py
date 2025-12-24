#!/usr/bin/env python3
"""
Generate SAST & Secrets scanning summary report.

Usage:
    python scripts/generate_sast_summary.py
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List


def load_json_report(filepath: Path) -> Dict[str, Any]:
    if not filepath.exists():
        return {}

    try:
        with open(filepath, encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, Exception) as e:
        print(f"Could not load {filepath}: {e}", file=sys.stderr)
        return {}


def analyze_semgrep(data: Dict[str, Any]) -> tuple:
    results = data.get("results", [])

    severity_counts = {"ERROR": 0, "WARNING": 0, "INFO": 0}
    findings = []

    for result in results:
        severity = result.get("extra", {}).get("severity", "INFO")
        severity_counts[severity] = severity_counts.get(severity, 0) + 1

        findings.append(
            {
                "severity": severity,
                "rule_id": result.get("check_id", "unknown"),
                "message": result.get("extra", {}).get("message", "No message"),
                "file": result.get("path", "unknown"),
                "line": result.get("start", {}).get("line", 0),
                "cwe": result.get("extra", {}).get("metadata", {}).get("cwe", "N/A"),
            }
        )

    return severity_counts, findings


def analyze_gitleaks(data: Dict[str, Any]) -> tuple:
    if isinstance(data, list):
        findings = data
    else:
        findings = data.get("findings", [])

    count = len(findings)
    secrets = []

    for finding in findings:
        secrets.append(
            {
                "rule": finding.get("RuleID", "unknown"),
                "file": finding.get("File", "unknown"),
                "line": finding.get("StartLine", 0),
                "commit": finding.get("Commit", "N/A")[:7],
                "secret": finding.get("Secret", "")[:20] + "...",
            }
        )

    return count, secrets


def generate_findings_section(findings: List[Dict], title: str, emoji: str) -> str:
    if not findings:
        return f"\n## {emoji} {title}\n\nNo {title.lower()} found!\n\n"

    section = f"\n## {emoji} {title}\n\n"
    section += f"Found **{len(findings)}** issues:\n\n"

    for idx, finding in enumerate(findings[:10], 1):
        section += f"### {idx}. {finding.get('rule_id', finding.get('rule', 'unknown'))}\n\n"
        section += f"**File:** `{finding['file']}`:{finding['line']}\n\n"

        if "message" in finding:
            section += f"**Message:** {finding['message'][:200]}\n\n"

        if "cwe" in finding and finding["cwe"] != "N/A":
            section += f"**CWE:** {finding['cwe']}\n\n"

        section += "---\n\n"

    if len(findings) > 10:
        section += f"*...and {len(findings) - 10} more findings.*\n\n"

    return section


def generate_action_plan(semgrep_counts: Dict, gitleaks_count: int) -> str:
    plan = "\n## Action Plan\n\n"

    critical_count = semgrep_counts.get("ERROR", 0) + gitleaks_count

    if critical_count > 0:
        plan += f"### Critical Issues: {critical_count}\n\n"
        plan += "**Immediate actions required:**\n\n"

        if gitleaks_count > 0:
            plan += f"1. **{gitleaks_count} Secrets detected** - Must be rotated immediately\n"
            plan += "   - Revoke exposed credentials\n"
            plan += "   - Generate new secrets\n"
            plan += "   - Update in secure storage (GitHub Secrets)\n"
            plan += "   - Add to `.gitleaks.toml` allowlist if false positive\n\n"

        if semgrep_counts.get("ERROR", 0) > 0:
            plan += f"2. **{semgrep_counts['ERROR']} High severity code issues**\n"
            plan += "   - Review and fix security vulnerabilities\n"
            plan += "   - Prioritize SQL injection and hardcoded secrets\n"
            plan += "   - Add unit tests for fixes\n\n"

        plan += "### Triage Process\n\n"
        plan += """
For each finding:

**Option 1: Fix Immediately**
- Security-critical issues (SQL injection, secrets)
- Update code to follow secure coding practices
- Add tests to prevent regression

**Option 2: Create Issue for Backlog**
- Lower priority issues
- Requires architectural changes
- Create GitHub Issue with:
  - Finding details
  - Severity and CWE
  - Proposed fix
  - Timeline

**Option 3: Add Waiver/Suppression**
- False positives
- Test code that mimics vulnerabilities
- Document in code with comment explaining why safe
"""
    else:
        plan += "**No critical issues found!**\n\n"
        plan += "Continue monitoring and maintain secure coding practices.\n\n"

    if semgrep_counts.get("WARNING", 0) > 0:
        plan += f"\n### Warnings: {semgrep_counts['WARNING']}\n\n"
        plan += "Review and address in next sprint:\n"
        plan += "- Missing rate limiting\n"
        plan += "- Unsafe environment variable usage\n"
        plan += "- Debug mode configurations\n\n"

    return plan


def generate_markdown_summary(
    semgrep_counts: Dict, semgrep_findings: List, gitleaks_count: int, gitleaks_secrets: List
) -> str:

    summary = f"""# SAST & Secrets Scanning Summary

**Scan Date:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")}

## Overview

| Tool | Category | Count |
|------|----------|-------|
| Semgrep | Critical (ERROR) | {semgrep_counts.get('ERROR', 0)} |
| Semgrep | Warning | {semgrep_counts.get('WARNING', 0)} |
| Semgrep | Info | {semgrep_counts.get('INFO', 0)} |
| Gitleaks | Secrets Found | {gitleaks_count} |

**Total Issues:** {semgrep_counts.get('ERROR', 0) + semgrep_counts.get('WARNING', 0) + gitleaks_count}

"""

    critical_findings = [f for f in semgrep_findings if f["severity"] == "ERROR"]
    summary += generate_findings_section(critical_findings, "Critical Findings (ERROR)", "")

    if gitleaks_secrets:
        summary += "\n## Exposed Secrets\n\n"
        summary += f"Found **{len(gitleaks_secrets)}** potential secrets:\n\n"
        for secret in gitleaks_secrets[:5]:
            summary += f"- **{secret['rule']}** in `{secret['file']}`:{secret['line']}\n"
        if len(gitleaks_secrets) > 5:
            summary += f"\n*...and {len(gitleaks_secrets) - 5} more secrets.*\n"
        summary += "\n"

    # Add warnings
    warning_findings = [f for f in semgrep_findings if f["severity"] == "WARNING"]
    summary += generate_findings_section(warning_findings, "Warnings", "")

    # Add action plan
    summary += generate_action_plan(semgrep_counts, gitleaks_count)

    # Add resources
    summary += """
## Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [CWE Database](https://cwe.mitre.org/)
- [Semgrep Rules](https://semgrep.dev/r)
- [Gitleaks Documentation](https://github.com/gitleaks/gitleaks)

## Integration with DevSecOps Report

This SAST summary will be integrated into the final DevSecOps Statement (DS-10).

**Key Metrics:**
- SAST coverage: Python codebase
- Custom rules: FastAPI-specific security checks
- Secret detection: Full git history scan
- Findings triaged: Fix/Backlog/Waiver decisions documented

---

*Generated by SAST & Secrets workflow*
"""

    return summary


def main():
    """Main function."""
    if len(sys.argv) < 2:
        print("Usage: python generate_sast_summary.py <reports_dir>", file=sys.stderr)
        sys.exit(1)

    reports_dir = Path(sys.argv[1])
    if not reports_dir.exists():
        reports_dir.mkdir(parents=True, exist_ok=True)

    print(f"Loading reports from: {reports_dir}")
    semgrep_data = load_json_report(reports_dir / "semgrep.json")
    gitleaks_data = load_json_report(reports_dir / "gitleaks.json")

    print("Analyzing findings...")
    semgrep_counts, semgrep_findings = analyze_semgrep(semgrep_data)
    gitleaks_count, gitleaks_secrets = analyze_gitleaks(gitleaks_data)

    print("Generating summary...")
    summary = generate_markdown_summary(
        semgrep_counts, semgrep_findings, gitleaks_count, gitleaks_secrets
    )

    summary_file = reports_dir / "sast_summary.md"
    with open(summary_file, "w", encoding="utf-8") as f:
        f.write(summary)

    print(f"\nSummary saved: {summary_file}")
    print("\nStatistics:")
    print(f"   Semgrep Critical: {semgrep_counts.get('ERROR', 0)}")
    print(f"   Semgrep Warnings: {semgrep_counts.get('WARNING', 0)}")
    print(f"   Secrets Found: {gitleaks_count}")

    critical_count = semgrep_counts.get("ERROR", 0) + gitleaks_count
    if critical_count > 0:
        print(f"\nFound {critical_count} critical issues!")
        sys.exit(1)

    print("\n SAST scan completed successfully")
    sys.exit(0)


if __name__ == "__main__":
    main()
