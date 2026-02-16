from django.shortcuts import render, redirect
from django.db.models import Q
from . import models
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
import gemini
from django.utils import timezone


# Create your views here.

def get_weekly_study_data(student):
    if not student:
        return [0]*7, 0
    
    # Get current date and find the start of the week (Monday)
    now = timezone.now()
    # weekday() is 0 (Mon) to 6 (Sun)
    start_of_week = now - timezone.timedelta(days=now.weekday()) 
    start_of_week = start_of_week.replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Filter test results for this week
    weekly_results = models.TestResult.objects.filter(
        student=student, 
        date__gte=start_of_week
    )
    
    # Aggregation: 7 days, Mon to Sun
    study_data = [0]*7
    for result in weekly_results:
        day_idx = result.date.weekday()
        if 0 <= day_idx < 7:
            study_data[day_idx] += result.study_time_seconds
        
    study_data_hours = [round(seconds / 3600, 2) for seconds in study_data]
    total_week_seconds = sum(study_data)
    total_week_hours = round(total_week_seconds / 3600, 2)
    
    # If no data, provide some mock data for visualization if requested, 
    # but requirement implies actual calculation.
    return study_data_hours, total_week_hours
def index(request):
    return render(request, 'index.html')

def mainpage(request):
    return render(request, 'mainpage.html')

def register(request):
    if request.method == 'POST':
        user_type = request.POST.get('user_type')
        name = request.POST.get('fullname')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        if user_type == 'student':
            user = models.Student(name=name, username=username, email=email, password=password)
            user.save()
        elif user_type == 'parent':
            childname = request.POST.get('childname')
            user = models.Parent(name=name, username=username, childname=childname, email=email, password=password)
            user.save()
        elif user_type == 'teacher':
            user = models.Teacher(name=name, username=username, email=email, password=password)
            user.save()
        elif user_type == 'hr':
            try:
                name = request.POST.get('fullname')
                username = request.POST.get('username')
                email = request.POST.get('email')
                phone = request.POST.get('phone')
                password = request.POST.get('password')
                company_details = request.POST.get('company_details')
                company_employee_id = request.POST.get('company_employee_id')
                
                # Check for existing user
                if models.HR.objects.filter(username=username).exists():
                     return render(request, 'register.html', {'error': 'Username already exists'})
                if models.HR.objects.filter(email=email).exists():
                     return render(request, 'register.html', {'error': 'Email already exists'})
                if models.HR.objects.filter(phone=phone).exists():
                     return render(request, 'register.html', {'error': 'Phone number already registered'})
                if models.HR.objects.filter(company_employee_id=company_employee_id).exists():
                     return render(request, 'register.html', {'error': 'Employee ID already registered'})
                     
                user = models.HR(
                    name=name,
                    username=username,
                    email=email,
                    phone=phone,
                    password=password,
                    company_details=company_details,
                    company_employee_id=company_employee_id
                )
                user.save()
                return redirect('login')
            except Exception as e:
                return render(request, 'register.html', {'error': str(e)})
        
        return redirect('login')

    return render(request, 'register.html')
    
def login(request):
    if request.method == 'POST':
        user_type = request.POST.get('user_type')
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        error = None
        
        if user_type == 'student':
            try:
                user = models.Student.objects.get(username=username)
                if user.password == password:
                    request.session['user_id'] = user.id
                    request.session['user_type'] = 'student'
                    # Record Login Activity
                    models.StudentActivity.objects.create(
                        student=user,
                        activity_name="Logged In",
                        activity_type="Login",
                        reference_link="/stdpage/"
                    )
                    return redirect('stdpage')
                else:
                    error = "Incorrect Password for Student"
            except models.Student.DoesNotExist:
                error = "Student Username not found"
                
        elif user_type == 'parent':
             try:
                user = models.Parent.objects.get(username=username)
                if user.password == password:
                    request.session['user_id'] = user.id
                    request.session['user_type'] = 'parent'
                    return redirect('parentpage')
                else:
                    error = "Incorrect Password for Parent"
             except models.Parent.DoesNotExist:
                error = "Parent Username not found"
                
        elif user_type == 'teacher':
             try:
                user = models.Teacher.objects.get(username=username)
                if user.password == password:
                    request.session['user_id'] = user.id
                    request.session['user_type'] = 'teacher'
                    return redirect('tchrpage')
                else:
                    error = "Incorrect Password for Teacher"
             except models.Teacher.DoesNotExist:
                error = "Teacher Username not found"
                
        elif user_type == 'hr':
             try:
                user = models.HR.objects.get(username=username)
                if user.password == password:
                    request.session['user_id'] = user.id
                    request.session['user_type'] = 'hr'
                    return redirect('hrpage')
                else:
                    error = "Incorrect Password for HR"
             except models.HR.DoesNotExist:
                error = "HR Username not found"
        
        
        # Return with the specific error message and the user_type to keep the tab active
        return render(request, 'login.html', {'error': error, 'user_type': user_type})

    return render(request,'login.html')

def logout_view(request):
    user_id = request.session.get('user_id')
    user_type = request.session.get('user_type')
    
    if user_type == 'student' and user_id:
        try:
            student = models.Student.objects.get(id=user_id)
            models.StudentActivity.objects.create(
                student=student,
                activity_name="Logged Out",
                activity_type="Login",
                reference_link=""
            )
        except models.Student.DoesNotExist:
            pass

    request.session.flush() # Clear session
    return redirect('mainpage')

def stdpage(request):
    user_id = request.session.get('user_id')
    user_type = request.session.get('user_type')
    student = None
    if user_type == 'student' and user_id:
         try:
            student = models.Student.objects.get(id=user_id)
         except models.Student.DoesNotExist:
            return redirect('login') 
    
    course_contents = models.CourseContent.objects.all().order_by('-uploaded_at')
    test_results = models.TestResult.objects.filter(student=student).order_by('-date')

    # Fetch User Activities
    top_activities = models.StudentActivity.objects.filter(student=student).order_by('-timestamp')[:3]
    
    # Calculate date 3 months ago
    three_months_ago = timezone.now() - timezone.timedelta(days=90)
    recent_activities_all = models.StudentActivity.objects.filter(student=student, timestamp__gte=three_months_ago).order_by('-timestamp')

    teachers = models.Teacher.objects.all()
    
    # Message History for Student
    message_history = []
    if student:
         message_history = models.Message.objects.filter(
            (Q(sender_id=student.id, sender_role='Student') & Q(deleted_by_sender=False)) |
            (Q(recipient_id=student.id, recipient_role='Student') & Q(deleted_by_recipient=False))
         ).order_by('-timestamp')
         
    # Certificates
    certificates = models.certificate.objects.filter(student=student)

    # Weekly Study Data
    weekly_study_data, total_week_hours = get_weekly_study_data(student)

    # Graph Data
    graph_data = test_results.order_by('date')
    graph_dates = [result.date.strftime("%d-%m-%Y") for result in graph_data]
    graph_topics = [result.course.title for result in graph_data]
    graph_marks = [result.marks for result in graph_data]
    
    avg_score = 0
    if graph_marks:
        avg_score = round(sum(graph_marks) / len(graph_marks))

    return render(request,'stdpage.html', {
        'student': student, 
        'course_contents': course_contents, 
        'test_results': test_results,
        'top_activities': top_activities,
        'recent_activities_all': recent_activities_all,
        'teachers': teachers,
        'message_history': message_history,
        'certificates': certificates,
        'graph_dates': json.dumps(graph_dates),
        'graph_marks': json.dumps(graph_marks),
        'graph_topics': json.dumps(graph_topics),

        'avg_score': avg_score,
    })

def parentpage(request):
    user_id = request.session.get('user_id')
    user_type = request.session.get('user_type')
    parent = None
    if user_type == 'parent' and user_id:
         try:
            parent = models.Parent.objects.get(id=user_id)
         except models.Parent.DoesNotExist:
             return redirect('login')

    test_results = models.TestResult.objects.none()
    certificates = []
    if parent:
        # Attempt to find student by childname
        child_student = models.Student.objects.filter(name=parent.childname).first()
        if child_student:
             test_results = models.TestResult.objects.filter(student=child_student).order_by('-date')
             certificates = models.certificate.objects.filter(student=child_student)
             
             # Weekly Study Data for Child
             weekly_study_data, total_week_hours = get_weekly_study_data(child_student)
        else:
             weekly_study_data, total_week_hours = [0]*7, 0
    else:
        weekly_study_data, total_week_hours = [0]*7, 0
    
    teachers = models.Teacher.objects.all()
    
    # # Certificates
    # certificates = models.certificate.objects.filter(student=parent)

    # Graph Data
    graph_data = test_results.order_by('date')
    graph_dates = [result.date.strftime("%d-%m-%Y") for result in graph_data]
    graph_topics = [result.course.title for result in graph_data]
    graph_marks = [result.marks for result in graph_data]

    avg_score = 0
    if graph_marks:
        avg_score = round(sum(graph_marks) / len(graph_marks))
    
    # Message History for Parent
    message_history = []
    if parent:
         message_history = models.Message.objects.filter(
            (Q(sender_id=parent.id, sender_role='Parent') & Q(deleted_by_sender=False)) |
            (Q(recipient_id=parent.id, recipient_role='Parent') & Q(deleted_by_recipient=False))
         ).order_by('-timestamp')

    return render(request,'parentpage.html', {
        'parent': parent, 
        'test_results': test_results, 
        'teachers': teachers, 
        'message_history': message_history, 
        'certificates': certificates,
        'weekly_study_data': json.dumps(weekly_study_data),
        'total_week_hours': total_week_hours,
        'graph_dates': json.dumps(graph_dates), 
        'graph_marks': json.dumps(graph_marks), 
        'graph_topics': json.dumps(graph_topics),
        'weekly_study_data': json.dumps(weekly_study_data),
        'total_week_hours': total_week_hours,
        'avg_score': avg_score,
    })

def tchrpage(request):
    user_id = request.session.get('user_id')
    user_type = request.session.get('user_type')
    teacher = None
    student_msgs = []
    parent_msgs = []
    hr_msgs = []
    student_msg_ids = []
    message_history = []
    
    if user_type == 'teacher' and user_id:
        try:
            teacher = models.Teacher.objects.get(id=user_id)
            messages = models.Message.objects.filter(recipient_id=teacher.id, recipient_role='Teacher').order_by('-timestamp')
            student_msgs = messages.filter(sender_role='Student')
            parent_msgs = messages.filter(sender_role='Parent')
            hr_msgs = messages.filter(sender_role='HR')
            
            student_msg_ids = list(student_msgs.values_list('sender_id', flat=True).distinct())
        except models.Teacher.DoesNotExist:
            return redirect('login')
             
        print(f"DEBUG: Teacher={teacher.username} (ID: {teacher.id})")
        
        # Message History for Teacher
        message_history = models.Message.objects.filter(
            (Q(sender_id=teacher.id, sender_role='Teacher') & Q(deleted_by_sender=False)) |
            (Q(recipient_id=teacher.id, recipient_role='Teacher') & Q(deleted_by_recipient=False))
        ).order_by('-timestamp')
        
    students = models.Student.objects.all()
    parents = models.Parent.objects.all()
    hr_users = models.HR.objects.all()
            
    return render(request,'tchrpage.html', {
        'teacher': teacher,
        'top_performers': models.TestResult.objects.filter(marks=15).order_by('-date'),
        'students': students,
        'parents': parents,
        'hr_users': hr_users,
        'message_history': message_history
    })

def send_message(request):
    if request.method == 'POST':
        user_id = request.session.get('user_id')
        user_type = request.session.get('user_type')
        
        if not user_id or not user_type:
            return redirect('login')
            
        # Role Map for Sender
        role_map = {
            'student': 'Student',
            'teacher': 'Teacher', 
            'parent': 'Parent',
            'hr': 'HR'
        }
        sender_role_db = role_map.get(user_type.lower(), 'Unknown')
        
        contact_username = request.POST.get('contact_username')
        contact_role = request.POST.get('contact_role')
        message_content = request.POST.get('body') # Form uses 'body'
        
        if not message_content:
             # Fallback for old forms if any
             message_content = request.POST.get('message')

        if not contact_username or not contact_role or not message_content:
            print("Missing fields in send_message")
            return redirect(request.META.get('HTTP_REFERER', 'mainpage'))

        try:
            contact_id = None
            if contact_role == 'Student':
                contact_id = models.Student.objects.get(username=contact_username).id
            elif contact_role == 'Teacher':
                contact_id = models.Teacher.objects.get(username=contact_username).id
            elif contact_role == 'Parent':
                contact_id = models.Parent.objects.get(username=contact_username).id
            elif contact_role == 'HR':
                contact_id = models.HR.objects.get(username=contact_username).id
            else:
                 print(f"Invalid role: {contact_role}")
                 return redirect(request.META.get('HTTP_REFERER', 'mainpage'))

            models.Message.objects.create(
                sender_id=user_id,
                sender_role=sender_role_db,
                recipient_id=contact_id,
                recipient_role=contact_role,
                body=message_content
            )
            return redirect(request.META.get('HTTP_REFERER', 'mainpage'))
            
        except Exception as e:
            print(f"Error sending message: {e}")
            return redirect(request.META.get('HTTP_REFERER', 'mainpage'))
            
    return redirect('mainpage')

def upload_content(request):
    if request.method == 'POST':
        user_id = request.session.get('user_id')
        user_type = request.session.get('user_type')
        
        if user_type == 'teacher' and user_id:
            try:
                teacher = models.Teacher.objects.get(id=user_id)
                title = request.POST.get('title')
                description = request.POST.get('description')
                content_type = request.POST.get('content_type')
                file = request.FILES.get('file')
                
                if title and file:
                    content = models.CourseContent(
                        title=title,
                        description=description,
                        content_type=content_type,
                        file=file,
                        teacher=teacher
                    )
                    content.save()
                    return redirect('tchrpage')
            except Exception as e:
                print(e)
                
    return redirect('tchrpage')

@csrf_exempt
def chat_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_message = data.get('message')
            if not user_message:
                return JsonResponse({'error': 'No message provided'}, status=400)
            
            response_text = ""
            options = []

            if "about website" in user_message.lower():
                response_text = "Welcome to our Online Learning Platform! We offer a wide range of courses to help you master new skills. Explore our courses, track your progress, and achieve your learning goals."
                options = ["About Courses", "Roadmap"]
            elif "about courses" in user_message.lower():
                response_text = "We offer comprehensive courses in various domains. Here are some of our popular tracks:"
                options = ["Python", "Java", "Full Stack Web Development"]
            elif "python" in user_message.lower():
                response_text = "Python Course:\n\n• Learn Python from scratch to advanced concepts.\n• Covers Data Structures, Algorithms, Web Development (Django/Flask), and Data Science basics.\n• Duration: 8 weeks\n• Level: Beginner to Intermediate"
                options = ["About Courses", "Roadmap"]
            elif "java" in user_message.lower():
                response_text = "Java Course:\n\n• Master Java programming logic and Object-Oriented Programming (OOP).\n• Includes detailed modules on Spring Boot and building robust enterprise applications.\n• Duration: 10 weeks\n• Level: Intermediate"
                options = ["About Courses", "Roadmap"]
            elif "full stack web development" in user_message.lower():
                response_text = "Full Stack Web Development:\n\n• Become a full-stack developer by learning frontend (HTML, CSS, JS, React) and backend (Node.js, Express, MongoDB).\n• Build real-world projects.\n• Duration: 12 weeks\n• Level: Advanced"
                options = ["About Courses", "Roadmap"]
            elif "roadmap" in user_message.lower():
                response_text = "Learning Roadmap:\n\n1. Start with a foundational language (Python or Java).\n2. Move to Web Development basics (HTML/CSS/JS).\n3. Choose a specialization (Full Stack, Data Science, etc.).\n4. Build projects and build your portfolio."
                options = ["About Website", "About Courses"]
            else:
                # Default Gemini response for other queries
                response_text = gemini.get_gemini_response(user_message)
                options = ["About Website", "About Courses", "Roadmap"]

            return JsonResponse({'response': response_text, 'options': options})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@csrf_exempt
def record_activity_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            student_id = request.session.get('user_id')
            user_type = request.session.get('user_type')

            if user_type == 'student' and student_id:
                student = models.Student.objects.get(id=student_id)
                activity_name = data.get('activity_name')
                activity_type = data.get('activity_type')
                reference_link = data.get('reference_link')

                models.StudentActivity.objects.create(
                    student=student,
                    activity_name=activity_name,
                    activity_type=activity_type,
                    reference_link=reference_link
                )
                
                # If viewing a course, record the start time in session
                if activity_type == 'Course' and reference_link:
                    try:
                        # reference_link is usually the course ID
                        course_id = reference_link
                        request.session[f'study_start_{course_id}'] = timezone.now().isoformat()
                    except Exception as e:
                        print(f"Error saving study start time: {e}")
                
                return JsonResponse({'status': 'success'})
            return JsonResponse({'error': 'Unauthorized'}, status=401)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid method'}, status=405)

def hrpage(request):
    user_id = request.session.get('user_id')
    user_type = request.session.get('user_type')
    hr = None
    if user_type == 'hr' and user_id:
         try:
            hr = models.HR.objects.get(id=user_id)
         except models.HR.DoesNotExist:
             return redirect('login')
             
    top_performers = models.TestResult.objects.filter(marks=15).order_by('-date')
    
    students = models.Student.objects.all()
    teachers = models.Teacher.objects.all()
    
    # Message History for HR
    message_history = []
    if hr:
         message_history = models.Message.objects.filter(
            (Q(sender_id=hr.id, sender_role='HR') & Q(deleted_by_sender=False)) |
            (Q(recipient_id=hr.id, recipient_role='HR') & Q(deleted_by_recipient=False))
         ).order_by('-timestamp')
    
    return render(request,'hrpage.html', {
        'hr': hr, 
        'top_performers': top_performers, 
        'students': students, 
        'teachers': teachers,
        'message_history': message_history
    })

def take_test(request, course_id):
    user_id = request.session.get('user_id')
    user_type = request.session.get('user_type')
    
    if user_type != 'student' or not user_id:
        return redirect('login')
        
    try:
        course = models.CourseContent.objects.get(id=course_id)
        
        # Check if test already exists in session to avoid re-generating on refresh
        # (Optional, but good for stability)
        # For now, let's regenerate for fresh test
        
        try:
            # Generate test using Gemini
            json_response = gemini.generate_test_questions(course.title, course.description)
            
            # Parse JSON - handle potential markdown code blocks
            if "```json" in json_response:
                 json_response = json_response.replace("```json", "").replace("```", "")
            
            test_data = json.loads(json_response)
            questions = test_data.get('questions', [])
        except Exception as e:
            print(f"API Error generating test (Using fallback): {e}")
            # Fallback questions for testing flow
            # Optionally add an error message to context about fallback mode if desired, 
            # but user asked for "without any error". 
            
        # Store in session for grading and review
        request.session[f'test_questions_{course_id}'] = questions
        
        return render(request, 'test.html', {'course': course, 'questions': questions})
    except models.CourseContent.DoesNotExist:
        return render(request, 'test.html', {'error': f"Course with ID {course_id} not found."})
    except Exception as e:
        print(f"Critical System Error: {e}")
        return render(request, 'test.html', {'error': f"Critical System Error: {str(e)}"})
        
def submit_test(request, course_id):
    if request.method == 'POST':
        user_id = request.session.get('user_id')
        user_type = request.session.get('user_type')
        
        if user_type != 'student' or not user_id:
            return redirect('login')

        try:
            student = models.Student.objects.get(id=user_id)
            course = models.CourseContent.objects.get(id=course_id)
            
            # Retrieve questions from session
            questions = request.session.get(f'test_questions_{course_id}', [])
            
            score = 0
            total_questions = len(questions) if questions else 15
            
            user_answers = {}
            
            for q in questions:
                q_type = q.get('type')
                q_id = str(q.get('id'))
                
                if q_type == 'msq':
                    selected_answer = request.POST.getlist(f'question_{q_id}')
                    correct_answer = q.get('correct_answer')
                    
                    # Ensure correct_answer is a list for comparison
                    if isinstance(correct_answer, str):
                        correct_answer = [correct_answer]
                        
                    # Compare sets for order-independent equality
                    if set(selected_answer) == set(correct_answer):
                        score += 1
                        
                    q['user_selected'] = selected_answer
                    q['is_correct'] = (set(selected_answer) == set(correct_answer))
                else:
                    # MCQ or Coding
                    selected_answer = request.POST.get(f'question_{q_id}')
                    correct_answer = q.get('correct_answer')
                    
                    if selected_answer == correct_answer:
                        score += 1
                        
                    q['user_selected'] = selected_answer
                    q['is_correct'] = (selected_answer == correct_answer)

            # Calculate study duration
            duration_seconds = 0
            start_time_iso = request.session.get(f'study_start_{course_id}')
            if start_time_iso:
                try:
                    start_time = timezone.datetime.fromisoformat(start_time_iso)
                    # Handle naive/aware datetime comparison if necessary
                    if timezone.is_aware(start_time):
                        duration = timezone.now() - start_time
                    else:
                        duration = timezone.datetime.now() - start_time
                    duration_seconds = int(duration.total_seconds())
                    
                    # Clear session variable after use
                    del request.session[f'study_start_{course_id}']
                except Exception as e:
                    print(f"Error calculating duration: {e}")

            # Save result
            models.TestResult.objects.create(
                student=student,
                course=course,
                marks=score,
                total_marks=total_questions,
                study_time_seconds=duration_seconds
            )

            # Record Test Completion Activity
            models.StudentActivity.objects.create(
                student=student,
                activity_name=f"Completed Test: {course.title}",
                activity_type="Test",
                reference_link=f"/submit_test/{course.id}/" # Or result page if available
            )
            
            
            return render(request, 'test_result.html', {
                'course': course, 
                'score': score, 
                'total': total_questions,
                'percentage': (score/total_questions)*100 if total_questions > 0 else 0,
                'questions': questions # Pass back for review
            })
            
        except Exception as e:
            print(f"Error submitting test: {e}")
            return redirect('stdpage')
            
    return redirect('stdpage')

# --- Messaging System APIs ---

@csrf_exempt
def get_messages_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            # Normalize user_role from session (e.g. 'student' -> 'Student')
            raw_user_role = request.session.get('user_type', '')
            user_id = request.session.get('user_id')
            
            if not user_id or not raw_user_role:
                 print("API Error: Unauthorized (Missing session data)")
                 return JsonResponse({'error': 'Unauthorized'}, status=401)
            
            # Map session role to DB role format
            role_map = {
                'student': 'Student',
                'teacher': 'Teacher', 
                'parent': 'Parent',
                'hr': 'HR'
            }
            db_user_role = role_map.get(raw_user_role.lower(), 'Unknown')

            contact_id = data.get('contact_id')
            contact_role = data.get('contact_role') # Expecting Capitalized from frontend
            
            print(f"DEBUG API: User={user_id}({db_user_role}) fetching with Contact={contact_id}({contact_role})")
            
            # (Sender = Me AND Recipient = Contact) OR (Sender = Contact AND Recipient = Me)
            # AND not deleted by me
            messages = models.Message.objects.filter(
                (Q(sender_id=user_id, sender_role=db_user_role, recipient_id=contact_id, recipient_role=contact_role) & Q(deleted_by_sender=False)) |
                (Q(sender_id=contact_id, sender_role=contact_role, recipient_id=user_id, recipient_role=db_user_role) & Q(deleted_by_recipient=False))
            ).order_by('timestamp')
            
            print(f"DEBUG API: Found {messages.count()} messages")
            
            # Mark as read where I am recipient
            messages.filter(recipient_id=user_id, recipient_role=db_user_role, is_read=False).update(is_read=True)
            
            results = []
            for m in messages:
                results.append({
                    'id': m.id,
                    'body': m.body,
                    'timestamp': m.timestamp.isoformat(),
                    'is_sender': (m.sender_id == user_id and m.sender_role == db_user_role),
                    'is_read': m.is_read
                })
                
            return JsonResponse({'messages': results})
        except Exception as e:
            print(e)
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid method'}, status=405)


@csrf_exempt
def send_message_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            raw_user_role = request.session.get('user_type', '')
            user_id = request.session.get('user_id')
            
            if not user_id:
                return JsonResponse({'error': 'Unauthorized'}, status=401)

            role_map = {
                'student': 'Student',
                'teacher': 'Teacher', 
                'parent': 'Parent',
                'hr': 'HR'
            }
            db_user_role = role_map.get(raw_user_role.lower(), 'Unknown')
            
            contact_id = data.get('contact_id')
            contact_username = data.get('contact_username') # New field
            contact_role = data.get('contact_role')
            body = data.get('body')
            
            if not body:
                return JsonResponse({'error': 'Empty message'}, status=400)
            
            # Username Lookup Logic
            if contact_username and contact_role:
                try:
                    if contact_role == 'Student':
                        target_user = models.Student.objects.get(username=contact_username)
                    elif contact_role == 'Teacher':
                        target_user = models.Teacher.objects.get(username=contact_username)
                    elif contact_role == 'Parent':
                        target_user = models.Parent.objects.get(username=contact_username)
                    elif contact_role == 'HR':
                        target_user = models.HR.objects.get(username=contact_username)
                    else:
                        return JsonResponse({'error': 'Invalid role'}, status=400)
                    
                    contact_id = target_user.id
                except Exception:
                    return JsonResponse({'error': f'{contact_role} username not found'}, status=404)
            
            if not contact_id:
                 return JsonResponse({'error': 'Recipient not specified'}, status=400)

            msg = models.Message.objects.create(
                sender_id=user_id,
                sender_role=db_user_role,
                recipient_id=contact_id,
                recipient_role=contact_role,
                body=body
            )
            
            return JsonResponse({'status': 'success', 'msg_id': msg.id})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid method'}, status=405)


@csrf_exempt
def delete_message_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            raw_user_role = request.session.get('user_type', '')
            user_id = request.session.get('user_id')
            
            if not user_id: return JsonResponse({'error': 'Unauthorized'}, status=401)
            
            role_map = {
                'student': 'Student',
                'teacher': 'Teacher', 
                'parent': 'Parent',
                'hr': 'HR'
            }
            db_user_role = role_map.get(raw_user_role.lower(), 'Unknown')
            
            msg_id = data.get('message_id')
            msg = models.Message.objects.get(id=msg_id)
            
            # Check permission
            is_sender = (msg.sender_id == user_id and msg.sender_role == db_user_role)
            is_recipient = (msg.recipient_id == user_id and msg.recipient_role == db_user_role)
            
            if not (is_sender or is_recipient):
                return JsonResponse({'error': 'Forbidden'}, status=403)
                
            # Soft Delete
            if is_sender:
                msg.deleted_by_sender = True
            if is_recipient:
                msg.deleted_by_recipient = True
                
            msg.save()
            
            # Hard Delete Check
            if msg.deleted_by_sender and msg.deleted_by_recipient:
                msg.delete()
                
            return JsonResponse({'status': 'success'})
        except models.Message.DoesNotExist:
            return JsonResponse({'error': 'Not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid method'}, status=405)

