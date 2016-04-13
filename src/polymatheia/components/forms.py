import django.forms as forms

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
FEEDBACK = (
        ('1', 0),
        ('2', 1),
        ('3', 2)
        )

class User(forms.Form):
    first_name = forms.CharField(label='First Name', required=True)
    last_name = forms.CharField(label='Last Name', required=True)
    onid = forms.CharField(label='ONID ID Number (932000000)', required=True)
    onid_name = forms.CharField(label='ONID Username (wymanl)', required=True)
    password = forms.CharField(label='Password', required=True, 
            widget=forms.PasswordInput)
    password2 = forms.CharField(label='Re-enter Password', required=True, 
            widget=forms.PasswordInput)

class Course(forms.Form):
    course_num = forms.IntegerField(label='CRN', required=True)
    name = forms.CharField(max_length=255, label='Course name', required=True)
    term = forms.ChoiceField(choices=TERMS)
    year = forms.DateField()
    dept = forms.ChoiceField(choices=DEPTS, required=True)

class Assignment(forms.Form):
    name = forms.CharField(label='Assignment name', max_length=255, 
            required=True)
    course_id = forms.CharField(max_length=255, required=True)
    #begin = forms.DateTimeField(label='Beginning date (MM/DD/YYYY HH:MM:SS)', 
    #end = forms.DateTimeField(label='Due date (MM/DD/YYYY HH:MM:SS)', 
    #instructions = forms.CharField
    limit = forms.IntegerField
    level = forms.ChoiceField(choices=FEEDBACK)
    #late = forms.BooleanField(required=True)

class Test(forms.Form):
    test_case = forms.IntegerField(required=True, label='Test name')
    points = forms.IntegerField(required=True)
    time_limit = forms.IntegerField(required=True)
    assignment = forms.CharField(max_length=255, required=True)
    result = forms.BooleanField(required=True)

class Submission(forms.Form):
    sfile = forms.FileField(required=True)
    comments = forms.CharField(required=True)
