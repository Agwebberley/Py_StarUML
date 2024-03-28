from django.db import models


class Departments(models.Model):
    department_id = models.CharField(max_length=10, primary_key=True)
    department_name = models.CharField(max_length=100)
    department_head = models.OneToOneField('Professors', on_delete=models.CASCADE)


class Students(models.Model):
    student_id = models.CharField(max_length=255, primary_key=True)
    student_first_name = models.CharField(max_length=100)
    student_last_name = models.CharField(max_length=100)
    student_enrollment_year = models.IntegerField()


class Students_Courses(models.Model):
    enrollment_id = models.CharField(max_length=10, primary_key=True)
    student_id = models.ForeignKey('Students', on_delete=models.CASCADE)
    course_id = models.ForeignKey('Courses', on_delete=models.CASCADE)


class Courses(models.Model):
    course_id = models.CharField(max_length=10, primary_key=True)
    course_name = models.CharField(max_length=100)
    department_id = models.CharField(max_length=255)
    professor_id = models.ForeignKey('Professors', on_delete=models.CASCADE)


class Professors(models.Model):
    professor_id = models.CharField(max_length=10, primary_key=True)
    professor_first_name = models.CharField(max_length=100)
    professor_last_name = models.CharField(max_length=100)
    department_id = models.ForeignKey('Departments', on_delete=models.CASCADE)
