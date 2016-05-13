commands = {
    "assignment": {
        "add":      {
            "access":   {
                "teacher":  True,
                "ta":       False,
                "student":  False,
                },

            "required": ['course-id', 'name'],

            "required2": [],

            "optional": ['begin', 'end', 'late', 'level', 'limit', 'name', 'tags'],

            "help":     "Adds assignment to selected course with given values.",

            },

        "view":     {
            "access":   {
                "teacher":  True,
                "ta":       True,
                "student":  True,
                },

            "required": [],

            "required2": [],

            "optional": ['assignment-id', 'course-id', 'dept',  'num', 'tags', 'teacher', 'term', 'version', 'year'],

            "help":     "Show all assignments, optionally filtered by optional values.",

            },

        "update":   {
            "access":   {
                "teacher":  True,
                "ta":       False,
                "student":  False,
                },

            "required": ['assignment-id'],

            "required2": [],

            "optional": ['begin', 'course-id', 'end', 'late', 'level', 'limit', 'name', 'tags'],

            "help":     "Update selected assignment with chosen values.",

            },

        "delete":   {
            "access":   {
                "teacher":  True,
                "ta":       False,
                "student":  False,
                },

            "required": ['assignment-id'],

            "required2": [],

            "optional": [],

            "help":     "Delete selected assignment. Requires user confirmation.",

            "confirmation": "Deleting this assignment will delete all versions of it and all student submissions for it.",

            },
        },


    "ce": {
        "add":      {
            "access":   {
                "teacher":  True,
                "ta":       False,
                "student":  False,
                },

            "required": ['name', 'text'],

            "required2": [],

            "optional": [],

            "help":     "Add common error with specified values.",

            },

        "view":     {
            "access":   {
                "teacher":  True,
                "ta":       False,
                "student":  False,
                },

            "required": [],

            "required2": [],

            "optional": ['assignment-id', 'ce-id', 'course-id', 'name', 'test-id', 'version'],

            "help":     "View all common errors [optionally filtered by key-value pairs].",

            },

        "update":   {
            "access":   {
                "teacher":  True,
                "ta":       False,
                "student":  False,
                },

            "required": ['ce-id'],

            "required2": [],

            "optional": ['name', 'text'],

            "help":     "Update a common error with chosen values.",

            },

        "delete":   {
            "access":   {
                "teacher":  True,
                "ta":       False,
                "student":  False,
                },

            "required": ['ce-id'],

            "required2": [],

            "optional": [],

            "help":     "Delete selected common error(s).",

            "confirmation": "Deleting this/these common errors will permanenty remove them from the database.",

            },

        "link":   {
            "access":   {
                "teacher":  True,
                "ta":       False,
                "student":  False,
                },

            "required": ['ce-id', 'test-id'],

            "required2": [],

            "optional": [],

            "help":     "Link selected common error(s) to selected test(s).",

            },
        },


    "course": {
        "add":      {
            "access":   {
                "teacher":  True,
                "ta":       False,
                "student":  False,
                },

            "required": ['name'],

            "required2": [],

            "optional": ['dept', 'num', 'term', 'year'],

            "help":     "Adds a course with specified values.",

            },

        "view":     {
            "access":   {
                "teacher":  True,
                "ta":       True,
                "student":  True,
                },

            "required": [],

            "required2": [],

            "optional": ['course-id', 'dept', 'name', 'num', 'teacher', 'term', 'year'],

            "help":     "List all courses, optionally filtered by selected values.",

            },

        "update":   {
            "access":   {
                "teacher":  True,
                "ta":       False,
                "student":  False,
                },

            "required": ['course-id'],

            "required2": [],

            "optional": ['dept', 'name', 'num', 'term', 'year'],

            "help":     "Update course by changing selected values.",

            },

        "delete":   {
            "access":   {
                "teacher":  True,
                "ta":       False,
                "student":  False,
                },

            "required": ['course-id'],

            "required2": [],

            "optional": [],

            "help":     "Delete selected course.",

            "confirmation": "Deleting this course will permanenty remove all assignments, assignment versions, and submissions associated with this course.",

            },
        },


    "grade": {
        "add":      {
            "access":   {
                "teacher":  False,
                "ta":       False,
                "student":  False,
                },

            "required": [],

            "required2": [],

            "optional": [],

            "help":     "",

            },

        "view":     {
            "access":   {
                "teacher":  False,
                "ta":       False,
                "student":  False,
                },

            "required": [],

            "required2": [],

            "optional": [],

            "help":     "",

            },

        "update":   {
            "access":   {
                "teacher":  True,
                "ta":       True,
                "student":  False,
                },

            "required": ['submission', 'grade'],

            "required2": ['assignment-id', 'student', 'grade'],

            "optional": [],

            "help":     "Grade update is an alias of submission update. Updates grade of submission. A specific submission can be selected with the submission key, or by using assignment-id and student keys to select a student's most recent submission for the assignment.",

            },

        "delete":   {
            "access":   {
                "teacher":  False,
                "ta":       False,
                "student":  False,
                },

            "required": [],

            "required2": [],

            "optional": [],

            "help":     "",

            "confirmation": "Deleting this  will permanenty remove ",

            },
        },

    "group": {
        "add":      {
            "access":   {
                "teacher":  True,
                "ta":       False,
                "student":  False,
                },

            "required": ['course-id', 'ta', 'student'],

            "required2": [],

            "optional": [],

            "help":     "Associate student(s) with selected TA for selected course. TA and students must already be associated with selected course. All TAs have privileges for all students in their courses.",

            },

        "view":     {
            "access":   {
                "teacher":  True,
                "ta":       True,
                "student":  False,
                },

            "required": ['ta'],

            "required2": ['course-id'],

            "optional": ['ta','course-id', 'student'],

            "help":     "View students assigned to selected TA",

            },

        "update":   {
            "access":   {
                "teacher":  False,
                "ta":       False,
                "student":  False,
                },

            "required": [],

            "required2": [],

            "optional": [],

            "help":     "",

            },

        "delete":   {
            "access":   {
                "teacher":  True,
                "ta":       False,
                "student":  False,
                },

            "required": ['course-id', 'ta'],

            "required2": [],

            "optional": ['student'],

            "help":     "Dis-associate student(s) with selected TA for selected course. Removes all students from selected TA for selected course if no students are listed.",

            "confirmation": None,

            },
        },



    "login": {
        "as":      {
            "access":   {
                "teacher":  True,
                "ta":       True,
                "student":  True,
                },

            "required": ['name', 'password'],

            "required2": [],

            "optional": [],

            "help":     "Login as selected user.",

            },

        "new":     {
            "access":   {
                "teacher":  True,
                "ta":       True,
                "student":  True,
                },

            "required": ['name', 'password'],

            "required2": [],

            "optional": [],

            "help":     "Create new user with given password. New users have basic student access.",

            },

        "update":   {
            "access":   {
                "teacher":  True,
                "ta":       True,
                "student":  True,
                },

            "required": ['password', 'new-password'],

            "required2": [],

            "optional": [],

            "help":     "Update password.",

            },
        },




    "student": {
        "add":      {
            "access":   {
                "teacher":  True,
                "ta":       False,
                "student":  False,
                },

            "required": ['course-id', 'student'],

            "required2": [],

            "optional": [],

            "help":     "Adds student(s) to the selected course.",

            },

        "view":     {
            "access":   {
                "teacher":  True,
                "ta":       True,
                "student":  True,
                },

            "required": [],

            "required2": [],

            "optional": ['course-id', 'first', 'last', 'student'],

            "help":     "View all students, optionally filtered by selected values.",

            },

        "update":   {
            "access":   {
                "teacher":  False,
                "ta":       False,
                "student":  False,
                },

            "required": [],

            "required2": [],

            "optional": [],

            "help":     "",

            },

        "delete":   {
            "access":   {
                "teacher":  True,
                "ta":       False,
                "student":  False,
                },

            "required": ['course-id', 'student'],

            "required2": [],

            "optional": [],

            "help":     "Removes student(s) from the selected course.",

            "confirmation": None,

            },
        },

    "submission": {
        "add":      {
            "access":   {
                "teacher":  False,
                "ta":       False,
                "student":  True,
                },

            "required": ['assignment-id', 'filepath',],

            "required2": [],

            "optional": [],

            "help":     "Upload selected file(s) as submission to the selected assignment.",

            },

        "view":     {
            "access":   {
                "teacher":  True,
                "ta":       True,
                "student":  True,
                },

            "required": [],

            "required2": [],

            "optional": ['assignment-id', 'student', 'submission'],

            "help":     "View selected assignment submission, all submissions for a selected assignment, or all submissions for a selected assignment and student. Students can only select/view their own submissions. Shows any available feedback, including grades.",

            },

        "update":   {
            "access":   {
                "teacher":  True,
                "ta":       True,
                "student":  False,
                },

            "required": ['submission', 'grade'],

            "required2": ['assignment-id', 'student', 'grade'],

            "optional": [],

            "help":     "Updates grade of submission. A specific submission can be selected with the submission key, or by using assignment-id and student keys to select a student's most recent submission for the assignment.",

            },

        "delete":   {
            "access":   {
                "teacher":  False,
                "ta":       False,
                "student":  False,
                },

            "required": [],

            "required2": [],

            "optional": [],

            "help":     "",

            "confirmation": None,

            },
        },

    "ta": {
        "add":      {
            "access":   {
                "teacher":  True,
                "ta":       False,
                "student":  False,
                },

            "required": ['ta'],

            "required2": [],

            "optional": ['course-id'],

            "help":     "Adds given ONID(s) as TAs, or if course-id is also given, adds the selected TA(s) to that course.",

            },

        "view":     {
            "access":   {
                "teacher":  True,
                "ta":       True,
                "student":  True,
                },

            "required": [],

            "required2": [],

            "optional": ['course-id', 'ta'],

            "help":     "List all TAs, optionally filtered by course-id or by TA ONID.",

            },

        "update":   {
            "access":   {
                "teacher":  False,
                "ta":       False,
                "student":  False,
                },

            "required": [],

            "required2": [],

            "optional": [],

            "help":     "",

            },

        "delete":   {
            "access":   {
                "teacher":  True,
                "ta":       False,
                "student":  False,
                },

            "required": ['ta'],

            "required2": [],

            "optional": ['course-id'],

            "help":     "Removes TA(s) from list of TAs. If a course-id is given, removes the selected TA(s) from that course",

            "confirmation": None,

            },
        },

    "tag": {
        "add":      {
            "access":   {
                "teacher":  True,
                "ta":       False,
                "student":  False,
                },

            "required": ['assignment-id', 'tags'],

            "required2": [],

            "optional": [],

            "help":     "Add tag(s) to selected assignment.",

            },

        "view":     {
            "access":   {
                "teacher":  True,
                "ta":       False,
                "student":  False,
                },

            "required": [],

            "required2": [],

            "optional": ['assignment-id', 'tags'],

            "help":     "Shows all tags for all assignments, all tags for a selected assignment, or all assignments with selected tags.",

            },

        "update":   {
            "access":   {
                "teacher":  False,
                "ta":       False,
                "student":  False,
                },

            "required": [],

            "required2": [],

            "optional": [],

            "help":     "",

            },

        "delete":   {
            "access":   {
                "teacher":  True,
                "ta":       False,
                "student":  False,
                },

            "required": ['assignment-id'],

            "required2": [],

            "optional": ['tags'],

            "help":     "Deletes all tags from an assignment, or if specific tags are selected, deletes just those tags. No confirmation.",

            "confirmation": None,

            },
        },

    "test": {
        "add":      {
            "access":   {
                "teacher":  True,
                "ta":       False,
                "student":  False,
                },

            "required": ['filepath', 'name'],

            "required2": [],

            "optional": ['assignment-id', 'points', 'time'],

            "help":     "Add test. If no assignment is selected, the test will be inactive until an assignment is selected using test update.",

            },

        "view":     {
            "access":   {
                "teacher":  True,
                "ta":       False,
                "student":  False,
                },

            "required": [],

            "required2": [],

            "optional": ['assignment-id', 'version', 'test-id'],

            "help":     "View all tests [for selected assignment-id [and version number, defaults to highest if not given]]",

            },

        "update":   {
            "access":   {
                "teacher":  True,
                "ta":       False,
                "student":  False,
                },

            "required": ['test-id'],

            "required2": [],

            "optional": ['filepath', 'name', 'points', 'time'],

            "help":     "Attempts to update selected test, adds update as new test if the test cannot be updated (tests can't be changed if any student submissions reference those tests).",

            },

        "delete":   {
            "access":   {
                "teacher":  True,
                "ta":       False,
                "student":  False,
                },

            "required": ['test-id'],

            "required2": [],

            "optional": [],

            "help":     "Attempts to delete selected tests. Tests can't be deleted if any student submissions reference those tests.",

            "confirmation": "Deleting this test will permanenty remove the test and associated file from the database.",

            },

        "link":   {
            "access":   {
                "teacher":  True,
                "ta":       False,
                "student":  False,
                },

            "required": ['test-id', 'assignment-id'],

            "required2": [],

            "optional": [],

            "help":     "Link test to assignment. If the assignment already has submissions, a new version with the test will be created, otherwise the test will be linked to the most recent version.",

            },

        "unlink":   {
            "access":   {
                "teacher":  True,
                "ta":       False,
                "student":  False,
                },

            "required": ['test-id', 'assignment-id'],

            "required2": [],

            "optional": [],

            "help":     "Attempts to unlink test from assignment. If the assignment already has submissions, a new version with the test removed will be created, otherwise the test will be unlinked from the most recent version.",

            },
        },

    # "command": {
        # "add":      {
            # "access":   {
                # "teacher":  False,
                # "ta":       False,
                # "student":  False,
                # },

            # "required": ['assignment-id', 'begin', 'ce-id', 'course-id', 'dept', 'end', 'filepath', 'first', 'grade', 'last', 'late', 'level', 'limit', 'name', 'num', 'points', 'student', 'submission', 'ta', 'tags', 'teacher', 'term', 'test-id', 'text', 'time', 'version', 'year'],

            # "required2": [],

            # "optional": ['assignment-id', 'begin', 'ce-id', 'course-id', 'dept', 'end', 'filepath', 'first', 'grade', 'last', 'late', 'level', 'limit', 'name', 'num', 'points', 'student', 'submission', 'ta', 'tags', 'teacher', 'term', 'test-id', 'text', 'time', 'version', 'year'],

            # "help":     "",

            # },

        # "view":     {
            # "access":   {
                # "teacher":  False,
                # "ta":       False,
                # "student":  False,
                # },

            # "required": ['assignment-id', 'begin', 'ce-id', 'course-id', 'dept', 'end', 'filepath', 'first', 'grade', 'last', 'late', 'level', 'limit', 'name', 'num', 'points', 'student', 'submission', 'ta', 'tags', 'teacher', 'term', 'test-id', 'text', 'time', 'version', 'year'],

            # "required2": [],

            # "optional": ['assignment-id', 'begin', 'ce-id', 'course-id', 'dept', 'end', 'filepath', 'first', 'grade', 'last', 'late', 'level', 'limit', 'name', 'num', 'points', 'student', 'submission', 'ta', 'tags', 'teacher', 'term', 'test-id', 'text', 'time', 'version', 'year'],

            # "help":     "",

            # },

        # "update":   {
            # "access":   {
                # "teacher":  False,
                # "ta":       False,
                # "student":  False,
                # },

            # "required": ['assignment-id', 'begin', 'ce-id', 'course-id', 'dept', 'end', 'filepath', 'first', 'grade', 'last', 'late', 'level', 'limit', 'name', 'num', 'points', 'student', 'submission', 'ta', 'tags', 'teacher', 'term', 'test-id', 'text', 'time', 'version', 'year'],

            # "required2": [],

            # "optional": ['assignment-id', 'begin', 'ce-id', 'course-id', 'dept', 'end', 'filepath', 'first', 'grade', 'last', 'late', 'level', 'limit', 'name', 'num', 'points', 'student', 'submission', 'ta', 'tags', 'teacher', 'term', 'test-id', 'text', 'time', 'version', 'year'],

            # "help":     "",

            # },

        # "delete":   {
            # "access":   {
                # "teacher":  False,
                # "ta":       False,
                # "student":  False,
                # },

            # "required": ['assignment-id', 'begin', 'ce-id', 'course-id', 'dept', 'end', 'filepath', 'first', 'grade', 'last', 'late', 'level', 'limit', 'name', 'num', 'points', 'student', 'submission', 'ta', 'tags', 'teacher', 'term', 'test-id', 'text', 'time', 'version', 'year'],

            # "required2": [],

            # "optional": ['assignment-id', 'begin', 'ce-id', 'course-id', 'dept', 'end', 'filepath', 'first', 'grade', 'last', 'late', 'level', 'limit', 'name', 'num', 'points', 'student', 'submission', 'ta', 'tags', 'teacher', 'term', 'test-id', 'text', 'time', 'version', 'year'],

            # "help":     "",

            # "confirmation": "Deleting this  will permanenty remove ",

            # },
        # },
    }


options = {
    "assignment-id":     {
            "type":     "int",
            "help":     "Number that identifies a particular assignment. Displayed using assignment view.",
            "table":    "assignments",
            "key":      "assignment_id",
            "grade":    ["versions", "version_id", "assignments", "assignment_id"],
            "submission":    ["versions", "version_id", "assignments", "assignment_id"],
            },
    "begin":     {
            "type":     "timestamp",
            "help":     "Date assignment opens. Defaults to current date at 23:59 PM.",
            "example":  "Format is mm/dd/yyyy hh:mm:ss. I.e. begin=\"9/3/10 5:03:00\".",
            "table":    "assignments",
            "key":      "begin_date",
            },
    "ce-id":     {
            "type":     "int",
            "help":     "Integer number that identifies a common error. Displayed using ce view.",
            "table":    "common_errors",
            "key":      "ce_id",
            },
    "course-id":     {
            "type":     "int",
            "help":     "Integer number that identifies a course. Displayed using course view.",
            "table":    "courses",
            "key":      "course_id",
            },
    "dept":     {
            "type":     "str",
            "help":     "Abbreviation for department (i.e. CS or ECE).",
            "table":    "depts",
            "key":      "dept_id",
            "course":   ["depts", "dept_id"],
            },
    "end":     {
            "type":     "timestamp",
            "help":     "Date assignment closes. Defaults to two weeks from current date at 11:59 PM.",
            "example":  "Format is mm/dd/yyyy hh:mm:ss. I.e. end=\"9/3/10 5:03:00\".",
            "table":    "assignments",
            "key":      "end_date",
            },
    "filepath":     {
            "type":     "file",
            "help":     "Filepath of file to be used.",
            },
    "first":     {
            "type":     "str",
            "help":     "First name.",
            "table":    "users",
            "key":      "firstname",
            },
    "grade":     {
            "type":     "int",
            "help":     "Grade as a simple point value",
            "table":    "submissions",
            "key":      "grade",
            },
    "last":     {
            "type":     "str",
            "help":     "Last name.",
            "table":    "users",
            "key":      "lastname",
            },
    "late":     {
            "type":     "int",
            "help":     "Number of days late an assignment can be turned in. Defaults to 0.",
            "table":    "assignments",
            "key":      "late_submission",
            },
    "level":     {
            "type":     "int",
            "help":     "Determines the amount of feedback assignment gives. Defaults to 1.",
            0:          "Reports if submission succedeed or failed.",
            1:          "Above levels plus grade.",
            2:          "Above levels plus lists of tests passed or failed, with error messages.",
            3:          "Above levels plus identifying information for tests.",
            "table":    "assignments",
            "key":      "feedback_level",
            },
    "limit":     {
            "type":     "int",
            "help":     "Number of submissions allowed. 0 or below allows infinite submissions. Defaults to 1.",
            "table":    "assignments",
            "key":      "submission_limit",
            },
    "name":     {
            "type":     "str",
            "help":     "Can be any quoted string",
            "key":      "name"
            },
    "num":     {
            "type":     "int",
            "help":     "Course number. For example, the num for 'CS 444' is '444'.",
            "table":    "courses",
            "key":      "course_num",
            },
    "password":     {
            "type":     "str",
            "help":     "User password. Can be of any length and include any characters except quotes and whitespace.",
            "table":    "users",
            "key":      "password",
            },
    "new-password":     {
            "type":     "str",
            "help":     "New user password. Can be of any length and include any characters except quotes and whitespace.",
            "table":    "users",
            "key":      "new_password",
            },
    "points":     {
            "type":     "int",
            "help":     "Amount of points a given item is worth.",
            "key":      "points"
            },
    "student":     {
            "type":     "str",
            "help":     "Oregon State Netword ID for student(s).",
            "example":  "Accepts single ONID, i.e. student=hennign, or multiple onids concatenated with ',', i.e. student=hennign,wymanl,gassa).",
            "table":    "users",
            "join":     ["users.user_id", "students.student_id"],
            "key":      "student_id",
            },
    "submission":     {
            "type":     "int",
            "help":     "Number that identifies a given assignment submission. Displayed using submission view.",
            "table":    "submissions",
            "key":      "submission_id",
            },
    "ta":     {
            "type":     "str",
            "help":     "Oregon State Netword ID for teacher assitant(s).",
            "example":  "Accepts single ONID, i.e. ta=hennign, or multiple onids concatenated with ',', i.e. ta=hennign,wymanl,gassa).",
            "table":    "users",
            "join":     ["users.user_id", "tas.ta_id"],
            "key":      "ta_id",
            },
    "tags":     {
            "type":     "str",
            "help":     "Keywords for assignment.",
            "example":   "For example, an assignment using Python for loops might have tags=python,\'control loops\'.",
            "table":    "tags",
            "key":      "tag_id",
            },
    "teacher":     {
            "type":     "str",
            "help":     "Oregon State Netword ID for teacher(s).",
            "example":  "Accepts single ONID, i.e. teacher=hennign, or multiple onids concatenated with ',', i.e. teacher=hennign,wymanl,gassa).",
            "table":    "users",
            "key":      "teacher_id",
            "course":   ["teachers_teach_courses", "course_id", "users", "user_id"],
            "assignment": ["users", "user_id"],
            },
    "term":     {
            "type":     "str",
            "help":     "Can be fall, winter, spring, or summer.",
            "table":    "courses",
            "key":      "term",
            },
    "test-id":     {
            "type":     "int",
            "help":     "Number that identifies a particular test. Displayed using test view.",
            "table":    "tests",
            "key":      "test_id",
            },
    "text":     {
            "type":     "str",
            "help":     "Filepath to file, or a string of text, explaining the error.",
            "table":    "tests",
            "key":      "text",
            },
    "time":     {
            "type":     "int",
            "help":     "Number of minutes a test is allowed to run before being aborted. Defaults to 1.",
            "table":    "tests",
            "key":      "time_limit",
            },
    "year":     {
            "type":     "int",
            "help":     "Year the course takes place in.",
            "table":    "courses",
            "key":      "year",
            },
    "version":     {
            "type":     "int",
            "help":     "Version number for assignment. Defaults to highest (most recent) available.",
            "table":    "versions",
            "key":      "version_id",
            },
    }
