import sys
import os
import re
import io
import base64

import PyPDF2
import xlsxwriter
from flask import Flask, request, jsonify

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
_VALID_SUBJECT_GRADES = {str(i) for i in range(1, 8)}
_VALID_TOK_EE_GRADES  = set("ABCDE")

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _safe_int(value):
    """Convert to int; return the original value unchanged if conversion fails."""
    try:
        return int(value)
    except (ValueError, TypeError):
        return value


def _validate_grades(subjects, full_name, is_diploma, messages):
    for sub, grade in subjects.items():
        is_tok_ee = is_diploma and sub[-2:] in ("TK", "EE")
        if is_tok_ee:
            if str(grade).upper() not in _VALID_TOK_EE_GRADES:
                messages.append({
                    "type": "warning",
                    "message": f"Unexpected TOK/EE grade '{grade}' for '{sub}' — {full_name} (included as-is)",
                })
        else:
            if str(grade) not in _VALID_SUBJECT_GRADES:
                messages.append({
                    "type": "warning",
                    "message": f"Unexpected subject grade '{grade}' for '{sub}' — {full_name} (included as-is)",
                })


def _extract_name(content, page_num):
    i = newline_count = 0
    flag = False
    name = ""
    for letter in content:
        if content[i:i + 4] == "Name":
            flag = True
        if newline_count == 3:
            name += letter
        if newline_count > 3:
            break
        if flag and content[i] == "\n":
            newline_count += 1
        i += 1
    parts = name.split(",")
    if len(parts) >= 2:
        first_name, last_name = parts[-1].strip(), parts[0].strip()
    else:
        first_name, last_name = name.strip(), ""
    full_name = f"{first_name} {last_name}".strip() or f"Unknown (page {page_num + 1})"
    return full_name


# ---------------------------------------------------------------------------
# Extraction
# ---------------------------------------------------------------------------

def _courses_extraction(content):
    subjects = {}
    m = re.search(r"(\w\n){5}\w", content)
    if not m:
        return subjects
    grades = m.group().split()

    lines = re.findall(r"^MAY.+(?:SL|HL).+\n", content, re.IGNORECASE | re.MULTILINE)
    if len(lines) != len(grades):
        return subjects

    for i, line in enumerate(lines):
        sub = str(line).split("-")[-1].strip().split("in")[0].strip()
        subjects[sub] = grades[i]
    return subjects


def _diploma_extraction(content):
    subjects = {}
    m = re.search(r"(\w\n){7}\w", content)
    if not m:
        return subjects
    grades = m.group().split()

    lines = re.findall(r"^MAY.+(?:SL|HL|TK|EE).+\n", content, re.IGNORECASE | re.MULTILINE)
    if len(lines) != len(grades):
        return subjects

    for i, line in enumerate(lines):
        sub = str(line).split("-")[-1].strip().split("in")[0].strip()
        subjects[sub] = grades[i]
    return subjects


def _extract_results(pdf_file):
    diploma_students: dict = {}
    courses_students: dict = {}
    messages: list = []

    try:
        reader = PyPDF2.PdfReader(pdf_file)
    except Exception as e:
        messages.append({"type": "error", "message": f"Could not open PDF: {e}"})
        return courses_students, diploma_students, messages

    for page_num, page in enumerate(reader.pages):
        try:
            content = page.extract_text()
            if not content:
                messages.append({"type": "warning", "message": f"Page {page_num + 1} returned no text — skipped"})
                continue

            level = re.search(r"\b(?:COURSE|DIPLOMA)\b", content, re.IGNORECASE)
            if not level:
                continue

            full_name = _extract_name(content, page_num)

            if level.group().lower() == "course":
                subjects = _courses_extraction(content)
                if not subjects:
                    messages.append({"type": "error", "message": f"Could not extract grades for {full_name} — EXCLUDED"})
                else:
                    _validate_grades(subjects, full_name, is_diploma=False, messages=messages)
                    courses_students[full_name] = subjects

            elif level.group().lower() == "diploma":
                subjects = _diploma_extraction(content)
                if not subjects:
                    messages.append({"type": "error", "message": f"Could not extract grades for {full_name} — EXCLUDED"})
                else:
                    _validate_grades(subjects, full_name, is_diploma=True, messages=messages)
                    diploma_students[full_name] = subjects

        except Exception as e:
            messages.append({"type": "warning", "message": f"Unexpected error on page {page_num + 1} — skipped ({e})"})

    return courses_students, diploma_students, messages


# ---------------------------------------------------------------------------
# Analytics
# ---------------------------------------------------------------------------

def _calculate_bonus(tok, ee):
    tok, ee = str(tok).strip().upper(), str(ee).strip().upper()
    bonus_3 = {("A", "A"), ("A", "B"), ("B", "A")}
    bonus_2 = {("B", "B"), ("A", "C"), ("C", "A"), ("A", "D"), ("D", "A"), ("B", "C"), ("C", "B")}
    bonus_1 = {("B", "D"), ("D", "B"), ("C", "C")}
    return 3 if (tok, ee) in bonus_3 else 2 if (tok, ee) in bonus_2 else 1 if (tok, ee) in bonus_1 else 0


def _calculate_total(subjects, is_diploma=True):
    total = 0
    tok = ee = ""
    for sub, score in subjects.items():
        if sub[-2:] == "TK":
            tok = score
        elif sub[-2:] == "EE":
            ee = score
        else:
            try:
                total += int(score)
            except (ValueError, TypeError):
                pass
    if is_diploma and tok and ee:
        total += _calculate_bonus(tok, ee)
    return total


def _get_subject_averages(diploma_students, courses_students):
    totals: dict = {}
    counts: dict = {}
    for students in (diploma_students, courses_students):
        for subjects in students.values():
            for sub, grade in subjects.items():
                if sub[-2:] in ("TK", "EE"):
                    continue
                try:
                    val = int(grade)
                    totals[sub] = totals.get(sub, 0) + val
                    counts[sub] = counts.get(sub, 0) + 1
                except (ValueError, TypeError):
                    pass
    return {sub: round(totals[sub] / counts[sub], 2) for sub in totals if counts[sub] > 0}


def _avg_subject_score(students, is_diploma):
    total_score = count = 0
    for subjects in students.values():
        for sub, score in subjects.items():
            if is_diploma and sub[-2:] in ("TK", "EE"):
                continue
            try:
                total_score += int(score)
                count += 1
            except (ValueError, TypeError):
                pass
    return round(total_score / count, 2) if count else 0


# ---------------------------------------------------------------------------
# Excel export
# ---------------------------------------------------------------------------

def _create_excel(diploma_students, courses_students):
    output = io.BytesIO()
    wb = xlsxwriter.Workbook(output, {"in_memory": True})
    ws = wb.add_worksheet()

    header_fmt = wb.add_format({"bold": True, "align": "center", "valign": "vcenter", "bg_color": "#D7E4BC"})
    headers = ["First name", "Last name", "Subject 1", "Subject 2", "Subject 3",
               "Subject 4", "Subject 5", "Subject 6", "TOK", "EE",
               "Bonus Points", "Total Points", "Tawjihi Average"]

    ws.merge_range("A1:M1", "Diploma Students", header_fmt)
    for col, val in enumerate(headers):
        ws.write(1, col, val)

    row = 2
    for student, subjects in diploma_students.items():
        parts = student.split(" ", 1)
        ws.write(row, 0, parts[0])
        ws.write(row, 1, parts[1] if len(parts) > 1 else "")
        col = 2
        for sub, grade in subjects.items():
            if sub[-2:] not in ("EE", "TK"):
                ws.write(row, col, _safe_int(grade))
                col += 1
            elif sub[-2:] == "EE":
                ws.write(row, 9, grade)
            elif sub[-2:] == "TK":
                ws.write(row, 8, grade)
        row += 1

    ws.merge_range(f"A{row+1}:M{row+1}", "Courses Students", header_fmt)
    for col, val in enumerate(headers):
        ws.write(row + 1, col, val)
    row += 2

    for student, subjects in courses_students.items():
        parts = student.split(" ", 1)
        ws.write(row, 0, parts[0])
        ws.write(row, 1, parts[1] if len(parts) > 1 else "")
        col = 2
        for sub, grade in subjects.items():
            ws.write(row, col, _safe_int(grade))
            col += 1
        row += 1

    wb.close()
    output.seek(0)
    return output.getvalue()


# ---------------------------------------------------------------------------
# Flask app
# ---------------------------------------------------------------------------
app = Flask(__name__)


@app.after_request
def _cors(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return response


@app.route("/api/extract", methods=["POST", "OPTIONS"])
def extract_endpoint():
    if request.method == "OPTIONS":
        return app.make_default_options_response()

    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    pdf_file = request.files["file"]
    if not (pdf_file.filename or "").lower().endswith(".pdf"):
        return jsonify({"error": "File must be a PDF"}), 400

    try:
        courses_students, diploma_students, messages = _extract_results(pdf_file)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    if not courses_students and not diploma_students:
        return jsonify({"error": "No data could be extracted from the PDF.", "messages": messages}), 422

    diploma_totals = [_calculate_total(s, True)  for s in diploma_students.values()]
    courses_totals = [_calculate_total(s, False) for s in courses_students.values()]

    # Build flat row objects for the frontend tables
    diploma_rows = [
        {"name": name, "total": total, **subjects}
        for name, subjects, total in zip(diploma_students.keys(), diploma_students.values(), diploma_totals)
    ]
    courses_rows = [
        {"name": name, "total": total, **subjects}
        for name, subjects, total in zip(courses_students.keys(), courses_students.values(), courses_totals)
    ]

    # Preserve insertion-order unique subject columns
    def _unique_cols(rows):
        seen: set = set()
        cols = []
        for row in rows:
            for k in row:
                if k not in ("name", "total") and k not in seen:
                    cols.append(k)
                    seen.add(k)
        return cols

    analytics = {
        "diploma_totals": diploma_totals,
        "courses_totals": courses_totals,
        "avg_diploma": round(sum(diploma_totals) / len(diploma_totals), 2) if diploma_totals else 0,
        "avg_courses": round(sum(courses_totals) / len(courses_totals), 2) if courses_totals else 0,
        "percent_40_plus": round(
            sum(s >= 40 for s in diploma_totals) / len(diploma_totals) * 100, 1
        ) if diploma_totals else 0,
        "subject_averages": _get_subject_averages(diploma_students, courses_students),
        "avg_diploma_subject": _avg_subject_score(diploma_students, True),
        "avg_courses_subject": _avg_subject_score(courses_students, False),
        "thresholds": {f"{t}+": int(sum(s >= t for s in diploma_totals)) for t in range(40, 46)},
    }

    excel_base64 = None
    try:
        excel_base64 = base64.b64encode(_create_excel(diploma_students, courses_students)).decode()
    except Exception as e:
        messages.append({"type": "warning", "message": f"Could not generate Excel file: {e}"})

    return jsonify({
        "diploma_rows":  diploma_rows,
        "courses_rows":  courses_rows,
        "diploma_cols":  _unique_cols(diploma_rows),
        "courses_cols":  _unique_cols(courses_rows),
        "analytics":     analytics,
        "messages":      messages,
        "excel_base64":  excel_base64,
    })
