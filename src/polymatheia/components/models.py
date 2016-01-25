from django.contrib.gis.db import models
import os

class Department(models.Model):
    """
    """

class Teacher(models.Model):
    """
    """

class TA(models.Model):
    """
    """

class Student(models.Model):
    """
    """

class Course(models.Model):
    """
    This is a comment
    """
    course_num = models.PositiveIntegerField()
    name = models.TextField()
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
    filepath = models.FileField(upload_to=user_directory)
    comments = models.TextField()
    date_submitted = models.DateTimeField(auto_now_add=True)
    grade = models.TextField()

class CommonErrors(models.Model):
    """
    """
