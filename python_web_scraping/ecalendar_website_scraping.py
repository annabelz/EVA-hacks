import requests
import numpy as np 
import scipy
from bs4 import BeautifulSoup
from bs4 import SoupStrainer
from itertools import chain
import re
import pandas as pd
from flask import Flask, render_template, request

def addCourse(course, term, not_taken_courses, num_credits_remaining, output_df):
    """
    course: variable name of the course OBJECT to be added
    num_credits_remaining: number of credits remaining in the major
    term: Fall or Winter
    
    """
    
    prereq = course.prereq
    coreq = course.coreq
    terms_available = course.terms
 
    if terms_available.__contains__(term):
        if prereq == '':
            course.taken=True
            return True

        elif prereq not in not_taken_courses:
            if coreq == '':
                course.taken=True
                return True
            elif num_credits_remaining >= int(output_df[output_df['Course Code']==course.code]['Num Credit Hours'].values[0])+int(output_df[output_df['Course Code']==coreq]['Num Credit Hours'].values[0]):
                course.taken=True
                return True
            else:
                return False

        else:
            return False
    else:
        return False

class Course:
    code=''
    ch=int(0)
    terms=''
    prereq=''
    coreq=''
    taken=False
    
    def __init__(self,code,ch,terms,prereq,coreq):
        self.code = code;
        self.ch = ch;
        self.terms = terms
        self.prereq = prereq
        self.coreq = coreq
        self.taken=False

app = Flask(__name__)

@app.route("/")

def index():
    
    user_link = request.args.get("Enter a link to the ECalendar for Your Major:", "")
    info = "doesnt go thru"

    if request.args['user_link'] != "": 
        if request.args['user_link'][:79] != 'https://www.mcgill.ca/study/2021-2022/faculties/science/undergraduate/programs/':
            info = ""
            raise NameError()
        info = get_info(request.args['user_link'])
           
            
    return (render_template("mcdegreeplanning.html") + "<p>" + info + "</p>")


def get_info(user_link): 
    user_link = input("Enter a link to the ECalendar for Your Major:")
    if user_link[:79] != 'https://www.mcgill.ca/study/2021-2022/faculties/science/undergraduate/programs/':
        raise NameError()

    page = requests.get(user_link)

    soup = BeautifulSoup(page.content, 'html.parser')
    all_course_codes = []
    all_course_names = []
    all_credit_hours = []
    all_terms = []
    all_prerequisites = []
    all_corequisites = []


    section_headers = [soup.find_all("h4")[i].text for i in range(0, len(soup.find_all("h4")))]

    for text in section_headers:
        if(text.__contains__('Complementary Courses')):
            break
        target = soup.find('h4',text=text)
        for sib in target.find_next_siblings():
            if sib.name=="h4":
                break
            else:
                
                major_courses = sib.find_all(class_="program-course")
                prerequisite_courses = []
                corequisite_courses = []
                for course in major_courses:
                    #find course name for each required major course
                    major_courses = course.find_all(class_="program-course-title")
                    major_courses = [major_courses[i].contents[0][15:major_courses[i].contents[0].index(")")+1].replace("\r","") for i in range(0, len(major_courses))]
                    full_course_name = major_courses[0]
                    course_code = full_course_name[:8]
                    all_course_codes.append(course_code)
                    
                    course_name = full_course_name[9:full_course_name.index("(")]
                    
                    num_credit_hours = full_course_name[(full_course_name.index("(")+1):(full_course_name.index("(")+2)]
                    all_credit_hours.append(num_credit_hours)
                    all_course_names.append(course_name)
                    
                    prereq_term_combined_info = course.find_all("p")
                    
                    #extract Fall/Winter term info for each required major course
                    for info in prereq_term_combined_info[2:3]:
                        term_course_info = list(info.children)[0]
                        term_course_info = term_course_info[19:]
                        all_terms.append(term_course_info)
                        
                    #lastly, extract prerequisites and corequisites (or lack thereof) from each major course
            
                    for info in prereq_term_combined_info:
                        term_course_info = info.children
                        term_course_info = list(term_course_info)
                        prerequisite_info = [term_course_info for s in term_course_info if 'Prerequisite' in s]
                        corequisite_info = [term_course_info for s in term_course_info if 'Corequisite' in s]
                        for i in range(0, len(prerequisite_info)):
                            if len(prerequisite_info[i])>0:
                                for j in range(1, len(prerequisite_info[i])):
                                    if(isinstance(prerequisite_info[i][j],str) != True):
                                        prerequisite_courses.append(prerequisite_info[i][j].contents)
                        
                        for i in range(0, len(corequisite_info)):
                            if len(corequisite_info[i])>0:
                                for j in range(1, len(corequisite_info[i])):
                                    if(isinstance(corequisite_info[i][j],str) != True):
                                        corequisite_courses.append(corequisite_info[i][j].contents)
                    
                    all_prerequisites.append(', '.join(np.unique(list(np.array(prerequisite_courses).flatten()))))
                    all_corequisites.append(', '.join(np.unique(list(np.array(corequisite_courses).flatten()))))

    #End goal: CSV file with following columns:
    #Course, Prerequisites, Term, # of credit hours

    #limit analyses of prereqs/coreqs to only required major courses
    all_prerequisites_pruned = []
    for prerequisite_list in all_prerequisites:
        new_prerequisite_list = []
        for course_code in all_course_codes:
            if course_code in prerequisite_list:
                new_prerequisite_list.append(course_code)
        
        all_prerequisites_pruned.append(', '.join(np.unique(list(np.array(new_prerequisite_list).flatten()))))

    all_corequisites_pruned = []
    for corequisite_list in all_corequisites:
        new_corequisite_list = []
        for course_code in all_course_codes:
            if course_code in corequisite_list:
                new_corequisite_list.append(course_code)
        
        all_corequisites_pruned.append(', '.join(np.unique(list(np.array(new_corequisite_list).flatten()))))


    output_df = pd.DataFrame({'Course Code':all_course_codes, 'Course Name':all_course_names, 'Num Credit Hours':all_credit_hours,
                            'Terms Offered':all_terms, 'Prerequisites':all_prerequisites_pruned, 'Corequisites':all_corequisites_pruned})
    output_df.to_csv("major_plan.csv",index=False)
    #return (output_df.to_html()) old option
    if 'COMP 202' in output_df['Course Code'].values:
        output_df = output_df[output_df['Course Code'] != 'COMP 202']
        
    if 'COMP 204' in output_df['Course Code'].values:
            output_df = output_df[output_df['Course Code'] != 'COMP 204']
        
    if 'COMP 208' in output_df['Course Code'].values:
            output_df = output_df[output_df['Course Code'] != 'COMP 208']

    all_course_codes = output_df['Course Code'].values
    all_prerequisites = output_df['Prerequisites'].values
    all_corequisites = output_df['Corequisites'].values

    print(len(all_course_codes))
    all_prerequisites_pruned = []
    for prerequisite_list in all_prerequisites:
        new_prerequisite_list = []
        for course_code in all_course_codes:
            if course_code in prerequisite_list:
                new_prerequisite_list.append(course_code)
        
        all_prerequisites_pruned.append(', '.join(np.unique(list(np.array(new_prerequisite_list).flatten()))))

    all_corequisites_pruned = []
    for corequisite_list in all_corequisites:
        new_corequisite_list = []
        for course_code in all_course_codes:
            if course_code in corequisite_list:
                new_corequisite_list.append(course_code)
        
        all_corequisites_pruned.append(', '.join(np.unique(list(np.array(new_corequisite_list).flatten()))))


    output_df.loc[:,'Prerequisites'] = all_prerequisites_pruned
    output_df.loc[:,'Corequisites'] = all_corequisites_pruned
    output_df.index = [i for i in range(len(output_df))]

    major_course_code_list = output_df["Course Code"].values
    #sort major courses
    sorted_major_course_code_list = sorted(major_course_code_list,key = lambda x: x.split()[1])


    major_courses=[Course(output_df[output_df['Course Code']==course]['Course Code'].values[0],
                        int(output_df[output_df['Course Code']==course]['Num Credit Hours'].values[0]),
                        output_df[output_df['Course Code']==course]['Terms Offered'].values[0],
                        output_df[output_df['Course Code']==course]['Prerequisites'].values[0],
                        output_df[output_df['Course Code']==course]['Corequisites'].values[0]) for course in sorted_major_course_code_list]

    major_course_code_list = output_df["Course Code"].values
    #sort major courses
    sorted_major_course_code_list = sorted(major_course_code_list,key = lambda x: x.split()[1])


    major_courses=[Course(output_df[output_df['Course Code']==course]['Course Code'].values[0],
                        int(output_df[output_df['Course Code']==course]['Num Credit Hours'].values[0]),
                        output_df[output_df['Course Code']==course]['Terms Offered'].values[0],
                        output_df[output_df['Course Code']==course]['Prerequisites'].values[0],
                        output_df[output_df['Course Code']==course]['Corequisites'].values[0]) for course in sorted_major_course_code_list]


    major_course_code_list = output_df["Course Code"].values
    #sort major courses
    sorted_major_course_code_list = sorted(major_course_code_list,key = lambda x: x.split()[1])



    term='Fall'


    num_credits_remaining=12
    for course in major_courses:
        if num_credits_remaining >= 3:
            added = addCourse(course,term,sorted_major_course_code_list,
                            num_credits_remaining=num_credits_remaining, output_df=output_df)
            if added == True:
                num_credits_remaining = num_credits_remaining - int(course.ch)

    taken_sem_1 = [major_courses[i] for i in range(len(major_courses)) if major_courses[i].taken==True]
    not_taken_sem_1 = [major_courses[i] for i in range(len(major_courses)) if major_courses[i].taken==False]
    not_taken_sem_1 = [major_courses[i] for i in range(len(major_courses)) if major_courses[i].taken==False]



    term='Winter'
    num_credits_remaining=12
    for course in not_taken_sem_1:
        if num_credits_remaining >= 3:
            added = addCourse(course,term,[not_taken_sem_1[i].code for i in range(len(not_taken_sem_1))],
                            num_credits_remaining=num_credits_remaining, output_df=output_df)
        if added == True:
                num_credits_remaining = num_credits_remaining - int(course.ch)

    taken_sem_2 = [not_taken_sem_1[i] for i in range(len(not_taken_sem_1)) if not_taken_sem_1[i].taken==True]
    not_taken_sem_2 = [not_taken_sem_1[i] for i in range(len(not_taken_sem_1)) if not_taken_sem_1[i].taken==False]

    term='Fall'
    num_credits_remaining=12
    for course in not_taken_sem_2:
        if num_credits_remaining >= 3:
            added = addCourse(course,term,[not_taken_sem_2[i].code for i in range(len(not_taken_sem_2))],
                            num_credits_remaining=num_credits_remaining, output_df=output_df)
            if added == True:
                num_credits_remaining = num_credits_remaining - int(course.ch)

    taken_sem_3 = [not_taken_sem_2[i] for i in range(len(not_taken_sem_2)) if not_taken_sem_2[i].taken==True]
    not_taken_sem_3 = [not_taken_sem_2[i] for i in range(len(not_taken_sem_2)) if not_taken_sem_2[i].taken==False]


    term='Winter'
    num_credits_remaining=12
    for course in not_taken_sem_3:
        if num_credits_remaining >= 3:
            added = addCourse(course,term, [not_taken_sem_3[i].code for i in range(len(not_taken_sem_3))],
                            num_credits_remaining=num_credits_remaining, output_df=output_df)
            if added == True:
                num_credits_remaining = num_credits_remaining - int(course.ch)

    taken_sem_4 = [not_taken_sem_3[i] for i in range(len(not_taken_sem_3)) if not_taken_sem_3[i].taken==True]
    not_taken_sem_4 = [not_taken_sem_3[i] for i in range(len(not_taken_sem_3)) if not_taken_sem_3[i].taken==False]

    term='Fall'
    num_credits_remaining=12
    for course in not_taken_sem_4:
        if num_credits_remaining >= 3:
            added = addCourse(course,term, [not_taken_sem_4[i].code for i in range(len(not_taken_sem_4))],
                            num_credits_remaining=num_credits_remaining, output_df=output_df)
            if added == True:
                num_credits_remaining = num_credits_remaining - int(course.ch)

    taken_sem_5 = [not_taken_sem_4[i] for i in range(len(not_taken_sem_4)) if not_taken_sem_4[i].taken==True]
    not_taken_sem_5 = [not_taken_sem_4[i] for i in range(len(not_taken_sem_4)) if not_taken_sem_4[i].taken==False]

    term='Winter'
    num_credits_remaining=12
    for course in not_taken_sem_5:
        if num_credits_remaining >= 3:
            added = addCourse(course,term, [not_taken_sem_5[i].code for i in range(len(not_taken_sem_5))],
                            num_credits_remaining=num_credits_remaining, output_df=output_df)
            if added == True:
                num_credits_remaining = num_credits_remaining - int(course.ch)

    taken_sem_6 = [not_taken_sem_5[i] for i in range(len(not_taken_sem_5)) if not_taken_sem_5[i].taken==True]
    not_taken_sem_6 = [not_taken_sem_5[i] for i in range(len(not_taken_sem_5)) if not_taken_sem_5[i].taken==False]

    output_string = "Courses to take Fall U1: "+', '.join([taken_sem_1[i].code for i in range(len(taken_sem_1))])+'\n'+\
        "Courses to take Winter U1: "+', '.join([taken_sem_2[i].code for i in range(len(taken_sem_2))])+'\n'+\
        "Courses to take Fall U2: "+', '.join([taken_sem_3[i].code for i in range(len(taken_sem_3))])+'\n'+\
        "Courses to take Winter U2: "+', '.join([taken_sem_4[i].code for i in range(len(taken_sem_4))])+'\n'+\
        "Courses to take Fall U3: "+', '.join([taken_sem_5[i].code for i in range(len(taken_sem_5))])+'\n'+\
        "Courses to take Winter U3: "+', '.join([taken_sem_6[i].code for i in range(len(taken_sem_6))])+'\n'

    return (output_string, output_df.to_html())

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)
    