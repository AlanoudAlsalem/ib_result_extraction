import streamlit as st
import pandas as pd
import altair as alt
import PyPDF2
import xlsxwriter
import io

# ------------------ PDF Extraction Logic ------------------ #

def courses_extraction(newline_count, content, letter):
    subjects_temp = ["", "", "", "", "", ""]
    subjects = {}
    for i in range(letter, len(content) + letter):
        if newline_count == 8: subjects_temp[0] += content[i]
        if newline_count == 9: subjects_temp[1] += content[i]
        if newline_count == 10: subjects_temp[2] += content[i]
        if newline_count == 11: subjects_temp[3] += content[i]
        if newline_count == 12: subjects_temp[4] += content[i]
        if newline_count == 13: subjects_temp[5] += content[i]

        if newline_count == 14:
            for j in range(len(subjects_temp)):
                subjects_temp[j] = str(subjects_temp[j]).split('-')[-1].strip()
            first_grade = subjects_temp[-1][-1]
            for j in range(len(subjects_temp)):
                subjects_temp[j] = subjects_temp[j].split('in')[0].strip()
            subjects[str(subjects_temp[0])] = first_grade
            remaning_grades = content[i:i+10].split()
            for j in range(1, len(subjects_temp)):
                subjects[str(subjects_temp[j])] = remaning_grades[j-1]
            break
        if content[i] == '\n':
            newline_count += 1
    return subjects

def diploma_extraction(newline_count, content, letter):
    subjects_temp = ["", "", "", "", "", "", "", ""]
    subjects = {}
    for i in range(letter, len(content) + letter):
        if newline_count == 8: subjects_temp[0] += content[i]
        if newline_count == 9: subjects_temp[1] += content[i]
        if newline_count == 10: subjects_temp[2] += content[i]
        if newline_count == 11: subjects_temp[3] += content[i]
        if newline_count == 12: subjects_temp[4] += content[i]
        if newline_count == 13: subjects_temp[5] += content[i]
        if newline_count == 14: subjects_temp[6] += content[i]
        if newline_count == 15: subjects_temp[7] += content[i]

        if newline_count == 17:
            for j in range(len(subjects_temp)):
                subjects_temp[j] = str(subjects_temp[j]).split('-')[-1].strip()
            first_grade = content[i-2]
            for j in range(len(subjects_temp)):
                subjects_temp[j] = subjects_temp[j].split('in')[0].strip()
            subjects[str(subjects_temp[0])] = first_grade
            remaning_grades = content[i:i+14].split()
            for j in range(1, len(subjects_temp)):
                subjects[str(subjects_temp[j])] = remaning_grades[j-1]
            break
        if content[i] == '\n':
            newline_count += 1
    return subjects

def extract_results(pdf_file):
    diploma_students = {}
    courses_students = {}
    reader = PyPDF2.PdfReader(pdf_file)
    for page in reader.pages:
        content = page.extract_text()
        i = 0
        newline_count = 0
        flag = False
        name, level = "", ""
        for letter in content:
            if content[i:i + 4] == "Name":
                flag = True
            if newline_count == 3: name += letter
            if newline_count == 4: level += letter
            if newline_count == 8:
                level = level.strip()
                if level.startswith("C"):
                    subjects = courses_extraction(newline_count, content, i)
                elif level.startswith("D"):
                    subjects = diploma_extraction(newline_count, content, i)
                else:
                    break
                break
            if flag and content[i] == '\n':
                newline_count += 1
            i += 1
        first_name = name.split(',')[-1].strip()
        last_name = name.split(',')[0].strip()
        full_name = f"{first_name} {last_name}"
        if level.startswith("C"):
            courses_students[full_name] = subjects
        elif level.startswith("D"):
            diploma_students[full_name] = subjects
    return courses_students, diploma_students

# ------------------ Excel Export ------------------ #

def create_excel_file(diploma_students, courses_students):
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output, {'in_memory': True})
    worksheet = workbook.add_worksheet()

    merge_format = workbook.add_format({
        'bold': True, 'align': 'center', 'valign': 'vcenter', 'bg_color': '#D7E4BC'
    })

    diploma_headers = ["First name", "Last name", "Subject 1", "Subject 2", "Subject 3",
                       "Subject 4", "Subject 5", "Subject 6", "TOK", "EE", "Bonus Points",
                       "Total Points", "Tawjihi Average"]
    worksheet.merge_range('A1:M1', 'Diploma Students', merge_format)
    for col, val in enumerate(diploma_headers): worksheet.write(1, col, val)

    row = 2
    for student, subjects in diploma_students.items():
        fname, lname = student.split(" ", 1)
        worksheet.write(row, 0, fname)
        worksheet.write(row, 1, lname)
        col = 2
        for subject, grade in subjects.items():
            if subject[-2:] not in ["EE", "TK"]:
                worksheet.write(row, col, int(grade))
                col += 1
        worksheet.write(row, 8, subjects.get("TOK", ""))
        worksheet.write(row, 9, subjects.get("EE", ""))
        row += 1

    worksheet.merge_range(f'A{row+1}:M{row+1}', 'Courses Students', merge_format)
    course_headers = diploma_headers
    for col, val in enumerate(course_headers): worksheet.write(row + 1, col, val)

    row += 2
    for student, subjects in courses_students.items():
        fname, lname = student.split(" ", 1)
        worksheet.write(row, 0, fname)
        worksheet.write(row, 1, lname)
        col = 2
        for subject, grade in subjects.items():
            worksheet.write(row, col, int(grade))
            col += 1
        row += 1

    workbook.close()
    output.seek(0)
    return output

# ------------------ Analytics Logic ------------------ #

def calculate_bonus(tok, ee):
    tok, ee = tok.strip().upper(), ee.strip().upper()
    bonus_3 = {("A", "A"), ("A", "B"), ("B", "A")}
    bonus_2 = {("B", "B"), ("A", "C"), ("C", "A"), ("A", "D"), ("D", "A")}
    bonus_1 = {("A", "E"), ("E", "A"), ("B", "D"), ("D", "B"),
               ("B", "C"), ("C", "B"), ("C", "C")}
    return 3 if (tok, ee) in bonus_3 else 2 if (tok, ee) in bonus_2 else 1 if (tok, ee) in bonus_1 else 0

def calculate_total(subjects, is_diploma=True):
    total = 0
    tok = ee = ""
    for sub, score in subjects.items():
        if sub[-2:] == "TK": tok = score
        elif sub[-2:] == "EE": ee = score
        else:
            try: total += int(score)
            except: pass
    if is_diploma and tok and ee:
        total += calculate_bonus(tok, ee)
    return total

def generate_leaderboard(students, totals, label):
    data = [{"Student": name, "Total Points": score} for name, score in zip(students.keys(), totals)]
    df = pd.DataFrame(data).sort_values("Total Points", ascending=False).reset_index(drop=True)
    st.subheader(f"🏅 Top {label} Performers")
    st.dataframe(df.head(10), use_container_width=True)

def get_average_subject_score(students, is_diploma):
        total_score = 0
        count = 0
        for student_subjects in students.values():
            for subject, score in student_subjects.items():
                if is_diploma and subject[-2:] in ["EE", "TK"]:
                    continue
                try:
                    total_score += int(score)
                    count += 1
                except:
                    continue
        return total_score / count if count else 0

# ------------------ Streamlit App ------------------ #

st.title("📄 IB Results Extractor to Excel")

uploaded_file = st.file_uploader("Upload a Candidate Results PDF", type=["pdf"])

if uploaded_file:
    with st.spinner("Processing PDF..."):
        try:
            courses_students, diploma_students = extract_results(uploaded_file)
        except Exception as e:
            st.error(f"❌ Error reading PDF: {e}")
            st.stop()

        if not courses_students and not diploma_students:
            st.error("❌ No data extracted from the PDF.")
            st.stop()

        try:
            excel_data = create_excel_file(diploma_students, courses_students)
        except Exception as e:
            st.error(f"❌ Error generating Excel file: {e}")
            st.stop()

    st.success("✅ Results extracted successfully!")
    st.download_button("📥 Download Excel File", data=excel_data,
                       file_name="extracted_results.xlsx",
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    # ------------------ Dashboard ------------------ #
    st.header("📊 Analytics Dashboard")

    diploma_totals = [calculate_total(s, True) for s in diploma_students.values()]
    courses_totals = [calculate_total(s, False) for s in courses_students.values()]

    if diploma_totals:
        st.metric("🎓 Avg Diploma Score", f"{sum(diploma_totals)/len(diploma_totals):.2f}")
        
        # percentage of students that got 40 or more
        num_40_plus = sum(score >= 40 for score in diploma_totals)
        percent_40_plus = (num_40_plus / len(diploma_totals)) * 100
        st.metric("🎯 % of Diploma Students Scoring ≥40", f"{percent_40_plus:.1f}%")
    if courses_totals:
        st.metric("📚 Avg Courses Score", f"{sum(courses_totals)/len(courses_totals):.2f}")

    st.subheader("📈 Diploma Students Scoring 40+")

    thresholds = {f"{t}+": sum(score >= t for score in diploma_totals) for t in range(40, 46)}
    df = pd.DataFrame.from_dict(thresholds, orient='index', columns=["Number of Students"]).reset_index()
    df.rename(columns={"index": "Threshold"}, inplace=True)

    chart = alt.Chart(df).mark_line(point=True, color="#30CDD7").encode(
        x="Threshold", y="Number of Students", tooltip=["Threshold", "Number of Students"]
    ).properties(width=600, height=400)

    st.altair_chart(chart, use_container_width=True)

    if diploma_totals:
        generate_leaderboard(diploma_students, diploma_totals, "Diploma")
    if courses_totals:
        generate_leaderboard(courses_students, courses_totals, "Courses")

    # avg subject score
    avg_diploma_subject = get_average_subject_score(diploma_students, is_diploma=True)
    avg_courses_subject = get_average_subject_score(courses_students, is_diploma=False)

    st.metric("📘 Avg Subject Score (Diploma)", f"{avg_diploma_subject:.2f}")
    st.metric("📗 Avg Subject Score (Courses)", f"{avg_courses_subject:.2f}")