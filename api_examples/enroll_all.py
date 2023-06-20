import requests 


username = 'student1'
password = 'testpass123'
base_url = 'http://127.0.0.1:8000/api/'


# retrieve all courses
r = requests.get(f'{base_url}courses/')
courses = r.json()

avaible_courses = ', '.join([course['title'] for course in courses])
print(f'Avaible courses: {avaible_courses}')



for course in courses:
    course_id = course['id']
    course_title = course['title']
    r = requests.post(f'{base_url}courses/{course_id}/enroll/',
                      auth=(username, password))
    if r.status_code == 200:
        # successful request
        print(f'Successfully enroll in {course_title}')
    else:
        print(f'Unsuccessfully enroll in {course_title}')

