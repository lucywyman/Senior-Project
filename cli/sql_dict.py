sql = {
    "assignment": {
        "view": {

            "table":    'assignments',

            "required": [
                ['assignments', 'assignment_id', 'assignment_id'],
                ['assignments', 'course_id', 'course_id'],
                ['assignments', 'begin_date', 'begin_date'],
                ['assignments', 'end_date', 'end_date'],
                ['assignments', 'submission_limit', 'submission_limit'],
                ['assignments', 'feedback_level', 'feedback_level'],
                ['assignments', 'late_submission', 'late_submission'],
                ['assignments', 'name', 'name'],
                ['depts', 'dept_name', 'dept_name'],
                ['courses', 'course_num', 'course_num'],
                ['courses', 'name', 'course_name'],
                # fourth entry specifies witch table to join with
                ['users', 'user_id', 'teacher_id', 'teachers'],
                ['users', 'username', 'teacher', 'teachers'],
            ],

            "optional": {},

            "allowed": [
                ['users', 'teachers', 'tchu'],
            ],

            "view_order": ['dept_name', 'course_num', 'assignment_id', 'name', 'end_date','late_submission', 'submission_limit', 'feedback_level', 'course_id'],

            "sort_order": ['course_id', 'assignment_id'],

        },
    },

    "ce": {
        "view": {

            "table":    'common_errors',

            "required": [
                ['common_errors', 'ce_id', 'ce_id'],
                ['common_errors', 'name', 'name'],
                ['common_errors', 'text', 'text'],
            ],

            "optional": {

                ('assignment_id','course_id','version_id'): [
                    ['assignments', 'assignment_id', 'assignment_id'],
                    ['assignments', 'name', 'assignment_name'],
                    ['courses', 'course_id', 'course_id'],
                    ['courses', 'name', 'course_name'],
                    ['versions', 'version_id', 'version_id'],
                    ['tests', 'test_id', 'test_id'],
                    ['tests', 'name', 'test_name'],
                ],

                ('test_id',): [
                    ['tests', 'test_id', 'test_id'],
                    ['tests', 'name', 'test_name'],
                ],
            },

            "allowed": [
            ],

            "view_order": ['ce_id', 'name', 'text', 'assignment_id', 'assignment_name', 'course_id', 'course_name', 'version_id', 'test_id', 'test_name'],

            "sort_order": ['test_id', 'course_id', 'assignment_id', 'ce_id'],

        },
    },

    "course": {
        "view": {

            "table":    'courses',

            "required": [
                ['courses', 'course_id', 'course_id'],
                ['courses', 'course_num', 'course_num'],
                ['courses', 'name', 'name'],
                ['courses', 'term', 'term'],
                ['courses', 'year', 'year'],
                ['depts', 'dept_name', 'dept_name'],
                ['users', 'user_id', 'teacher_id', 'teachers'],
                ['users', 'username', 'teacher', 'teachers'],
            ],

            "optional": {},

            "allowed": [
                ['users', 'teachers', 'tchu'],
            ],

            "view_order": ['course_id', 'dept_name', 'course_num', 'name', 'term', 'year', 'teacher' ],

            "sort_order": ['year', 'term', 'dept_name', 'course_num', 'course_id'],

        },
    },

    "group": {
        "view": {

            "table":    'tas_assigned_students',

            "required": [
                ['tas_assigned_students', 'ta_id', 'ta_id'],
                ['tas_assigned_students', 'student_id', 'student_id'],
                ['courses', 'course_id', 'course_id'],
                ['courses', 'course_num', 'course_num'],
                ['courses', 'name', 'course_name'],
                ['depts', 'dept_name', 'dept_name'],
                ['users', 'username', 'ta', 'tas'],
                ['users', 'username', 'student', 'students'],
            ],

            "optional": {},

            "allowed": [
                ['users', 'tas', 'tu'],
                ['users', 'students', 'su'],
            ],

            "view_order": ['course_id', 'dept_name', 'course_num', 'ta', 'student', 'course_name'],

            "sort_order": ['dept_name', 'course_num', 'course_id', 'ta', 'student'],

        },
    },

    "student": {
        "view": {

            "table":    'students_take_courses',

            "required": [
                ['courses', 'course_num', 'course_num'],
                ['courses', 'name', 'course_name'],
                ['depts', 'dept_name', 'dept_name'],
                ['students_take_courses', 'course_id', 'course_id'],
                ['students_take_courses', 'student_id', 'student_id'],
                ['users', 'firstname', 'first', 'students'],
                ['users', 'lastname', 'last', 'students'],
                ['users', 'username', 'student', 'students'],
            ],

            "optional": {},

            "allowed": [
                ['users', 'students', 'su'],
            ],

            "view_order": ['course_id', 'dept_name', 'course_num', 'course_name', 'student', 'last', 'first'],

            "sort_order": ['dept_name', 'course_num', 'course_id', 'student'],

        },
    },

    "submission": {
        "view": {

            "table":    'submissions_have_tests',

            "required": [
                ['submissions', 'submission_id', 'submission_id'],
                ['students_create_submissions', 'student_id', 'student_id'],
                ['tests', 'test_id', 'test_id'],
                ['tests', 'name', 'test_name'],
                ['versions', 'version_id', 'version_id'],
                ['assignments', 'assignment_id', 'assignment_id'],
                ['depts', 'dept_name', 'dept_name'],
                ['assignments', 'name', 'assignment_name'],
                ['submissions', 'grade', 'grade'],
                ['courses', 'name', 'course_name'],
                ['submissions', 'submission_date', 'submission_date'],
                ['submissions_have_tests', 'result', 'result'],
                ['users', 'username', 'student', 'students'],
                ['courses', 'course_num', 'course_num'],
            ],

            "optional": {},

            "allowed": [
                ['users', 'students', 'su'],
            ],

            "view_order": ['assignment_id', 'version_id', 'submission_id', 'submission_date', 'student', 'grade', 'assignment_name', 'dept_name', 'course_num'],

            "sort_order": ['assignment_id', 'version_id', 'submission_id'],

        },
    },

    "ta": {
        "view": {

            "table":    'tas_assist_in_courses',

            "required": [
                ['tas', 'ta_id', 'ta_id'],
                ['users', 'username', 'ta', 'tas'],
                ['courses', 'course_id', 'course_id'],
                ['courses', 'course_num', 'course_num'],
                ['courses', 'name', 'course_name'],
                ['depts', 'dept_name', 'dept_name'],
            ],

            "optional": {},

            "allowed": [
                ['users', 'tas', 'tau'],
            ],

            "view_order": ['course_id', 'dept_name', 'course_num', 'course_name', 'ta' ],

            "sort_order": ['course_id', 'ta'],

        },
    },

    "tag": {
        "view": {

            "table":    'assignments_have_tags',

            "required": [
                ['assignments', 'assignment_id', 'assignment_id'],
                ['assignments', 'name', 'assignment_name'],
                ['assignments', 'course_id', 'course_id'],
                ['depts', 'dept_name', 'dept_name'],
                ['courses', 'course_num', 'course_num'],
                ['courses', 'name', 'course_name'],
                ['tags', 'tag_id', 'tag_id'],
                ['tags', 'text', 'text'],

            ],

            "optional": {},

            "allowed": [
            ],

            "view_order": ['assignment_id', 'assignment_name', 'text', 'course_id', 'dept_name', 'course_num', 'course_name'],

            "sort_order": ['course_id', 'assignment_id', 'text'],

        },
    },

    "test": {
        "view": {

            "table":    'versions_have_tests',

            "required": [
                ['tests', 'test_id', 'test_id'],
                ['tests', 'name', 'test_name'],
                ['versions', 'version_id', 'version_id'],
                ['assignments', 'assignment_id', 'assignment_id'],
                ['assignments', 'course_id', 'course_id'],
                ['assignments', 'name', 'assignment_name'],
                ['depts', 'dept_name', 'dept_name'],
                ['courses', 'course_num', 'course_num'],
                ['courses', 'name', 'course_name'],
            ],

            "optional": {},

            "allowed": [
            ],

            "view_order": ['test_id', 'test_name', 'assignment_id', 'assignment_name', 'version_id', 'course_id', 'dept_name', 'course_num', 'course_name'],

            "sort_order": ['course_id', 'version_id', 'test_id'],

        },
    },

}