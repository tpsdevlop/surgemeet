from datetime import datetime, timedelta
from googleMeet.models import Participant
from django.views.decorators.http import require_GET
from django.views.decorators.csrf import csrf_exempt
from .models import *
from django.http import HttpResponse, JsonResponse
from collections import defaultdict
from django.db.models.functions import Cast

@csrf_exempt
@require_GET
def frontpagedeatialsmethod(request):
    try:
        # Define subjects and get sessions only once
        subjects = ["HTMLCSS", "Java_Script", "SQL", "Python", "Internship"]
        sessions = Session.objects.filter(subject__in=subjects).values("id", "subject", "studentsinvited")
        sessionscount = sessions.count()
        # Get student details
        student_details = list(StudentDetails.objects.all().values(
            'StudentId',
            'firstName',
            'lastName',
            'college_Id',
            'branch',
            'CGPA',
            'score',
            'Course_Time',
            'user_Type',
            'email',
            'mob_No'
        ).order_by('StudentId'))
        
        # Filter out admin/trainer/test accounts
        # student_details = [
        #     student for student in student_details 
        #     if not any(excluded in student['StudentId'] 
        #                for excluded in ['ADMI', 'TRAI', 'TEST'])
        # ]
        
        if not student_details:
            return JsonResponse({'message': 'No data found'}, status=404)

        student_ids = [student['StudentId'] for student in student_details]

        # Fetch all required data in one go
        all_questions = list(QuestionDetails_Days.objects.filter(
            Student_id__in=student_ids
        ).values(
            'Student_id', 
            'Subject', 
            'DateAndTime',
            'Score',
            'Attempts',
            'Ans',
            'Result'
        ))

        all_days_questions = list(StudentDetails_Days_Questions.objects.filter(
            Student_id__in=student_ids
        ).values())

        all_attendance = list(Attendance.objects.filter(
            SID__in=student_ids
        ).values('SID', 'Login_time', 'Duration', 'Last_update'))

        all_rankings = list(Rankings.objects.filter(
            StudentId__in=student_ids
        ).values('StudentId', 'Course', 'Rank'))
        
        # Organize data into lookup dictionaries
        questions_data = {}
        days_questions = {}
        attendance_by_student = {}
        rankings_by_student = {}

        # Organize questions data
        for q in all_questions:
            student_id = q['Student_id']
            if student_id not in questions_data:
                questions_data[student_id] = []
            questions_data[student_id].append(q)

        # Organize days questions data
        for dq in all_days_questions:
            days_questions[dq['Student_id']] = dq

        # Organize attendance data
        for att in all_attendance:
            student_id = att['SID']
            if student_id not in attendance_by_student:
                attendance_by_student[student_id] = []
            attendance_by_student[student_id].append(att)

        # Organize rankings data
        for rank in all_rankings:
            student_id = rank['StudentId']
            if student_id not in rankings_by_student:
                rankings_by_student[student_id] = []
            rankings_by_student[student_id].append(rank)

        # Calculate user durations
        user_durations = get_total_durations_for_all_students(all_attendance)
        rankings = getRankings(all_rankings)

        # Process each student's data
        result = []
        for student in student_details:
            student_id = student['StudentId']
            
            # Create student base info
            student_info = {
                'id': student_id,
                'name': f"{student['firstName']} {student['lastName']}",
                'College': student['college_Id'],
                'Branch': student['branch'],
                'CGPA': student['CGPA'],
                'Category': student['user_Type'],
                'email': student['email'],
                'phone': student['mob_No']
            }

            # Get student's days questions
            days_questions_data = days_questions.get(student_id, {})

            # Create delay context
            delay_context = {
                'student_data': student,
                'questions_data': questions_data.get(student_id, []),
                'days_questions': days_questions_data,
                'attendance_data': attendance_by_student.get(student_id, []),
                'rankings_data': rankings_by_student.get(student_id, [])
            }
            subject_counts = get_subject_counts(questions_data.get(student_id, []))

            # Calculate scores and other metrics
            student_info.update({
                'totalScore': scorescumulation(days_questions_data),
                'overallScore': overallscore(days_questions_data)['totalscore'],
                'totalNumberOFQuesAns': {
                    'totalNumberOFQuesAns': subject_counts.get(student_id, {}),
                },
                'no_of_hrs': user_durations.get(student_id, {}),
                'Delay': delay(student_id, delay_context),
                'rank': {
                    course: ranking_data.get(student_id, {'rank': '0'})
                    for course, ranking_data in rankings.items()
                },
                'attendanceSummary': get_online_attendance(student_id, sessions,sessionscount)
            })

            result.append(student_info)

        return JsonResponse(result, safe=False)

    except Exception as e:
        print(f"Error in frontpagedeatialsmethod: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

def overallscore(student):
    try:
        easy = medium = hard = 0
        number_questions_assigned = 0
        question_list = {
            "HTMLCSS", "Java_Script", "SQL_Day_1", "SQL_Day_2", "SQL_Day_3",
            "SQL_Day_4", "SQL_Day_5", "SQL_Day_6", "SQL_Day_7", "SQL_Day_8",
            "SQL_Day_9", "SQL_Day_10", "Python_Day_1", "Python_Day_2",
            "Python_Day_3", "Python_Day_4", "Python_Day_5"
        }
        qns_lists = student['Qns_lists']
        for topic in question_list:
            questions_per_list = qns_lists.get(topic)
            if not questions_per_list:
                continue  
            number_questions_assigned += len(questions_per_list)
            for question in questions_per_list:
                if len(question) >= 4:
                    difficulty = question[-4]
                    if difficulty == "E":
                        easy += 1
                    elif difficulty == "M":
                        medium += 1
                    else:
                        hard += 1

        totalscore = (5 * easy) + (10 * medium) + (15 * hard)

        return {
            "totalscore": totalscore,
            "totalnumofquestionassigned": number_questions_assigned
        }
    
    except Exception as e:
        return {"error": str(e)}

def get_total_durations_for_all_students(attendance_records, subject=None):
    # Define date ranges for each subject
    subjects_date_ranges = {
        "HTMLCSS": ("2024-10-03", "2024-10-12"),
        "Java_Script": ("2024-10-14", "2024-11-02"),
        "SQL": ("2024-11-04", "2024-11-13"),
        "Python": ("2024-11-15", "2024-11-24"),
        "Internship": ("2024-11-26", "2024-12-31")
    }

    # Convert date ranges to aware datetime objects
    subjects_date_ranges = {
        subject_name: (
            timezone.make_aware(datetime.strptime(start, '%Y-%m-%d')), 
            timezone.make_aware(datetime.strptime(end, '%Y-%m-%d'))
        ) for subject_name, (start, end) in subjects_date_ranges.items()
    }

    student_subject_durations = defaultdict(lambda: defaultdict(float))

    for record in attendance_records:
        student_id = record['SID']
        login_time = record['Login_time']
        duration = record['Duration']

        # Track total duration for all subjects
        student_subject_durations[student_id]['All'] += duration

        for subject_name, (start_date, end_date) in subjects_date_ranges.items():
            if start_date <= login_time <= end_date:
                student_subject_durations[student_id][subject_name] += duration

    # Convert seconds to hours and round to 2 decimal places
    for student_id, durations in student_subject_durations.items():
        student_subject_durations[student_id] = {
            subject_name: round(duration / 3600, 2) 
            for subject_name, duration in durations.items()
        }

    # If subject is specified, return only that subject's data
    if subject:
        filtered_durations = {}
        for student_id, durations in student_subject_durations.items():
            if subject in durations:
                filtered_durations[student_id] = {subject: durations[subject]}
        return filtered_durations

    return student_subject_durations
def get_subject_counts(question_details):
    categories = {"HTML": 30, "Python": 200, "SQL": 150, "Java_Script": 30}
    subject_counts_by_student = {}
    for question in question_details:
        student_id = question['Student_id']
        subject = question['Subject']
        if student_id not in subject_counts_by_student:
            subject_counts_by_student[student_id] = {subject: 0 for subject in categories.keys()}
        if subject in categories:
            subject_counts_by_student[student_id][subject] = subject_counts_by_student[student_id].get(subject, 0) + 1
    for student_id, subject_counts in subject_counts_by_student.items():
        for subject, count in subject_counts.items():
            limit = categories[subject]
            subject_counts[subject] = f"{count}/{limit}"
    return subject_counts_by_student



def getRankings(rankings_data):
    try:
        # Organize rankings by course using the pre-fetched data
        organized_rankings = {}
        for rank in rankings_data:
            course = rank['Course']
            student_id = rank['StudentId']
            
            if course not in organized_rankings:
                organized_rankings[course] = {}
                
            organized_rankings[course][student_id] = {
                'rank': str(rank['Rank']),
            }
            
        return organized_rankings
    except Exception as e:
        print(f"Error in getRankings: {str(e)}")
        return {}
def scorescumulation(student):
    score_sum = 0
    score_HTMLCSS = 0
    score_breakdown = {}
    
    score_lists = student.get('Score_lists', {})
    
    for key, value in score_lists.items():
        if isinstance(value, str) and '/' in value:
            try:
                score_value = float(value.split("/")[0])
            except ValueError:
                continue
        elif isinstance(value, (int, float)):
            score_value = value
        else:
            continue
        if key in {"HTMLScore", "CSSScore"}:
            score_HTMLCSS += score_value
        else:
            score_sum += score_value
        
        score_breakdown[key] = score_value
    total_HTMLCSS_half = score_HTMLCSS / 2
    score_sum += total_HTMLCSS_half

    score_breakdown['HTMLCSSScore'] = round(total_HTMLCSS_half, 2)
    
    return {
        'Total_Score': score_sum,
        'Score_Breakdown': score_breakdown
    }

from datetime import datetime
from django.utils import timezone
from datetime import datetime
from django.utils import timezone

def delay(student_id, context):
    try:
        student_data = context['student_data']
        if not student_data:
            return {
                "HTMLCSS": {"total_days": 10, "delay": "0"},
                "Java_Script": {"total_days": 21, "delay": "0"},
                "SQL": {"total_days": 10, "delay": 0},
                "Python": {"total_days": 10, "delay": 0}
            }

        # Define course durations
        course_durations = {
            "HTMLCSS": 10,
            "Java_Script": 21,
            "SQL": 10,
            "Python": 10
        }

        course_time = student_data['Course_Time']
        days_questions = context['days_questions']
        
        ended_courses = {}
        started_courses = {}
        list_of_course = []
        current_time = datetime.now()

        # Process course times
        for course, timings in course_time.items():
            if not timings or 'Start' not in timings:  # Skip if no timing data
                continue
                
            start_time = datetime.strptime(timings['Start'], "%Y-%m-%d") if isinstance(timings['Start'], str) else timings['Start']
            end_time = datetime.strptime(timings['End'], "%Y-%m-%d") if isinstance(timings['End'], str) else timings['End']

            # Handle ongoing SQL and Python courses
            if course in ["SQL", "Python"]:
                if current_time > start_time:
                    duration = (end_time - start_time).days + 1
                    started_courses[course] = {
                        'Start Time': start_time,
                        'days': duration
                    }

            # Handle completed courses
            if end_time < current_time:
                duration = (end_time - start_time).days + 1
                ended_courses[course] = {
                    'End Time': end_time,
                    'days': duration
                }
                list_of_course.append(course)

        result = {}
        days = days_questions
        
        if days:
            # Handle completed courses (HTMLCSS and JavaScript)
            for course in list_of_course:
                total_days = ended_courses.get(course, {}).get('days', 0)
                
                if course == "HTMLCSS":
                    if "HTML" in days['Ans_lists'] and len(days['Qns_lists'][course]) == len(days['Ans_lists']["HTML"]):
                        delay = last_submit({
                            "StudentId": student_id,
                            "Course": course,
                            "End_time": ended_courses[course]['End Time']
                        })
                    else:
                        delay = compare_w_current(ended_courses[course]['End Time'])
                    
                    if type(delay) == int and delay > 0 :
                        delay -= 1
                    # print(delay)
                    result[course] = {
                        'total_days': total_days,
                        'delay': delay
                    }
                
                elif course in days['Qns_lists'] and course in days['Ans_lists']:
                    if len(days['Qns_lists'][course]) == len(days['Ans_lists'][course]):
                        delay = last_submit({
                            "StudentId": student_id,
                            "Course": course,
                            "End_time": ended_courses[course]['End Time']
                        })
                    else:
                        delay = compare_w_current(ended_courses[course]['End Time'])
                    
                    result[course] = {
                        'total_days': total_days,
                        'delay': delay
                    }
            course_total_delays = {'SQL': 0, 'Python': 0}
            
            for course in started_courses:
                start = started_courses[course]['Start Time']
                days_passed = min(compare_w_current(start), 10)
                
                for i in range(days_passed):
                    day_key = f"{course}_Day_{i+1}"
                    current = datetime.utcnow() + timedelta(hours=5, minutes=30)
                    current = datetime.strptime(str(current).split(' ')[0], "%Y-%m-%d")
                    time = start
                    existing = datetime.strptime(str(time).split(' ')[0], "%Y-%m-%d")
                    d_days = (current - existing).days
                    day_delay = d_days - i

                    # Check if the day is completed
                    if (day_key in days['Qns_lists'] and 
                        day_key in days['Ans_lists'] and 
                        len(days['Qns_lists'][day_key]) == len(days['Ans_lists'][day_key])):
                        
                        completion_time = datetime.strptime(days['End_Course'][day_key], "%Y-%m-%d") if isinstance(days['End_Course'][day_key], str) else days['End_Course'][day_key]
                        expected_completion = start + timedelta(days=(i + 1))
                        
                        if expected_completion < completion_time:
                            day_delay = (completion_time - expected_completion).days + 1
                        else:
                            day_delay = 0

                    if day_delay > 0:
                        course_total_delays[course] += 1

                    result[day_key] = {
                        "delay": day_delay,
                        "total_days": 1
                    }

            # Add summary entries for SQL and Python
            for course in ['SQL', 'Python']:
                if course in course_total_delays:
                    result[course] = {
                        "total_days": 10,
                        "delay": course_total_delays[course]
                    }

        # Format final output
        output = {
            "HTMLCSS": result.get("HTMLCSS", {"total_days": 10, "delay": "0"}),
            "Java_Script": result.get("Java_Script", {"total_days": 21, "delay": "0"})
        }
        
        # Add all other entries (SQL_Day_1, SQL_Day_2, etc.)
        for key in result:
            if key not in ["HTMLCSS", "Java_Script"]:
                output[key] = result[key]

        return output

    except Exception as e:
        print(f"Error in delay calculation: {str(e)}{student_id}")
        return {
            "HTMLCSS": {"total_days": 10, "delay": "0"},
            "Java_Script": {"total_days": 21, "delay": "0"},
            "SQL": {"total_days": 10, "delay": 0},
            "Python": {"total_days": 10, "delay": 0}
        }


def calculate_course_delays(data):
    student_id = data['StudentId']
    ended_courses = data['Ended_Courses']
    started_courses = data['Started_Courses']
    questions_data = data['questions_data']
    days = data['days_questions']
    result = {}
    course_total_delays = {'SQL': 0, 'Python': 0} 
    if days:
        for course in ['HTMLCSS', 'Java_Script']:
            if course in ended_courses:
                total_days = ended_courses[course]['days']
                if course in days.Qns_lists and (
                    (course == "HTMLCSS" and "HTML" in days.Ans_lists and len(days.Qns_lists[course]) == len(days.Ans_lists["HTML"])) or
                    (course != "HTMLCSS" and course in days.Ans_lists and len(days.Qns_lists[course]) == len(days.Ans_lists[course]))
                ):
                    delay = last_submit({
                        "StudentId": student_id,
                        "Course": course,
                        "End_time": ended_courses[course]['End Time']
                    })
                else:
                    delay = compare_w_current(ended_courses[course]['End Time'])
                
                result[course] = {
                    'total_days': total_days,
                    'delay': delay
                }
        
        for course in started_courses:
            base_course = course  # SQL or Python
            start = started_courses[course]['Start Time']
            days_passed = compare_w_current(start)
            if days_passed > 10:
                days_passed = 10
                
            for i in range(days_passed):
                day_key = f"{base_course}_Day_{i+1}"
                current = datetime.utcnow().__add__(timedelta(hours=5, minutes=30))
                current = datetime.strptime(str(current).split(' ')[0], "%Y-%m-%d")
                time = started_courses[course]['Start Time']
                existing = datetime.strptime(str(time).split(' ')[0], "%Y-%m-%d")
                d_days = (current-existing).days
                
                day_delay = d_days - i
                if day_delay > 0:  # Only count positive delays
                    course_total_delays[base_course] += 1
                
                result[day_key] = {
                    "delay": day_delay,
                    "total_days": 1
                }
        if 'SQL' in course_total_delays:
            result['SQL'] = {
                "total_days": 10,
                "delay": course_total_delays['SQL']
            }
        if 'Python' in course_total_delays:
            result['Python'] = {
                "total_days": 10,
                "delay": course_total_delays['Python']
            }
    return result


def compare_w_current(time):
    current = datetime.utcnow() + timedelta(hours=5, minutes=30)
    current = datetime.strptime(str(current).split(' ')[0], "%Y-%m-%d")
    existing = datetime.strptime(str(time).split(' ')[0], "%Y-%m-%d")
   
    return (current - existing).days

def last_submit(ex):
    student_id = ex['StudentId']
    all_submissions = QuestionDetails_Days.objects.filter(Student_id=student_id)
    recent_times = []
    course = ex['Course']
    delay = 0

    if all_submissions:
        current_course = "HTML" if course == "HTMLCSS" else course
        for submission in all_submissions:
            if submission.Subject == current_course:
                submission_time = submission.DateAndTime
                recent_times.append(submission_time)

    if recent_times:
        recent_time = max(recent_times)
        current = datetime.utcnow() + timedelta(hours=5, minutes=30)
        current = datetime.strptime(str(current).split(' ')[0], "%Y-%m-%d")
        existing = datetime.strptime(str(recent_time).split(' ')[0], "%Y-%m-%d")
        end = ex['End_time']
        end = datetime.strptime(str(end).split(' ')[0], "%Y-%m-%d")

        if (end - existing).days >= 0:
            delay = "0"
        elif (end - existing).days < 0:
            delay = (existing - end).days

    return delay
from meetsessions.models import Session
from bson.objectid import ObjectId

def get_online_attendance(student_id, sessions, sessionscount):
    try:
        subjects = ["HTMLCSS", "Java_Script", "SQL", "Python", "Internship"]
        attendance_summary = {subject: {'attended': 0, 'invited': 0} for subject in subjects}

        # Organize sessions by subject
        subject_sessions = {}
        for session in sessions:
            subject = session['subject']
            if subject not in subject_sessions:
                subject_sessions[subject] = []
            # Convert MongoDB ObjectId to string if necessary
            session_id = str(session['id']) if isinstance(session['id'], ObjectId) else str(session['id'])
            subject_sessions[subject].append(session_id)

        try:
            # MongoDB-specific query for participants
            participated_sessions = list(
                Participant.objects.filter(student_id=student_id)
                .values_list('session_id', flat=True)
            )
            
            # Convert all ObjectIds to strings
            participated_sessions = [
                str(session_id) if isinstance(session_id, ObjectId) else str(session_id)
                for session_id in participated_sessions
            ]
            
        except Exception as e:
            print(f"Error fetching participant sessions: {repr(e)}")
            return JsonResponse({
                "status": 500,
                "message": "Error fetching participant data",
                "error": str(e)
            })

        # Calculate attendance for each subject
        for subject in subjects:
            invited_sessions = subject_sessions.get(subject, [])
            # Using sets for faster comparison
            invited_set = set(invited_sessions)
            participated_set = set(participated_sessions)
            attended_count = len(invited_set.intersection(participated_set))

            attendance_summary[subject] = {
                'attended': attended_count,
                'invited': len(invited_sessions)
            }

        # Calculate overall attendance
        attendance_summary["All"] = {
            'attended': len(participated_sessions),
            'invited': sessionscount
        }

        return attendance_summary

    except Exception as e:
        print(f"General error in get_online_attendance: {repr(e)}")
        return JsonResponse({
            "status": 500,
            "message": "An error occurred while processing attendance data",
            "error": str(e)
        })