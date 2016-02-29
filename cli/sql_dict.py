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
                ['users', 'username', 'teacher_id', 'teachers'],
            ],
                
            "optional": {},
            
            "allowed": [
                ['users', 'teachers', 'tchu'],
            ],
            
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
                ['users', 'username', 'teacher_id', 'teachers'],
            ],
                
            "optional": {},
            
            "allowed": [
                ['users', 'teachers', 'tchu'],
            ],
            
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
            
        },
    },
    
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
                ['users', 'username', 'teacher'],
            ],
                
            "optional": {},
            
            "allowed": [
                ['users', 'teachers', 'tu'],
            ],
            
        },
    },
    
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
                ['users', 'username', 'teacher'],
            ],
                
            "optional": {},
            
            "allowed": [
                ['users', 'teachers', 'tu'],
            ],
            
        },
    },
    
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
                ['users', 'username', 'teacher'],
            ],
                
            "optional": {},
            
            "allowed": [
                ['users', 'teachers', 'tu'],
            ],
            
        },
    },
    
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
                ['users', 'username', 'teacher'],
            ],
                
            "optional": {},
            
            "allowed": [
                ['users', 'teachers', 'tu'],
            ],
            
        },
    },
    
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
                ['users', 'username', 'teacher'],
            ],
                
            "optional": {},
            
            "allowed": [
                ['users', 'teachers', 'tu'],
            ],
            
        },
    },
    
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
                ['users', 'username', 'teacher'],
            ],
                
            "optional": {},
            
            "allowed": [
                ['users', 'teachers', 'tu'],
            ],
            
        },
    },
    
    
    
    

}