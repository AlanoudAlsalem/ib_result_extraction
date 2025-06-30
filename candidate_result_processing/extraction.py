import os
import PyPDF2
import xlsxwriter
import streamlit as st

def courses_extraction(newline_count, content, letter):
    subjects_temp = ["", "", "", "", "", ""]
    subjects = {}
    for i in range(letter, len(content) + letter):
        # subject 1 extraction
        if newline_count == 8: subjects_temp[0] += content[i]
        
        # subject 2 extraction
        if newline_count == 9:  subjects_temp[1] += content[i]

        # subject 3 extraction
        if newline_count == 10: subjects_temp[2] += content[i]
        
        # subject 4 extraction
        if newline_count == 11: subjects_temp[3] += content[i]
        
        # subject 5 extraction
        if newline_count == 12: subjects_temp[4] += content[i]
        
        # subject 6 extraction
        if newline_count == 13: subjects_temp[5] += content[i]

        # all subjects extracted for courses students
        if newline_count == 14:
            # clean subject names
            for j in range(len(subjects_temp)):
                subjects_temp[j] = str(subjects_temp[j]).split('-')[-1].strip()

            first_grade = subjects_temp[-1][-1]
            
            # clean subject names
            for j in range(len(subjects_temp)):
                subjects_temp[j] = subjects_temp[j].split('in')[0].strip()
            
            # append first subject and grade
            subjects[str(subjects_temp[0])] = first_grade

            remaning_grades = content[i:i+10].split()

            for j in range(len(subjects_temp)):
                if j == 0: continue
                else:
                    subjects[str(subjects_temp[j])] = remaning_grades[j-1]

            break 
        
        if content[i] == '\n':
            newline_count += 1

    return subjects

def diploma_extraction(newline_count, content, letter):
    subjects_temp = ["", "", "", "", "", "", "", ""]
    subjects = {}
    for i in range(letter, len(content) + letter):
        # subject 1 extraction
        if newline_count == 8: subjects_temp[0] += content[i]
        
        # subject 2 extraction
        if newline_count == 9:  subjects_temp[1] += content[i]

        # subject 3 extraction
        if newline_count == 10: subjects_temp[2] += content[i]
        
        # subject 4 extraction
        if newline_count == 11: subjects_temp[3] += content[i]
        
        # subject 5 extraction
        if newline_count == 12: subjects_temp[4] += content[i]
        
        # subject 6 extraction
        if newline_count == 13: subjects_temp[5] += content[i]

        # subject 7 extraction
        if newline_count == 14: subjects_temp[6] += content[i]

        # subject 8 extraction
        if newline_count == 15: subjects_temp[7] += content[i]

        # all subjects extracted for courses students
        if newline_count == 17:
            # clean subject names
            for j in range(len(subjects_temp)):
                subjects_temp[j] = str(subjects_temp[j]).split('-')[-1].strip()

            first_grade = content[i-2]
            
            # clean subject names
            for j in range(len(subjects_temp)):
                subjects_temp[j] = subjects_temp[j].split('in')[0].strip()
            
            
            # append first subject and grade
            subjects[str(subjects_temp[0])] = first_grade

            remaning_grades = content[i:i+14].split()

            for j in range(len(subjects_temp)):
                if j == 0: continue
                else:
                    subjects[str(subjects_temp[j])] = remaning_grades[j-1]

            break

        if content[i] == '\n':
            newline_count += 1

    return subjects

def extract_results(pdf_file):
    diploma_students = {}
    courses_students = {}

    reader = PyPDF2.PdfReader(pdf_file, strict=False)

    student_count = 0
    for page in reader.pages:
        student_count += 1

        content = page.extract_text()
        name_str = "Name"
        i = 0
        newline_count = 0
        flag = False

        name = ""
        level = ""

        for letter in content:
            if content[i:i + len(name_str)] == name_str:
                flag = True

            # name extraction
            if newline_count == 3: name += letter
            
            # courses/ diploma extraction
            if newline_count == 4: level += letter
            
            if newline_count == 8:
                level = level.strip()
                # courses
                if level[0] == 'C':
                    subjects = courses_extraction(newline_count, content, i)
                elif level[0] == 'D':
                    subjects = diploma_extraction(newline_count, content, i)
                else:
                    print(f"ERROR in extracting results for {name}")
                    student_count -= 1
                
                break
                
            if flag and content[i] == '\n':
                newline_count += 1

            i += 1

        
        first_name = name.split(',')[-1].strip()
        last_name = name.split(',')[0].strip()
        if level[0] == 'C':
            courses_students[f"{first_name} {last_name}"] = subjects
        elif level[0] == 'D':
            diploma_students[f"{first_name} {last_name}"] = subjects
    
    print(f"Total students extracted: {student_count}")

    return courses_students, diploma_students

directory = "candidate_result_processing"
pdf_file_path = os.path.join(directory, "candidate_results_2024.pdf")
courses_students, diploma_students = extract_results("/Users/alanoud/dev/AA/candidate_result_processing/candidate_results_2024.pdf")

workbook = xlsxwriter.Workbook('output.xlsx')
worksheet = workbook.add_worksheet()

merge_format = workbook.add_format({
    'bold': True,
    'align': 'center',
    'valign': 'vcenter',
    'bg_color': '#D7E4BC'
})

worksheet.merge_range('A1:M1', 'Diploma Students', merge_format)

diploma_row_data = [
    "First name", "Last name", "Subject 1", "Subject 2", "Subject 3", "Subject 4",
    "Subject 5", "Subject 6", "TOK", "EE", "Bonus Points", "Total Points", "Tawjihi Average"
]

courses_row_data = [
    "First name", "Last name", "Subject 1", "Subject 2", "Subject 3", "Subject 4",
    "Subject 5", "Subject 6", "", "", "", "Total Points", "Tawjihi Average"
]

# diploma columns
row = 1  # Excel row 2
start_col = 0  # Excel column A
for col, value in enumerate(diploma_row_data, start=start_col):
    worksheet.write(row, col, value)

row = 2
for student in diploma_students:
    student_subjects = diploma_students[student]

    for col in range(10):
        if col == 0: # first name
            worksheet.write(row, col, student.split(' ')[0])
        elif col == 1: # last name
            last_name = ""
            for part in student.split(' ')[1:]:
                last_name += part 
                last_name += " "
            
            last_name.strip()

            worksheet.write(row, col, last_name)
        elif col == 8: # TOK
            for subject in diploma_students[student]:
                if subject[-2:] == "TK":
                    worksheet.write(row, col, diploma_students[student][subject])
        elif col == 9: # EE
            for subject in diploma_students[student]:
                if subject[-2:] == "EE":
                    worksheet.write(row, col, diploma_students[student][subject])
        else:
            for subject in student_subjects:
                if subject[-2:] not in ["EE", "TK"]:
                    worksheet.write(row, col, int(student_subjects[subject]))
                    del student_subjects[subject]
                    break
    
    row += 1

bonus_points = '=IF(AND(I3="A", J3="A"), 3, IF(AND(I3="A", J3="B"), 3, IF(AND(I3="B", J3="A"), 3, IF(AND(I3="B", J3="B"), 2, IF(AND(I3="A", J3="C"), 2, IF(AND(I3="C", J3="A"), 2, IF(AND(I3="A", J3="D"), 2, IF(AND(I3="D", J3="A"), 2, IF(AND(I3="A", J3="E"), 1, IF(AND(I3="E", J3="A"), 1, IF(AND(I3="B", J3="D"), 1, IF(AND(I3="D", J3="B"), 1, IF(AND(I3="B", J3="C"), 2, IF(AND(I3="C", J3="B"), 2, IF(AND(I3="C", J3="C"), 1, 0)))))))))))))))'
total_points = '=SUM(C3:H3,K3)'

worksheet.merge_range(f'A{row+1}:M{row+1}', 'Courses Students', merge_format)
row += 1

# courses columns
start_col = 0  # Excel column A
for col, value in enumerate(courses_row_data, start=start_col):
    worksheet.write(row, col, value)

for student in courses_students:
    student_subjects = courses_students[student]

    for col in range(8):
        if col == 0: # first name
            worksheet.write(row, col, student.split(' ')[0])
        elif col == 1: # last name
            last_name = ""
            for part in student.split(' ')[1:]:
                last_name += part 
                last_name += " "
            
            last_name.strip()

            worksheet.write(row, col, last_name)
        else:
            for subject in student_subjects:
                worksheet.write(row, col, int(student_subjects[subject]))
                del student_subjects[subject]
                break
    
    row += 1

workbook.close()

# --------------------------- Streamlit App --------------------------- #

st.title("📄 IB Results Extractor to Excel")

uploaded_file = st.file_uploader("Upload a Candidate Results PDF", type=["pdf"])

if uploaded_file:
    with st.spinner("Processing PDF..."):
        courses_students, diploma_students = extract_results(uploaded_file)
        excel_path = "output.xlsx"

    st.success("✅ Results extracted successfully!")
    with open(excel_path, "rb") as file:
        st.download_button(
            label="📥 Download Excel File",
            data=file,
            file_name="extracted_results.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )