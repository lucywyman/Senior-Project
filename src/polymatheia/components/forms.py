from django.forms as forms
from polymatheia.components.models import (Teacher, TA, Student, Course, 
        Assignment, Test)

TERMS = (
        'Winter',
        'Spring',
        'Summer',
        'Fall'
        )

class Course(forms.ModelForm):

    class Meta:
        model = Course
        exclude = []
        widgets = {
                'course_num': forms.PositiveIntegerField(
                    attrs={'required': 'true'}),
                'name': forms.TextInput(attrs={'required': 'true'}),
                'term': forms.Select(choices=TERMS, attrs={'required':'true'}),
                'year': forms.DateField(),
                'dept': forms.something
                }


class Assignment(forms.ModelForm):

    class Meta:
        model = Assignment
        exclude = []
        widgets = {
                'name': forms.TextInput(attrs={'required': 'true'}),
                # Other attributes may be necessary
                'begin_date': forms.DateTimeField,
                'end_date': forms.DateTimeField,
                'instructions': forms.TextArea,
                'submission_limit': forms.PositiveIntegerField,
                'feedback_level': forms.wut,
                'late': forms.Boolean
                }


class Test(forms.ModelForm):

    class Meta:
        model = Test
        exclude = []
        widgets = {
                'test_case': forms.PositiveIntegerField,
                'points': forms.PositiveIntegerField,
                'time_limit': forms.PositiveIntegerField
                'assignment': forms.list?
                'result': forms.TextArea
                }

class Submission(forms.Modelform):

    class Meta:
        model = Submission
        exclude = []
        widgets = {
                # Modify type
                'file': forms.FileField,
                'comments': forms.TextArea,
                }

