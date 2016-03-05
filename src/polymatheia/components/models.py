from django.contrib.gis.db import models
import os

class Department(models.Model):
    """
    The Department model holds information about each relevant department 
    that has classes at Oregon state. For example, the Computer Science 
    department has 'CS' prefixed to their classes, which is relevant to 
    determining the class id.
    """
    name = models.TextField()


class User(models.Model):
    """
    """
    first_name = models.TextField()
    last_name = models.TextField()
    onid = models.TextField()
    password = models.CharField(max_length=1024)


class Teacher(models.Model):
    """
    """
    classes = models.ManyToManyField('Course')
    user = models.ForeignKey('User', null=False, blank=False)

class TA(models.Model):
    """
    """
    classes = models.ManyToManyField('Course')
    user = models.ForeignKey('User', null=False, blank=False)

class Student(models.Model):
    """
    """
    user = models.ForeignKey('User', null=False, blank=False)


class Course(models.Model):
    """
    The course model describes a course at Oregon state.

    This includes the course number (ie. 312 for CS312)
    the name (ie. Linux System Administration)
    the crn (ie. 98765)
    the term (ie. Winter)
    the year (ie. 2016)
    the department (ie. CS)
    """
    course_num = models.PositiveIntegerField()
    name = models.TextField()
    crn = models.PositiveIntegerField()
    term = models.TextField()
    year = models.DateField()
    dept = models.ForeignKey('Department', null=False, blank=False)

class Assignment(models.Model):
    name = models.TextField()
    begin_date = models.DateTimeField()
    end_date = models.DateTimeField()
    instructions = models.TextField()
    submission_limit = models.PositiveIntegerField()
    # Not sure what this should be
    feedback_level = models.PositiveIntegerField()
    late = models.BooleanField()
    

class Test(models.Model):
    test_case = models.PositiveIntegerField()
    points = models.PositiveIntegerField()
    time_limit = models.PositiveIntegerField()
    assignment = models.ForeignKey('Assignment', null=True, blank=True)
    common_errors = models.ForeignKey('CommonErrors', null=True, blank=True)
    result = models.TextField()


class Submission(models.Model):
    # TODO define media root
    def user_directory(self):
        return 'user_{0}/{1}'.format(instance.user.id, filename)+'/submissions'
    student = models.TextField()
    #filepath = models.FileField(upload_to=user_directory)
    comments = models.TextField()
    date_submitted = models.DateTimeField(auto_now_add=True)
    grade = models.TextField()

class CommonErrors(models.Model):
    """
    """
