teacher = {
    "course": """usage: course add [<key>=<value>]...

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
    linked to course will be deleted as well."""

}
ta = {
    "course": """usage: course view [<key>=<value>]...
    
    list all courses you are a TA in, showing:
        [course-id] [dept] [course-number] [course-name] [teacher-id]
        
    optionally filtered by key-value pairs
        keys: [course-id] [dept] [course-number] [course-name] [term] [year]"""

}
student = {
    "course": """usage: course view [<key>=<value>]...
    
    list all courses you are currently taking, showing:
        [course-id] [dept] [course-number] [course-name] [teacher-id]
        
    optionally filtered by key-value pairs
        keys: [course-id] [dept] [course-number] [course-name] [term] [year]"""
}