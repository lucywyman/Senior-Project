from django.contrib.gis.db import models
import os

class Teacher(models.Model):


class TA(models.Model):

class Student(models.Model):


class Course(models.Model):
    """
    This is a comment
    """
    course_num: models.PositiveIntegerField()
    name: models.TextField()
    term: models.TextField()
    year: models.DateField()
    dept: models.ForeignKey('Department', null=False, blank=False)

class Assignment(models.Model):
    name: models.TextField()
    begin_date: models.DateTimeField()
    end_date: models.DateTimeField()
    instructions: models.TextField()
    submission_limit: models.PositiveIntegerField()
    feedback_level: models.?
    late: models.Boolean
    

class Test(models.Model):
    test_case = models.PositiveIntegerField()
    points = models.PositiveIntegerField()
    time_limit = models.PositiveIntegerField()
    assignment = models.ForeignKey('Assignment', null=True, blank=True)
    common_errors = models.ForeignKey('CommonErrors', null=True, blank=True)
    result = models.TextArea()


class Submission(models.Model):
    def filename(self):
        return os.path.basename(self.file.name)

    student = models.TextField()
    filepath = models.FileField(upload_to=$USER+'submissions')
    comments = models.TextArea()
    date_submitted = models.DateTimeField(auto_now_add=True)
    grade = models.TextField()
