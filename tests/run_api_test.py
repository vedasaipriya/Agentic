"""Quick test script: uploads sample PDF and runs full pipeline via API."""
import requests
import json
import time

print("Uploading sample PDF and running full pipeline...")
print("This will take 3-5 minutes (local LLM on CPU)...")
print()

start = time.time()

with open("tests/sample_requirements.pdf", "rb") as f:
    r = requests.post(
        "http://localhost:8000/api/analyze",
        files={"file": ("sample_requirements.pdf", f, "application/pdf")},
        timeout=600,
    )

elapsed = time.time() - start
print(f"Status: {r.status_code}")
print(f"Time: {elapsed:.1f}s")

if r.status_code == 200:
    data = r.json()
    c = data["clarification"]
    t = data["test_data"]

    print()
    print("=" * 50)
    print("RESULTS")
    print("=" * 50)
    print(f"Risk Level: {c['risk_level']}")
    print(f"Missing Requirements: {len(c['missing_requirements'])}")
    print(f"Ambiguities: {len(c['ambiguities'])}")
    print(f"Clarification Questions: {len(c['clarification_questions'])}")
    print(f"Assumptions: {len(c['assumptions'])}")
    print()

    valid = len(t["valid_cases"])
    invalid = len(t["invalid_cases"])
    edge = len(t["edge_cases"])
    boundary = len(t["boundary_values"])
    security = len(t["security_cases"])
    total = valid + invalid + edge + boundary + security

    print(f"Test Cases: {total} total")
    print(f"  Valid:    {valid}")
    print(f"  Invalid:  {invalid}")
    print(f"  Edge:     {edge}")
    print(f"  Boundary: {boundary}")
    print(f"  Security: {security}")

    print()
    print("--- Summary ---")
    print(c["summary"])

    # Save full output
    with open("output/test_result.json", "w", encoding="utf-8") as out:
        json.dump(data, out, indent=2)
    print()
    print("Full JSON saved to output/test_result.json")
else:
    print(f"ERROR: {r.text}")
