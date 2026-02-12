from django.shortcuts import render, redirect
from . import models


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
        
        return redirect('login')

    return render(request, 'register.html')
    
def login(request):
    if request.method == 'POST':
        user_type = request.POST.get('user_type')
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = None
        if user_type == 'student':
            try:
                user = models.Student.objects.get(username=username, password=password)
                if user:
                    request.session['user_id'] = user.id
                    request.session['user_type'] = 'student'
                    return redirect('stdpage')
            except models.Student.DoesNotExist:
                pass
        elif user_type == 'parent':
             try:
                user = models.Parent.objects.get(username=username, password=password)
                if user:
                    request.session['user_id'] = user.id
                    request.session['user_type'] = 'parent'
                    return redirect('parentpage')
             except models.Parent.DoesNotExist:
                pass
        elif user_type == 'teacher':
             try:
                user = models.Teacher.objects.get(username=username, password=password)
                if user:
                    request.session['user_id'] = user.id
                    request.session['user_type'] = 'teacher'
                    return redirect('tchrpage')
             except models.Teacher.DoesNotExist:
                pass
        
        # If user not found or password incorrect
        return render(request, 'login.html', {'error': 'Invalid Credentials'})

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