from django.shortcuts import render, redirect
from . import models
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import gemini


# Create your views here.


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

def stdpage(request):
    user_id = request.session.get('user_id')
    user_type = request.session.get('user_type')
    student = None
    if user_type == 'student' and user_id:
         try:
            student = models.Student.objects.get(id=user_id)
         except models.Student.DoesNotExist:
            return redirect('login') 
    
    return render(request,'stdpage.html', {'student': student})

def parentpage(request):
    user_id = request.session.get('user_id')
    user_type = request.session.get('user_type')
    parent = None
    if user_type == 'parent' and user_id:
         try:
            parent = models.Parent.objects.get(id=user_id)
         except models.Parent.DoesNotExist:
             return redirect('login')

    return render(request,'parentpage.html', {'parent': parent})

def tchrpage(request):
    user_id = request.session.get('user_id')
    user_type = request.session.get('user_type')
    teacher = None
    if user_type == 'teacher' and user_id:
         try:
            teacher = models.Teacher.objects.get(id=user_id)
         except models.Teacher.DoesNotExist:
             return redirect('login')
             
    return render(request,'tchrpage.html', {'teacher': teacher})

@csrf_exempt
def chat_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_message = data.get('message')
            if not user_message:
                return JsonResponse({'error': 'No message provided'}, status=400)
            
            response_text = gemini.get_gemini_response(user_message)
            return JsonResponse({'response': response_text})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request method'}, status=405)

def hrpage(request):
    user_id = request.session.get('user_id')
    user_type = request.session.get('user_type')
    hr = None
    if user_type == 'hr' and user_id:
         try:
            hr = models.HR.objects.get(id=user_id)
         except models.HR.DoesNotExist:
             return redirect('login')
             
    return render(request,'hrpage.html', {'hr': hr})

