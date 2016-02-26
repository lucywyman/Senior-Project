#!/usr/bin/python

import http.server
import socketserver
import argparse
import json
import psycopg2
import psycopg2.extras
import command_dict
from datetime import datetime

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
        
        if command == 'course':
            if subcommand == 'view':
                
                #check data to build where clause
                condition = None
                length = len(data)
                
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