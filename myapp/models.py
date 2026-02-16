from django.db import models

# Create your models here.
class Student(models.Model):
    name = models.CharField(max_length=100)
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100)

    def __str__(self):
        return self.username

class Parent(models.Model):
    name = models.CharField(max_length=100)
    username = models.CharField(max_length=100, unique=True)
    childname = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100)

    def __str__(self):
        return self.username

class Teacher(models.Model):
    name = models.CharField(max_length=100)
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, unique=True, null=True, blank=True)
    password = models.CharField(max_length=100)

    def __str__(self):
        return self.username

class HR(models.Model):
    name = models.CharField(max_length=100)
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, unique=True, null=True, blank=True)
    password = models.CharField(max_length=100)
    company_details = models.TextField()
    company_employee_id = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.username

class CourseContent(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    content_type = models.CharField(max_length=50) # Video, PDF, etc.
    file = models.FileField(upload_to='course_content/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.title

class Message(models.Model):
    sender_id = models.IntegerField(default=0)
    sender_role = models.CharField(max_length=50, default="Unknown") # 'Student', 'Teacher', 'HR', 'Parent'
    recipient_id = models.IntegerField(default=0)
    recipient_role = models.CharField(max_length=50, default="Unknown")
    body = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    # Soft delete flags
    deleted_by_sender = models.BooleanField(default=False)
    deleted_by_recipient = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.sender_role} -> {self.recipient_role}: {self.body[:50]}"

class TestResult(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(CourseContent, on_delete=models.CASCADE)
    marks = models.IntegerField()
    total_marks = models.IntegerField(default=15)
    date = models.DateTimeField(auto_now_add=True)
    study_time_seconds = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.student.username} - {self.course.title} - {self.marks}/{self.total_marks}"

class StudentActivity(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    activity_name = models.CharField(max_length=255)
    activity_type = models.CharField(max_length=50) # 'Login', 'Course', 'Test'
    reference_link = models.CharField(max_length=255, blank=True, null=True) # URL or ID
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.username} - {self.activity_name} ({self.timestamp})"


class certificate(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    course = models.ForeignKey(CourseContent, on_delete=models.CASCADE)
    certificate = models.FileField(upload_to='certificates/')
    date = models.DateTimeField(auto_now_add=True)
    total_marks = models.IntegerField(default=15)


    def __str__(self):
        return f"{self.student.username} - {self.course.title}"

