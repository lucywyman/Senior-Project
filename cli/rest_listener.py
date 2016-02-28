#!/usr/bin/python

import http.server
import socketserver
import argparse
import json
import psycopg2
import psycopg2.extras
import command_dict
from datetime import datetime
import db_graph

# Connect to an existing database
conn = psycopg2.connect("dbname=postgres user=postgres password=killerkat5", cursor_factory= psycopg2.extras.RealDictCursor)
conn.autocommit = True



PORT = 8000
SERVER = 'localhost'
class RESTfulHandler(http.server.BaseHTTPRequestHandler):

    def do_GET(self):
        """Serve a GET request."""
        
        # split path into components
        # path will always begin and end with '/', creating empty
        # entry at beginning and end of list, removed by path[1:-1] slice
        path = self.path.split('/')
        path = path[1:-1]
        
        # create cursor for querying db
        cur = conn.cursor()
        
        command = path[0]
        subcommand = path[1]
        
        data = self.rfile.read(int(self.headers['Content-Length'])).decode("UTF-8")
        data = json.loads(data)
        
        condition = None
        length = len(data)
        
        # # Replace version with actual version_id number
        # if 'version' in data and 'assignment-id' in data:
            # cur.execute("SELECT ROW_NUMBER() OVER (PARTITION BY assignment_id) AS c_no, version_id, assignment_id FROM versions WHERE c_no=%(version)s AND assignment_id=%(assignment-id)s", data)
            # result = cur.fetchone()
            # data['version'][0] = result['version_id']
            
        if 'begin' in data:
            data['begin'][0] = datetime.strptime(data['begin'][0], '%x %X')
        if 'end' in data:
            data['end'][0] = datetime.strptime(data['end'][0], '%x %X')
        
        if command == 'assignment':
        
            #check data to build where clause
            
            if length > 0:
                condition = "WHERE "
                for opt in data:
                    print(data)
                    print(opt)
                    condition += command_dict.options[opt]['key'] + "=%(" + opt + ")s"
                    length -= 1
                    if length > 0:
                        condition += " AND "
                        
            query = """
                SELECT assignments.assignment_id, assignments.course_id, assignments.name, begin_date, end_date, submission_limit, feedback_level, late_submission, dept_name, course_num, courses.name, username 
                FROM assignments
                INNER JOIN courses
                ON courses.course_id=assignments.course_id
                INNER JOIN depts
                ON depts.dept_id=courses.dept_id
                INNER JOIN teachers_teach_courses
                ON teachers_teach_courses.course_id=assignments.course_id
                INNER JOIN users
                ON users.user_id=teachers_teach_courses.teacher_id
                """
                
            if condition != None:
                query += condition
                
            # TODO - Quick workaround for data being in arrays
            # How to deal with when multiple values available?
            for k in data:
                data[k] = data[k][0]
                
            print(query)
            print(data)
            cur.execute(query, data)
            
        if command == 'ce':
        

            query = """
                SELECT DISTINCT common_errors.ce_id, """

            if ('assignment-id' in data) or ('course-id' in data) or ('version' in data):
                query += """assignments.assignment_id, assignments.name AS assignment_name, courses.course_id, courses.name AS course_name, versions.version_id, tests.test_id, tests.name AS test_name, """
            elif 'test-id' in data:
                query += """tests.test_id, tests.name AS test_name, """
                
            query += """common_errors.name, common_errors.text FROM common_errors"""
            
            joins = {
                "assignment-id": [
                    ['tests_have_common_errors', 'common_errors', 'ce_id'],
                    ['tests', 'tests_have_common_errors', 'test_id'],
                    ['versions_have_tests', 'tests', 'test_id'],
                    ['versions', 'versions_have_tests', 'version_id'],
                    ['assignments', 'versions', 'assignment_id'],
                    ['courses', 'assignments', 'course_id']
                    ],
                
                "course-id":    [
                    ['tests_have_common_errors', 'common_errors', 'ce_id'],
                    ['tests', 'tests_have_common_errors', 'test_id'],
                    ['versions_have_tests', 'tests', 'test_id'],
                    ['versions', 'versions_have_tests', 'version_id'],
                    ['assignments', 'versions', 'assignment_id'],
                    ['courses', 'assignments', 'course_id']
                    ],
                    
                'version':  [
                    ['tests_have_common_errors', 'common_errors', 'ce_id'],
                    ['tests', 'tests_have_common_errors', 'test_id'],
                    ['versions_have_tests', 'tests', 'test_id'],
                    ['versions', 'versions_have_tests', 'version_id'],
                    ['assignments', 'versions', 'assignment_id'],
                    ['courses', 'assignments', 'course_id']
                    ],
                
                'test-id': [
                    ['tests_have_common_errors', 'common_errors', 'ce_id'],
                    ['tests', 'tests_have_common_errors', 'test_id'],
                    ['versions_have_tests', 'tests', 'test_id'],
                    ],
                    
                }
                
            join_set = []
            for key in ['assignment-id', 'course-id', 'version', 'test-id']:
                if key in data:
                    join_set += joins[key]
                    print("Join set is:")
                    print(join_set)
            
            used_tables = ['common_errors']
            join_size_old = 0
            join_size_new = 1
            
            # This algorithm is designed to keep going over possible
            # joins until a pass is made where no joins are used.
            # This allows us to assume that list of joins is unordered
            # and as long as one new join is made each pass, that
            # opens the oppurtunity for new joins to be made in the
            # following pass
            while join_size_new != join_size_old:
                join_size_old = len(used_tables)
                for join in join_set:
                    print(join)
                    # we only want to do a join if one table is
                    # already used and one table isn't. If neither
                    # are used, we aren't joining to the query, which
                    # is an error. If both are used, they are already
                    # part of the query and cannot be added again
                    print("0:")
                    print(used_tables)
                    print(join[0] in used_tables)
                    print(join[1] in used_tables)
                    print((join[0] in used_tables) != (join[1] in used_tables))
                    if (join[0] in used_tables) != (join[1] in used_tables):
                        if join[0] in used_tables:
                            print(query)
                            query += " INNER JOIN " + join[1] + " ON " + join[0] + "." + join[2] + "=" + join[1] + "." + join[2] + " "
                            used_tables.append(join[1])
                        elif join[1] in used_tables:
                            print(query)
                            query += " INNER JOIN " + join[0] + " ON " + join[0] + "." + join[2] + "=" + join[1] + "." + join[2] + " "
                            used_tables.append(join[0])
                    print(query)
                    print("1:")
                    print(used_tables)
                join_size_new = len(used_tables)
                
                
            #check data to build where clause
            
            if length > 0:
                condition = " WHERE "
                for opt in data:
                    print(data)
                    print(opt)
                    if opt != 'name':
                        condition += command_dict.options[opt]['table'] + "." + command_dict.options[opt]['key'] + "=%(" + opt + ")s"
                    else:
                        condition += 'common_errors.' + command_dict.options[opt]['key'] + "=%(" + opt + ")s"
                    length -= 1
                    if length > 0:
                        condition += " AND "
            
            
                
            if condition != None:
                query += condition
            
            
                
            # TODO - Quick workaround for data being in arrays
            # How to deal with when multiple values available?
            for k in data:
                data[k] = data[k][0]
                
            print(query)
            print(data)
            cur.execute(query, data)
        
        
        if command == 'course':
        
            
            #check data to build where clause
            
            
            if length > 0:
                condition = "WHERE "
                for opt in data:
                    print(data)
                    print(opt)
                    condition += command_dict.options[opt]['key'] + "=%(" + opt + ")s"
                    length -= 1
                    if length > 0:
                        condition += " AND "
                        
            query = """
                SELECT courses.course_id, dept_name, course_num, courses.name, username, term, year
                FROM courses
                INNER JOIN depts
                ON depts.dept_id=courses.dept_id
                INNER JOIN teachers_teach_courses
                ON teachers_teach_courses.course_id=courses.course_id
                INNER JOIN users
                ON users.user_id=teachers_teach_courses.teacher_id
                """
                
            if condition != None:
                query += condition
                
            # TODO - Quick workaround for data being in arrays
            # How to deal with when multiple values available?
            for k in data:
                data[k] = data[k][0]
                
            print(query)
            print(data)
            cur.execute(query, data)
   
        # print(vars(self))
        # print(self.requestline)
        # print(self.headers)
        # response = self.rfile.read(int(self.headers['Content-Length'])).decode("UTF-8")
        # print(response)
        
        # data = json.loads(response)
        # print("Data is:")
        # print(data)
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        result = cur.fetchall()
        print(result)
        
        for entry in result:
            if 'begin_date' in entry:
                entry['begin_date'] = entry['begin_date'].strftime('%x %X')
            if 'end_date' in entry:
                entry['end_date'] = entry['end_date'].strftime('%x %X')
        
      
        print(json.dumps(result, indent=2))
        result = json.dumps(result)

        self.wfile.write(bytes(result, 'UTF-8'))
        
        
    def do_POST(self):
        """Serve a POST request"""
        
        # split path into components
        # path will always begin and end with '/', creating empty
        # entry at beginning and end of list, removed by path[1:-1] slice
        path = self.path.split('/')
        path = path[1:-1]
        
        # create cursor for querying db
        cur = conn.cursor()
        
        command = path[0]
        subcommand = path[1]
        
        data = self.rfile.read(int(self.headers['Content-Length'])).decode("UTF-8")
        data = json.loads(data)
        
        if subcommand == 'add':
            table = None
            
            if command == 'assignment':
                table = 'assignments'
                #TODO implement tags
                #TODO add teacher_id behind the scenes
                if 'begin' in data:
                    data['begin'][0] = datetime.strptime(data['begin'][0], '%x %X')
                if 'end' in data:
                    data['end'][0] = datetime.strptime(data['end'][0], '%x %X')                   
            elif command == 'ce':
                #TODO add teacher_id behind the scenes
                table = 'common_errors'
            elif command == 'course':
                table = 'courses'
                if 'dept' in data:
                    cur.execute("SELECT depts.dept_id FROM depts INNER JOIN courses ON courses.dept_id=depts.dept_id WHERE depts.dept_name=%s", (data['dept'][0],))
                    data['dept'][0] = cur.fetchone()['dept_id']
            elif command == 'group':
                table = 'tas_assigned_students'
                # convert onids to user_ids
                # TODO - This doesn't support multiples as it should
                cur.execute("SELECT users.user_id FROM users INNER JOIN students ON users.user_id=students.student_id WHERE users.username=%s", (data['student'][0],))
                data['student'][0] = cur.fetchone()['user_id']
                cur.execute("SELECT users.user_id FROM users INNER JOIN tas ON users.user_id=tas.ta_id WHERE users.username=%s", (data['ta'][0],))
                data['ta'][0] = cur.fetchone()['user_id']
            elif command == 'student':
                table = 'students_take_courses'
                # convert onids to user_ids
                # TODO - This doesn't support multiples as it should
                cur.execute("SELECT users.user_id FROM users INNER JOIN students ON users.user_id=students.student_id WHERE users.username=%s", (data['student'][0],))
                data['student'][0] = cur.fetchone()['user_id']
            elif command == 'submission':
                table = 'submissions'
                #TODO - How to deal with file?
            elif command == 'ta':
                if 'course-id' in data:
                    table = 'tas_assist_in_courses'
                else:
                    table = 'tas'
                cur.execute("SELECT users.user_id FROM users WHERE users.username=%s", (data['ta'][0],))
                data['ta'][0] = cur.fetchone()['user_id']
            elif command == 'tag':
                table = 'assignments_have_tags'
                # TODO - insert ignore tags before getting tag_id (make sure they exist) (this may require delete then insert for postgre?)
                cur.execute("SELECT tags.tag_id FROM tags WHERE tags.text=%s", (data['tags'][0],))
                # TODO - only want to show teacher's own assignments
                # join to assignments to teachers and filter by name
                data['tags'][0] = cur.fetchone()['tag_id']
            elif command == 'test':
                table = 'tests'
                # TODO - how to deal with file?
                # Use cgi
                 
            length = len(data)
            keys = data.keys()
            
            query = "INSERT INTO " + table + " ("
            for opt in keys:
                query += command_dict.options[opt]['key']
                length -= 1
                if length > 0:
                    query += ", "
            query += ") VALUES ("
            
            length = len(data)
            for opt in keys:
                query += "%(" + opt + ")s"
                length -= 1
                if length > 0:
                    query += ", "
            query += ")"
            
            # TODO - Quick workaround for data being in arrays
            # How to deal with when multiple values available?
            for k in data:
                data[k] = data[k][0]
                
            print(query)
            print(data)
            cur.execute(query, data)
        
        idkey = None
        if subcommand == 'update':
            if command == 'assignment':
                idkey = 'assignment-id'
                table = 'assignments'
                #TODO implement tags
                #TODO add teacher_id behind the scenes
                if 'begin' in data:
                    data['begin'][0] = datetime.strptime(data['begin'][0], '%x %X')
                if 'end' in data:
                    data['end'][0] = datetime.strptime(data['end'][0], '%x %X')                   
            elif command == 'ce':
                idkey = 'ce-id'
                table = 'common_errors'
            elif command == 'course':
                idkey = 'course-id'
                table = 'courses'
                if 'dept' in data:
                    cur.execute("SELECT depts.dept_id FROM depts INNER JOIN courses ON courses.dept_id=depts.dept_id WHERE depts.dept_name=%s", (data['dept'][0],))
                    data['dept'][0] = cur.fetchone()['dept_id']
            elif command == 'grade' or command == 'submission':
                #TODO - how is this affected by edge case where multiple students create one submission? Also students submission add needs to support students keyword
                idkey = 'submission'
                if 'assignment-id' in data:
                    # get student id from onid
                    cur.execute("SELECT users.user_id FROM users INNER JOIN students ON users.user_id=students.student_id WHERE users.username=%s", (data['student'][0],))
                    data['student'][0] = cur.fetchone()['user_id']
                    # use assignment-id and student-id to select correct submission-id
                    
                    
                    cur.execute(""" SELECT MAX(S.submission_id)
                        FROM submissions AS S
                        INNER JOIN students_create_submissions AS C
                        ON S.submission_id=C.submission_id
                        INNER JOIN versions AS V
                        ON S.version_id=V.version_id
                        WHERE 
                            V.assignment_id=%s
                            AND C.student_id=%s """, (data['assignment-id'][0], data['student'][0],))
                    data['submission'] = []
                    data['submission'].append(cur.fetchone()['max'])
                    # remove unused keys
                    data.pop('assignment-id')
                    data.pop('student')
                table = 'submissions'
            elif command == 'test':
                idkey = 'test-id'
                table = 'tests'
                
            # -1 is because an update command must include an idkey
            length = len(data) - 1
            keys = data.keys()
            
            query = "UPDATE " + table + " SET "
            for opt in keys:
                if opt != idkey:
                    query += command_dict.options[opt]['key'] + "=%(" + opt + ")s"
                    length -= 1
                    if length > 0:
                        query += ", "
            query += " WHERE " + command_dict.options[idkey]['key'] + "=%(" + idkey + ")s"
            
            
            
            # TODO - Quick workaround for data being in arrays
            # How to deal with when multiple values available?
            for k in data:
                data[k] = data[k][0]
                
            print(query)
            print(data)
            cur.execute(query, data)
            
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        # TODO - Add better confirmation message
        # result = cur.fetchall()
        # print(json.dumps(result, indent=2))
        # result = json.dumps(result)

        # self.wfile.write(bytes(result, 'UTF-8'))
        
        
    def do_DELETE(self):
        """Serve a DELETE request"""
        
        # split path into components
        # path will always begin and end with '/', creating empty
        # entry at beginning and end of list, removed by path[1:-1] slice
        path = self.path.split('/')
        path = path[1:-1]
        
        # create cursor for querying db
        cur = conn.cursor()
        
        command = path[0]
        subcommand = path[1]
        
        data = self.rfile.read(int(self.headers['Content-Length'])).decode("UTF-8")
        data = json.loads(data)
        
        if subcommand == 'delete':
            table = None
            if command == 'assignment':
                table = 'assignments'                   
            elif command == 'ce':
                table = 'common_errors'
            elif command == 'course':
                table = 'courses'
            elif command == 'group':
                table = 'tas_assigned_students'
                # convert onids to user_ids
                # TODO - This doesn't support multiples as it should
                if 'student' in data:
                    cur.execute("SELECT users.user_id FROM users INNER JOIN students ON users.user_id=students.student_id WHERE users.username=%s", (data['student'][0],))
                    data['student'][0] = cur.fetchone()['user_id']
                cur.execute("SELECT users.user_id FROM users INNER JOIN tas ON users.user_id=tas.ta_id WHERE users.username=%s", (data['ta'][0],))
                data['ta'][0] = cur.fetchone()['user_id']
            elif command == 'student':
                table = 'students_take_courses'
                # convert onids to user_ids
                # TODO - This doesn't support multiples as it should
                cur.execute("SELECT users.user_id FROM users INNER JOIN students ON users.user_id=students.student_id WHERE users.username=%s", (data['student'][0],))
                data['student'][0] = cur.fetchone()['user_id']
            elif command == 'submission':
                table = 'submissions'
                #TODO - How to deal with file?
            elif command == 'ta':
                if 'course-id' in data:
                    table = 'tas_assist_in_courses'
                else:
                    table = 'tas'
                cur.execute("SELECT users.user_id FROM users WHERE users.username=%s", (data['ta'][0],))
                data['ta'][0] = cur.fetchone()['user_id']
            elif command == 'tag':
                table = 'assignments_have_tags'
                # TODO - insert ignore tags before getting tag_id (make sure they exist) (this may require delete then insert for postgre?)
                cur.execute("SELECT tags.tag_id FROM tags WHERE tags.text=%s", (data['tags'][0],))
                # TODO - only want to show teacher's own assignments
                # join to assignments to teachers and filter by name
                data['tags'][0] = cur.fetchone()['tag_id']
            elif command == 'test':
                table = 'tests'
                #TODO - File support
    
    
            # -1 is because an update command must include an idkey
            length = len(data)
            keys = data.keys()
            
            query = "DELETE FROM " + table + " WHERE "
            for opt in keys:
                query += command_dict.options[opt]['key'] + "=%(" + opt + ")s"
                length -= 1
                if length > 0:
                    query += " AND "

            
            
            
            # TODO - Quick workaround for data being in arrays
            # How to deal with when multiple values available?
            for k in data:
                data[k] = data[k][0]
                
            print(query)
            print(data)
            cur.execute(query, data)
            
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
    def send_head(self):
        """Common code for GET and HEAD commands.

        This sends the response code and MIME headers.

        Return value is either a file object (which has to be copied
        to the outputfile by the caller unless the command was HEAD,
        and must be closed by the caller under all circumstances), or
        None, in which case the caller has nothing further to do.

        """
        path = self.translate_path(self.path)
        f = None
        if os.path.isdir(path):
            parts = urllib.parse.urlsplit(self.path)
            if not parts.path.endswith('/'):
                # redirect browser - doing basically what apache does
                self.send_response(HTTPStatus.MOVED_PERMANENTLY)
                new_parts = (parts[0], parts[1], parts[2] + '/',
                             parts[3], parts[4])
                new_url = urllib.parse.urlunsplit(new_parts)
                self.send_header("Location", new_url)
                self.end_headers()
                return None
            for index in "index.html", "index.htm":
                index = os.path.join(path, index)
                if os.path.exists(index):
                    path = index
                    break
            else:
                return self.list_directory(path)
        ctype = self.guess_type(path)
        try:
            f = open(path, 'rb')
        except OSError:
            self.send_error(HTTPStatus.NOT_FOUND, "File not found")
            return None
        try:
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-type", ctype)
            fs = os.fstat(f.fileno())
            self.send_header("Content-Length", str(fs[6]))
            self.send_header("Last-Modified", self.date_time_string(fs.st_mtime))
            self.end_headers()
            return f
        except:
            f.close()
            raise


if __name__ == '__main__':

    handler = RESTfulHandler
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--cgi', action='store_true',
                       help='Run as CGI Server')
    parser.add_argument('--bind', '-b', default='', metavar='ADDRESS',
                        help='Specify alternate bind address '
                             '[default: all interfaces]')
    parser.add_argument('port', action='store',
                        default=8000, type=int,
                        nargs='?',
                        help='Specify alternate port [default: 8000]')
    args = parser.parse_args()
    if args.cgi:
        handler_class = http.server.CGIHTTPRequestHandler
    else:
        handler_class = handler # http.server.SimpleHTTPRequestHandler (old default handler)
    http.server.test(HandlerClass=handler_class, port=args.port, bind=args.bind)