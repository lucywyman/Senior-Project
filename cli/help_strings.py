teacher = {

    "assignment": """    assignment add <course-id> <name>=<value> [<key>=<value>]...
        add assignment with chosen name. Prompts for confirmation if name
        is not unique in course.
            [name] [begin] [end] [submission-limit | limit] [feedback-level | level]
            [late-submission] [visible] [tag]
		
    assignment view  [course-id=<course-id> | (assignment-id=<assignment-id> [<version-num>])] [tags <tags>...]
        show all assignments [for selected course], or show specific
        assignment [with selected version number]. Optionally filter by tags.
			
    assignment update <assignment-id> [<key>=<value>]...
        update selected assignment
		   
    assignment delete <assignment-id>
        delete selected assignment
        requires confirmation since action cannot be reversed. All assignment
        versions and assignment submissions linked to assignment will be
        deleted as well.""",
    
    "ce": """    ce add (<key>=<value>)...
        add common error with given key-value pairs
        [name] [text]
		
    ces view [<key>=<value>]...
        view all your entered common errors [optionally filtered by key-value pairs]
        [course-id] [course-name] [course-num] [name] [assignment-id] [test-id]
			
    ce update <ce-id> (<key>=<value>)...
        update selected common error
        brings up prompts for updated information
	
    ce delete <ce-id>...
        delete selected common error(s).

    ce link test <test-id>... to <ce-id>...
        link common error(s) to test(s).""",

    "course": """    usage: course add [<key>=<value>]...

        Adds a course with given values. If specified values result in
        non-unique course, prompt for confirmation.
    
            keys: [dept] [course-num | num] [term] [year] [course-name | name]
	
    usage: course view [<key>=<value>]...

        List all courses being taught by current user showing:
            [course-id] [dept] [course-number] [course-name] [teacher-onid]
        optionally filtered by key-value pairs:
            keys: [course-id] [dept] [course-number] [course-name] [term] [year]
                
    usage: course update <course-id> [<key>=<value>]...

        Update course by changing selected (key, value) pairs.
            keys: [dept] [course-number] [course-name] [term] [year]
                
    usage: course delete <course-id>

        Delete selected course.
        Brings up prompt asking for confirmation that action cannot be reversed
        and all assignments, assignment versions, and assignment submissions
        linked to course will be deleted as well.""",
        
    "grade": """    grade (<submission-id> | (<assignment-id> <student-id>)) <grade>
        grade is an alias of "submission update".
        updates grade on submission to given value. Submission is selected
        by submission-id or by assignment-id combined with student-id
        (automatically selects most recent submission by that student for
        that assignment-id)""",
            
    "group": """    group add <course-id> <ta-onid> <student-onid>...
        associate student(s) with selected TA for selected course. TA and
        students must already be associated with selected course. All TAs
        have privileges for all students in their courses. Grouping allows
        you to assign specific students to specific TAs for grading so the
        TAs can easily see who they need to grade (if assignments are not
        auto-graded).
			
    group view <course-id> <ta-onid>
        view students assigned to selected TA
			
    group delete <course-id> <ta-onid> [<student-onid>]...
        dis-associate student(s) with selected TA for selected course.
        Defaults to remove all students from selected TA if no student-onids
        are given.""",
    
    "student": """    student view [<key>=<value>]...
        view all students taught by user. Filter by key-value pairs.
            [course-id] [onid] [first] [last]
	
    student add <course-id> <student-onid>...
        adds student to selected course
            eg 'add student 15 doej doeja' would add user Jon Doe and Jane 
            Doe to course 15 (assuming user has permissions for group 15)

    student delete <course-id> <student-onid>...
        removes student(s) from selected course.
            eg 'delete student 15 doej doeja' would remove users Jon Doe and
            Jane Doe from course 15 (assuming user has permissions for group
            15)""",
    
    "submission": """    submission view  <assignment-id> <student-onid>
        view student's submission for given assignment and any feedback
        (including grade)

    submission update (<submission-id> | (<assignment-id> <student-id>)) <grade>
    grade - alias of "submission update"
        updates grade on submission to given value. Submission is selected
        by submission-id or by assignment-id combined with student-id
        (automatically selects most recent submission by that student for
        that assignment-id)""",
    
    "ta": """    ta view [<key>=<value>]...
        list TAs for all your courses filtered by key-value pair
            course-id] [ta-onid]
			
    ta add <ta-onid>...
        adds given username(s) to TA table. Users must be added to TA table
        before being added to courses.
			
    ta delete <ta-onid>...
        removes given username(s) from TA table. Users must be added to TA
        table before being added to courses.
    
    ta add <course-id> <ta-onid>...
        add selected TA(s) to selected course. Users must be added to TA
        table before being added to courses. TAs have privileges for courses
        they are assisting in.
			
    ta delete <course-id> <ta-onid>...
        removes selected TA(s) from selected course. If TA(s) was(were)
        assigned any students in that course, they are removed.""",
    
    "tag": """    tag <assignment-id> ( ((add | delete) <tag>...)) | view )
        For selected assignment either view all tags or, add or delete one
        or more tags.
            eg  tag 12345 add python3
                tag 43532 add python2 parsing opengl
                tag 43532 view""",
            
    "test": """    test add (<key>=<value>)...
        add test to selected assignment
            [name] [file] [points] [time-limit | time]
			
    test view [<assignment-id> [<version-number>]]
        view all tests [for selected assignment-id [and version number,
        defaults to highest if not given]]

    test update <test-id> (<key>=<value>)...
        attempts to update selected test, adds update as new test if the
        test cannot be updated (tests can't be changed if any student
        submissions reference those tests).

    test delete <test-id>
        delete selected test
        requires confirmation since action cannot be reversed"""
        
}
ta = {

    "assignment": """    assignment view [<key>=<value>]...
        show all assignments optionally filtered by key-value pairs
            [course-id] [dept] [course-num | num]""",
    
    "ce": """Instructor only command.""",

    "course": """    usage: course view [<key>=<value>]...
    
        list all courses being TAed by current user, showing:
            [course-id] [dept] [course-number] [course-name] [teacher-id]
        
        optionally filtered by key-value pairs
            keys: [course-id] [dept] [course-number] [course-name] [term] [year]""",
    
    "grade": """    grade (<submission-id> | (<assignment-id> <student-id>)) <grade>
        grade is an alias of "submission update".
        updates grade on submission to given value. Submission is selected
        by submission-id or by assignment-id combined with student-id
        (automatically selects most recent submission by that student for
        that assignment-id)""",
        
    "group": """    group view <course-id>
        view students assigned to user in selected course""",
        
    "student": """    student view [<course-id>]
        view all students [in selected course]""",
    
    "submission": """    submission view <assignment-id> <student-onid>
        view student's submission for given assignment and any feedback 
        (including grade)
        
    submission update (<submission-id> | (<assignment-id> <student-id>)) <grade>
    grade update - alias of "submission update"
        updates grade on submission to given value. Submission is selected
        by submission-id or by assignment-id combined with student-id 
        (automatically selects most recent submission by that student for 
        that assignment-id)""",
    
    "ta": """Instructor only command.""",
        
    "tag": """Instructor only command.""",
    
    "test": """Instructor only command."""   

}
student = {
    
    "assignment": """    assignment view [<key>=<value>]...
        show all assignments optionally filtered by key-value pairs
            [course-id] [dept] [course-num | num]""",
    
    "ce": """Instructor only command.""",

    "course": """    usage: course view [<key>=<value>]...
    
        list all courses being taken by current user, showing:
            [course-id] [dept] [course-number] [course-name] [teacher-id]
            
        optionally filtered by key-value pairs
            keys: [course-id] [dept] [course-number] [course-name] [term] [year]""",
            
    "grade": """Instructor only command.""",
        
    "group": """Instructor only command.""",
        
    "student": """Instructor only command.""",
    
    "submission": """    submission add <assignment-id> <filepath>
        upload file at filepath as submission to selected assignment
	
    submission view <assignment-id> [all | <submission-id>]
        view your most recent submission for given assignment and any
        available feedback (including grade) [or view all submissions for
        selected assignment or specific submission]. """,
    
    "ta": """Instructor only command.""",
        
    "tag": """Instructor only command.""",
    
    "test": """Instructor only command.""",
    
    
    
}