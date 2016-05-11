import django.forms as forms

TERMS = (
        ('winter', 'Winter'),
        ('spring', 'Spring'),
        ('summer', 'Summer'),
        ('fall', 'Fall')
        )

DEPTS = (
        ('cs', 'Computer Science'),
        ('ece', 'Electrical Computer Engineering')
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
    num = forms.IntegerField(label='CRN', required=True)
    name = forms.CharField(max_length=255, label='Course name', required=True)
    term = forms.ChoiceField(choices=TERMS)
    year = forms.DateField()
    dept = forms.ChoiceField(choices=DEPTS, required=True)

class Assignment(forms.Form):
    name = forms.CharField(label='Assignment name', max_length=255, 
            required=True)
    begin = forms.DateTimeField(label='Beginning date (MM/DD/YY HH:MM:SS)', 
            required=True)
    end = forms.DateTimeField(label='Due date (MM/DD/YY HH:MM:SS)', 
        required=True)
    instructions = forms.CharField
    limit = forms.IntegerField
    level = forms.ChoiceField(choices=FEEDBACK)
    #late = forms.BooleanField(required=True)

class Test(forms.Form):
    name = forms.CharField(required=True, label='Test name')
    points = forms.IntegerField(required=True)
    time = forms.IntegerField(required=True)
    filepath = forms.FileField(required=True)

class Submission(forms.Form):
    subpath = forms.FileField(required=True)
    comments = forms.CharField(required=True)
