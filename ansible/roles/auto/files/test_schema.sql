DROP SCHEMA public CASCADE;
CREATE SCHEMA public;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO public;
COMMENT ON SCHEMA public IS 'standard public schema';

CREATE TABLE users (
    user_id		serial PRIMARY KEY,
	username	varchar(30) UNIQUE,
	firstname	varchar(50),
	lastname	varchar(70),
    auth        varchar(150)
);
INSERT INTO users (username, auth)
VALUES
    ('teststudent', '$pbkdf2-sha512$25000$vfdeay3lvLe2VirlfK/1Pg$X8Kyw9u2UHkg3R0YC5vzfM1ETAE5bak73Q8E8aswNBqYoj7IavK9pDgCT0.eVmk54oR5kBJqnCRt9PMbgrA06Q'),
    ('testta', '$pbkdf2-sha512$25000$vfdeay3lvLe2VirlfK/1Pg$X8Kyw9u2UHkg3R0YC5vzfM1ETAE5bak73Q8E8aswNBqYoj7IavK9pDgCT0.eVmk54oR5kBJqnCRt9PMbgrA06Q'),
    ('testteacher', '$pbkdf2-sha512$25000$vfdeay3lvLe2VirlfK/1Pg$X8Kyw9u2UHkg3R0YC5vzfM1ETAE5bak73Q8E8aswNBqYoj7IavK9pDgCT0.eVmk54oR5kBJqnCRt9PMbgrA06Q'),
    ('hennign', '$pbkdf2-sha512$25000$vfdeay3lvLe2VirlfK/1Pg$X8Kyw9u2UHkg3R0YC5vzfM1ETAE5bak73Q8E8aswNBqYoj7IavK9pDgCT0.eVmk54oR5kBJqnCRt9PMbgrA06Q'),
    ('gassa', '$pbkdf2-sha512$25000$vfdeay3lvLe2VirlfK/1Pg$X8Kyw9u2UHkg3R0YC5vzfM1ETAE5bak73Q8E8aswNBqYoj7IavK9pDgCT0.eVmk54oR5kBJqnCRt9PMbgrA06Q'),
    ('wymanl', '$pbkdf2-sha512$25000$vfdeay3lvLe2VirlfK/1Pg$X8Kyw9u2UHkg3R0YC5vzfM1ETAE5bak73Q8E8aswNBqYoj7IavK9pDgCT0.eVmk54oR5kBJqnCRt9PMbgrA06Q');

CREATE TABLE students (
	student_id		integer PRIMARY KEY,
	FOREIGN KEY (student_id) REFERENCES users (user_id) ON DELETE CASCADE
);
INSERT INTO students (student_id)
SELECT user_id from users
WHERE username='teststudent'
    OR username='hennign';

CREATE TABLE tas (
	ta_id		integer PRIMARY KEY,
	FOREIGN KEY (ta_id) REFERENCES users (user_id) ON DELETE CASCADE
);
INSERT INTO tas (ta_id)
SELECT user_id from users
WHERE username='testta'
    OR username='gassa';

CREATE TABLE teachers (
	teacher_id		integer PRIMARY KEY,
	FOREIGN KEY (teacher_id) REFERENCES users (user_id) ON DELETE CASCADE
);
INSERT INTO teachers (teacher_id)
SELECT user_id from users
WHERE username='testteacher'
    OR username='wymanl';

CREATE TABLE depts (
	dept_id		smallserial PRIMARY KEY,
	dept_name		varchar(10)
);
INSERT INTO depts (dept_name)
VALUES ('cs'), ('ece');

CREATE TABLE courses (
	course_id	serial PRIMARY KEY,
	dept_id		smallint REFERENCES depts (dept_id) ON DELETE CASCADE,
	course_num	smallint,
	name		varchar(100) not null,
	term		varchar(6),
	year		smallint
);
INSERT INTO courses (dept_id, course_num, name, term, year)
VALUES
    (1,  161, 'Introduction to Computer Science I',  'winter', 2016),
    (2, 271, 'Digital Logic Design',                'spring', 2016),
    (1,  480, 'Translators',                         'winter', 2016);

CREATE TABLE students_take_courses (
	student_id	integer REFERENCES students (student_id) ON DELETE CASCADE,
	course_id	integer REFERENCES courses (course_id) ON DELETE CASCADE,
	PRIMARY KEY (student_id, course_id)
);
INSERT INTO students_take_courses (student_id, course_id)
SELECT S.student_id, C.course_id
FROM students AS S, courses AS C
LIMIT 2;

CREATE TABLE tas_assist_in_courses (
	ta_id		integer REFERENCES tas (ta_id) ON DELETE CASCADE,
	course_id	integer REFERENCES courses (course_id) ON DELETE CASCADE,
	PRIMARY KEY (ta_id, course_id)
);
INSERT INTO tas_assist_in_courses (ta_id, course_id)
SELECT T.ta_id, C.course_id
FROM courses AS C, tas AS T
LIMIT 2;

CREATE TABLE tas_assigned_students (
	ta_id		integer REFERENCES tas (ta_id) ON DELETE CASCADE,
	student_id	integer REFERENCES students (student_id) ON DELETE CASCADE,
	course_id	integer REFERENCES courses (course_id) ON DELETE CASCADE,
	PRIMARY KEY (ta_id, student_id, course_id)
);
INSERT INTO tas_assigned_students (ta_id, student_id, course_id)
SELECT T.ta_id, S.student_id, S.course_id
FROM students_take_courses AS S, tas AS T
LIMIT 2;

CREATE TABLE teachers_teach_courses (
	teacher_id	integer	REFERENCES teachers (teacher_id) ON DELETE CASCADE,
	course_id	integer REFERENCES courses (course_id) ON DELETE CASCADE,
	PRIMARY KEY (teacher_id, course_id)
);
INSERT INTO teachers_teach_courses (teacher_id, course_id)
SELECT T.teacher_id, C.course_id
FROM courses AS C, teachers AS T;

CREATE TABLE assignments (
	assignment_id		serial PRIMARY KEY,
	course_id			integer REFERENCES courses (course_id) ON DELETE CASCADE,
    teacher_id          integer REFERENCES teachers (teacher_id) ON DELETE CASCADE,
	name				varchar(100) NOT NULL,
	begin_date			timestamp,
	end_date			timestamp,
	submission_limit	smallint,
	feedback_level		smallint,
	late_submission		smallint
);
INSERT INTO assignments (course_id, teacher_id, name, begin_date, end_date, submission_limit, feedback_level, late_submission)
VALUES ( 1, (
    SELECT T.teacher_id
    FROM teachers_teach_courses AS T
    WHERE T.course_id=1
    LIMIT 1
    ), 'Intro to Loops', TIMESTAMP '2016-02-16 12:00:00', TIMESTAMP '2016-02-24 23:59:00', 0, 3, 7);

CREATE TABLE tags (
	tag_id		serial PRIMARY KEY,
	text		varchar(50) UNIQUE
);
INSERT INTO tags (text)
VALUES ('python'), ('loopcontrol'), ('forloop'), ('whileloop'), ('dowhileloop');

CREATE TABLE assignments_have_tags (
	assignment_id	integer REFERENCES assignments (assignment_id) ON DELETE CASCADE,
	tag_id			integer REFERENCES tags (tag_id) ON DELETE CASCADE,
	PRIMARY KEY (assignment_id, tag_id)
);
INSERT INTO assignments_have_tags (assignment_id, tag_id)
SELECT A.assignment_id, T.tag_id
FROM assignments as A, tags as T
LIMIT 2;

CREATE TABLE tests (
	test_id			serial PRIMARY KEY,
    teacher_id      integer REFERENCES teachers (teacher_id) ON DELETE CASCADE,
	name		    varchar(50),
	points			smallint,
	time_limit		smallint
);

CREATE TABLE versions (
	version_id		serial PRIMARY KEY,
	assignment_id	integer REFERENCES assignments (assignment_id) ON DELETE CASCADE
);
INSERT INTO versions (assignment_id)
SELECT A.assignment_id
FROM assignments as A;

CREATE TABLE submissions (
	submission_id		serial PRIMARY KEY,
	version_id			integer REFERENCES versions (version_id) ON DELETE CASCADE,
	submission_date		timestamp DEFAULT now(),
	grade				real
);
INSERT INTO submissions (version_id)
SELECT V.version_id
FROM versions AS V;

CREATE TABLE submissions_have_results (
	submission_id		integer REFERENCES submissions (submission_id) ON DELETE CASCADE,
	test_id			    integer REFERENCES tests (test_id) ON DELETE CASCADE,
	results             text  ,
    PRIMARY KEY (submission_id, test_id)
);

CREATE TABLE students_create_submissions (
	student_id			integer REFERENCES students (student_id) ON DELETE CASCADE,
	submission_id		integer REFERENCES submissions (submission_id) ON DELETE CASCADE,
	PRIMARY KEY (student_id, submission_id)
);
INSERT INTO students_create_submissions (student_id, submission_id)
SELECT S.student_id, U.submission_id
FROM students as S, submissions as U;

CREATE TABLE versions_have_tests (
	version_id		integer REFERENCES versions (version_id) ON DELETE CASCADE,
	test_id			integer REFERENCES tests (test_id) ON DELETE CASCADE,
	PRIMARY KEY	(version_id, test_id)
);


CREATE TABLE submissions_have_tests (
	submission_id	integer REFERENCES submissions (submission_id) ON DELETE CASCADE,
	test_id			integer REFERENCES tests (test_id) ON DELETE CASCADE,
	result			bool,
	PRIMARY KEY (submission_id, test_id)
);


CREATE TABLE common_errors (
	ce_id		serial PRIMARY KEY,
	teacher_id	integer REFERENCES teachers (teacher_id) ON DELETE CASCADE,
	name		varchar(50),
	text		varchar(150)
);

CREATE TABLE tests_have_common_errors (
	test_id			integer REFERENCES tests (test_id) ON DELETE CASCADE,
	ce_id			integer REFERENCES common_errors (ce_id) ON DELETE CASCADE,
	PRIMARY KEY (test_id, ce_id)
);
INSERT INTO tests_have_common_errors (test_id, ce_id)
SELECT T.test_id, C.ce_id
FROM tests as T, common_errors as C;