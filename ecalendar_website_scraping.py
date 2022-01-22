
from types import NoneType
import requests
import numpy as np 
import scipy
from bs4 import BeautifulSoup
from bs4 import SoupStrainer
from itertools import chain
import re
import pandas as pd
from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/")
def index():
    
    user_link: str = request.args.get("Enter a link to the ECalendar for Your Major:")
    if user_link == None: 
        info = ""
    elif user_link[:79] != 'https://www.mcgill.ca/study/2021-2022/faculties/science/undergraduate/programs/':
        info = ""
        raise NameError()
        
    else:
        info = get_info(user_link)
    return render_template("mcdegreeplanning.html") + info


@app.route("/")
def get_info(user_link):    
    

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
    output_df = pd.DataFrame({'Course Code':all_course_codes, 'Course Name':all_course_names, 'Num Credit Hours':all_credit_hours,
                            'Terms Offered':all_terms, 'Prerequisites':all_prerequisites, 'Corequisites':all_corequisites})
    output_df.to_csv("major_plan.csv",index=False)
    return (output_df)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8080, debug=True)

