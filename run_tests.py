"""
تشغيل أسئلة التجربة وإنتاج تقرير.

الاستخدام:
    1) شغّلي الـ API:  uvicorn api:app --port 8000
    2) جهزي ملف test_cases.csv بالأعمدة:
         question, role, expected_status, expected_id, note
       - expected_status: ok أو no_answer
       - expected_id: معرّف السؤال المتوقع (للأسئلة المعروفة فقط)
       - role: اتركيه فارغًا ليصبح "الكل"
    3) python run_tests.py
"""

import csv
from datetime import datetime
from pathlib import Path

import requests

API_URL = "http://127.0.0.1:8000"
CASES = Path("test_cases.csv")
REPORT_CSV = Path("test_report.csv")
REPORT_MD = Path("test_report.md")


def run_case(case: dict) -> dict:
    role = (case.get("role") or "").strip() or "الكل"
    expected_status = (case.get("expected_status") or "").strip()
    expected_id = (case.get("expected_id") or "").strip()

    response = requests.post(
        f"{API_URL}/search",
        json={"question": case["question"], "role": role},
        timeout=15,
    )
    response.raise_for_status()
    data = response.json()

    sources = data.get("sources") or []
    got_status = data.get("status")
    got_id = sources[0].get("id", "") if sources else ""
    has_source = bool(sources and sources[0].get("source"))
    has_date = bool(sources and sources[0].get("updated"))

    if expected_status == "ok":
        passed = (
            got_status == "ok"
            and (not expected_id or got_id == expected_id)
            and has_source
        )
    else:
        passed = got_status == "no_answer" and not data.get("answer")

    return {
        "question": case["question"],
        "role": role,
        "expected": expected_status
        + (f" ({expected_id})" if expected_id else ""),
        "got": got_status + (f" ({got_id})" if got_id else ""),
        "has_source": "نعم" if has_source else "لا",
        "has_update_date": "نعم" if has_date else "لا",
        "result": "نجح" if passed else "فشل",
        "note": case.get("note", ""),
    }


def main():
    with CASES.open(encoding="utf-8-sig") as f:
        cases = [c for c in csv.DictReader(f) if c.get("question")]

    results = [run_case(c) for c in cases]

    fields = list(results[0].keys())
    with REPORT_CSV.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(results)

    known = [r for r in results if r["expected"].startswith("ok")]
    outside = [r for r in results if r["expected"].startswith("no_answer")]
    known_pass = sum(r["result"] == "نجح" for r in known)
    outside_pass = sum(r["result"] == "نجح" for r in outside)

    lines = [
        "# تقرير تجربة مساعد المعرفة الداخلي",
        "",
        f"تاريخ التشغيل: {datetime.now():%Y-%m-%d %H:%M}",
        "",
        "## الملخص",
        "",
        f"- أسئلة معروفة الإجابة: {known_pass} / {len(known)} نجحت",
        f"- أسئلة خارج المحتوى أو الصلاحية: {outside_pass} / {len(outside)} نجحت",
        "",
        "## التفاصيل",
        "",
        "| # | السؤال | الدور | المتوقع | الفعلي | مصدر | تاريخ تحديث | النتيجة |",
        "|---|---|---|---|---|---|---|---|",
    ]

    for i, r in enumerate(results, 1):
        lines.append(
            f"| {i} | {r['question']} | {r['role']} | {r['expected']} "
            f"| {r['got']} | {r['has_source']} | {r['has_update_date']} "
            f"| {r['result']} |"
        )

    failed = [r for r in results if r["result"] == "فشل"]
    lines += ["", "## الحالات الفاشلة وسبب الفشل", ""]

    if failed:
        for r in failed:
            lines.append(f"- {r['question']} — المتوقع {r['expected']}، الفعلي {r['got']}")
    else:
        lines.append("لا توجد حالات فاشلة.")

    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"تم: {known_pass}/{len(known)} معروفة، {outside_pass}/{len(outside)} خارج المحتوى")


if __name__ == "__main__":
    main()
