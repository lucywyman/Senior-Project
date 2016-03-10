import django.forms as forms
from polymatheia.components.models import (User, Teacher, TA, Student, Course, 
		Assignment, Test, Submission)

TERMS = (
		('W', 'Winter'),
		('Sp', 'Spring'),
		('Su', 'Summer'),
		('F', 'Fall')
		)

DEPTS = (
		('CS', 'Computer Science'),
		('ECE', 'Electrical Computer Engineering')
		)

TYPES = (
		('P', 'Professor'),
		('TA', 'TA'),
		('S', 'Student')
		)

## TODO How to specify teacher vs. student vs. TA

class NewUser(forms.Form):
	first_name = forms.CharField(label='First Name', required=True)
	last_name = forms.CharField(label='Last Name', required=True)
	##TODO ask to re-enter onid
	onid = forms.CharField(label='ONID ID Number', required=True)
	usertype = forms.ChoiceField(choices=TYPES,
			required=True, label='Are you a Professor, TA, or student?')
	password = forms.CharField(label='Password', required=True, widget=forms.PasswordInput)
	password2 = forms.CharField(label='Re-enter Password', required=True, widget=forms.PasswordInput)

class Course(forms.Form):
	course_num = forms.IntegerField(label='CRN', required=True)
	name = forms.CharField(max_length=255, label='Course name', required=True)
	term = forms.ChoiceField(choices=TERMS)
	year = forms.DateField()
	dept = forms.ChoiceField(choices=DEPTS, required=True)

class Assignment(forms.Form):
	name = forms.CharField(max_length=255, required=True)
	# Other attributes may be necessary
	begin_date = forms.DateTimeField
	end_date = forms.DateTimeField
	instructions = forms.CharField
	submission_limit = forms.IntegerField
	feedback_level = forms.ChoiceField(choices=[1, 2, 3])
	late = forms.BooleanField

class Test(forms.Form):
	test_case = forms.IntegerField
	points = forms.IntegerField
	time_limit = forms.IntegerField
	assignment = forms.CharField(max_length=255)
	result = forms.CharField

class Submission(forms.Form):
	# Modify type
	sfile = forms.FileField
	comments = forms.CharField
