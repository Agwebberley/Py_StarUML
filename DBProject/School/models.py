from django.db import models


class Departments(models.Model):
    department_id = models.CharField()
    department_name = models.CharField()
    department_head = models.OneToOneField('Professors', on_delete=models.CASCADE)


class Courses(models.Model):
    course_id = models.CharField()
    course_name = models.CharField()
    department_id = models.ForeignKey('Departments', on_delete=models.CASCADE)
    professor_id = models.ForeignKey('Professors', on_delete=models.CASCADE)


class Students(models.Model):
    student_id = models.CharField()
    student_first_name = models.CharField()
    student_last_name = models.CharField()
    student_enrollment_year = models.IntegerField()


class Students_Courses(models.Model):
    enrollment_id = models.CharField()
    student_id = models.ForeignKey('Students', on_delete=models.CASCADE)
    course_id = models.ForeignKey('Courses', on_delete=models.CASCADE)


class Professors(models.Model):
    professor_id = models.CharField()
    professor_first_name = models.CharField()
    professor_last_name = models.CharField()
    department_id = models.ForeignKey('Departments', on_delete=models.CASCADE)
