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
from sql_dict import sql
import os
import cgi
import ast
from shutil import move, rmtree

# Connect to an existing database
conn = psycopg2.connect("dbname=postgres user=postgres password=killerkat5", cursor_factory= psycopg2.extras.RealDictCursor)
conn.autocommit = True



PORT = 8000
SERVER = 'localhost'
class RESTfulHandler(http.server.BaseHTTPRequestHandler):

    def do_GET(self):
        """Serve a GET request."""

        # split path into components
        path = self.path
        if path.startswith('/') and path.endswith('/'):
            path = path.split('/')
            path = path[1:-1]
        elif path.startswith('/') and not path.endswith('/'):
            path = path.split('/')
            path = path[1:]

        # if path isn't length 2, then it's a bad
        # path and we should just stop
        if len(path) != 2:
            self.send_response(404)
            self.end_headers()
            return



        # create cursor for querying db
        cur = conn.cursor()

        command = path[0]
        subcommand = path[1]

        try:
            data = self.rfile.read(int(self.headers['Content-Length'])).decode("UTF-8")
            data = json.loads(data)
        except:
            data = {}

        condition = None
        length = len(data)


        select = []
        tables = []
        for row in sql[command][subcommand]['required']:
            if row[0] not in tables:
                tables += [row[0]]
            select.append(row)


        # translate keys to db keys
        tmp = {}
        for key in data:
            tmp[command_dict.options[key]['key']] = data[key]


        data = {}
        for key in tmp:
            data[key] = tmp[key]


        tmp = data.keys()
        for key, value in sql[command][subcommand]['optional'].items():
            if any(i in key for i in tmp):
                for row in value:
                    if row[0] not in tables:
                        tables += [row[0]]
                    select.append(row)


        # This list comphresion filters out any joins involving user
        # that do not join to the allowed table
        if 'allowed' in sql[command][subcommand]:
            for row in sql[command][subcommand]['allowed']:
                if row[1] not in tables:
                    tables += [row[1]]
        print(tables)
        print("-----")

        tmp = db_graph.generate_joins(db_graph.graph, sql[command][subcommand]['table'], tables)
        print(tmp)
        print("-----")
        # remove assignments join path and manually add
        # teachers_teach_courses join path
        # both paths have cost of two, but assignments path hides courses
        # with no associated assignments
        if command == 'course':
            not_allowed = ['assignments', 'tas', 'tas_assist_in_courses', 'tas_assigned_students']
            tmp = [x for x in tmp if (x[0] not in not_allowed) and (x[1] not in not_allowed)]
            tmp.insert(0,['courses', 'teachers_teach_courses', 'course_id', 'course_id'])
            tmp.insert(0,['teachers_teach_courses', 'teachers', 'teacher_id', 'teacher_id'])
            tmp.insert(0,['teachers', 'users', 'teacher_id', 'user_id'])

        join_set = ([x for x in tmp
            if (any(y[0] for y in tmp if (y[0]=='users' or y[1]=='users')))
               and (
                (
                    (x[0]=='users') and
                    (x[1] in [z[1] for z in sql[command][subcommand]['allowed']])
                    )
               or
               (
                    (x[1]=='users') and
                    (x[0] in [z[1] for z in sql[command][subcommand]['allowed']])
                    )
               )
               or ((x[0]!='users') and (x[1]!='users'))
            ])


        query = """SELECT DISTINCT """

        # generate list of keys to select
        if sql[command][subcommand]['allowed'] and len(sql[command][subcommand]['allowed'])>0:
            tmp = sql[command][subcommand]['allowed']
            query += ", ".join(
                ["{0}.{1} AS {2}".format(a[2], b[1], b[2])
                    for a in tmp for b in select
                    if (a[0]==b[0]) and (a[1]==b[3]) and (b[1]!=b[2])
                    ]
                + ["{0}.{1} AS {2}".format(x[0], x[1], x[2]) for x
                    in select if (x[1] != x[2]) and (x[0]!='users')]
                + ["{0}.{1}".format(x[0], x[1]) for x
                    in select if (x[1] == x[2])]
                )

        else:
            query += ", ".join(
                ["{0}.{1} AS {2}".format(x[0], x[1], x[2]) for x
                    in select if x[1] != x[2]]
                + ["{0}.{1}".format(x[0], x[1]) for x
                    in select if x[1] == x[2]]
                )

        query += " FROM " + sql[command][subcommand]['table']

        used_tables = [sql[command][subcommand]['table']]
        used_users = []
        join_size_old = 0
        join_size_new = 1



        print(join_set)
        print("-----")
        # This algorithm is designed to keep going over possible
        # joins until a pass is made where no joins are used.
        # This allows us to assume that list of joins is unordered
        # and as long as one new join is made each pass, that
        # opens the oppurtunity for new joins to be made in the
        # following pass
        while join_size_new != join_size_old:
            join_size_old = len(used_tables) + len(used_users)
            for join in join_set:
                print("join, used tables, len(allowed), used users:")
                print(join)
                print(used_tables)
                print(len(sql[command][subcommand]['allowed']))
                print(used_users)
                print("--------")
                if (join[0] in used_tables) != (join[1] in used_tables):
                    if (join[0] == 'users' and len(sql[command][subcommand]['allowed']) > 0):
                        print("entered join[0]=='users' branch:")
                        tmp = [x[2] for x in sql[command][subcommand]['allowed'] if x[1]==join[1]]
                        print(tmp)
                        print("--------")
                        if tmp and tmp[0] not in used_users:
                            query += (" INNER JOIN " + join[0] + " AS "
                                + tmp[0] + " ON " + tmp[0] + "." + join[2] + "=" + join[1] + "." + join[3] + " ")
                            used_users.append(tmp[0])
                    elif (join[1] == 'users' and len(sql[command][subcommand]['allowed']) > 0):
                        tmp = [x[2] for x in sql[command][subcommand]['allowed'] if x[1]==join[0]]
                        if tmp and tmp[0] not in used_users:
                            query += (" INNER JOIN " + join[1] + " AS "
                                + tmp[0] + " ON " + tmp[0] + "." + join[3] + "=" + join[0] + "." + join[2] + " ")
                            used_users.append(tmp[0])
                    elif join[0] in used_tables and join[0]!='users':
                        # print(query)
                        query += " INNER JOIN " + join[1] + " ON " + join[0] + "." + join[2] + "=" + join[1] + "." + join[3] + " "
                        used_tables.append(join[1])
                    elif join[1] in used_tables and join[1]!='users':
                        # print(query)
                        query += " INNER JOIN " + join[0] + " ON " + join[0] + "." + join[2] + "=" + join[1] + "." + join[3] + " "
                        used_tables.append(join[0])
            join_size_new = len(used_tables) + len(used_users)

        # if allowed table exists and is longer than one, we need to use
        # id numbers instead of onids
        if sql[command][subcommand]['allowed'] and len(sql[command][subcommand]['allowed']) > 0:
            if 'teacher_id' in data:
                cur.execute("SELECT users.user_id FROM users INNER JOIN teachers ON users.user_id=teachers.teacher_id WHERE users.username=%s", (data['teacher_id'][0],))
                data['teacher_id'][0] = cur.fetchone()['user_id']
            if 'student_id' in data:
                cur.execute("SELECT users.user_id FROM users INNER JOIN students ON users.user_id=students.student_id WHERE users.username=%s", (data['student_id'][0],))
                data['student_id'][0] = cur.fetchone()['user_id']
            if 'ta_id' in data:
                cur.execute("SELECT users.user_id FROM users INNER JOIN tas ON users.user_id=tas.ta_id WHERE users.username=%s", (data['ta_id'][0],))
                data['ta_id'][0] = cur.fetchone()['user_id']

        #check data to build where clause
        print(select)
        print("-----")
        print('data')
        print(data)

        # if allowed table exists and is longer than one, we need to use
        # id numbers instead of onids
        if sql[command][subcommand]['allowed'] and len(sql[command][subcommand]['allowed']) > 0:
            tmp = sql[command][subcommand]['allowed']
            if length > 0:
                condition = " WHERE " + " AND ".join(
                    ["{0}.{1}=%({2})s".format(a[2], b[1], b[1])
                    for a in tmp for b in select
                    if (a[0]==b[0]) and (a[1]==b[3]) and (b[1]!=b[2]) and (b[1] in data)]
                    +
                    ["{0}.{1}=%({2})s".format(x[0], x[1], x[1]) for x
                    in select if (x[1] in data) and (x[1] == x[2])]
                    )
        else:
            if length > 0:
                condition = " WHERE " + " AND ".join(
                    ["{0}.{1}=%({2})s".format(x[0], x[1], x[1]) for x
                    in select if (x[1] in data) and (x[1] == x[2])]
                    +
                    ["{0}.{1}=%({2})s".format(x[0], x[1], x[2]) for x
                    in select if (x[2] in data) and (x[1]=='username') and (x[1] != x[2])]
                    )

        if condition != None:
            query += condition

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

        result = cur.fetchall()
        print(result)

        for entry in result:
            if 'submission_date' in entry:
                entry['submission_date'] = entry['submission_date'].strftime('%x %X')
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
        path = self.path
        if path.startswith('/') and path.endswith('/'):
            path = path.split('/')
            path = path[1:-1]
        elif path.startswith('/') and not path.endswith('/'):
            path = path.split('/')
            path = path[1:]

        # if path isn't length 2, then it's a bad
        # path and we should just stop
        if len(path) != 2:
            self.send_response(404)
            self.end_headers()
            return


        # create cursor for querying db
        cur = conn.cursor()

        command = path[0]
        subcommand = path[1]

        print(self.headers)

        data = None
        fileitem = None

        if self.headers['Content-Type'] == 'application/json':
            try:
                data = self.rfile.read(int(self.headers['Content-Length'])).decode("UTF-8")
                data = json.loads(data)
            except:
                data = {}

        elif 'multipart/form-data' in self.headers['Content-Type']:

            form = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={'REQUEST_METHOD':'POST',
                         })
            # print("Form:")
            print(form)
            variable = ""
            value = ""
            data = {}
            print(form.keys())
            for key in form.keys():
                if key not in ['file', 'filepath']:
                    variable = str(key)
                    value = str(form.getvalue(variable))
                    print("value: {0}".format(value))

                    #TODO Lists should result in mutiple sends from cli, so this should eventually be removed. Fixes items coming in quoted array or makes item into array.
                    try:
                        data[variable] = ast.literal_eval(value)
                    except:
                        data[variable] = [str(value)]

                    if type(data[variable]) != type([]):
                        data[variable] = [str(value)]

            print(data)

            fileitem = form['file']

            # Test if the file was uploaded
            if fileitem.filename:
               fn = os.path.basename(fileitem.filename)
               open(os.path.normpath(sql['basedir'] + fn), 'wb').write(fileitem.file.read())
               message = 'The file "' + fn + '" was uploaded successfully'
            else:
               message = 'No file was uploaded'

            print(message)

            #TODO add logic to replace test update with test add if test is already being used by a version.

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
                cur.execute("""SELECT MAX(versions.version_id) AS max_version FROM versions GROUP BY versions.assignment_id HAVING assignment_id=%(assignment-id)s""", data)
                data['version']= []
                data['version'].append(cur.fetchone()['max_version'])
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



            filepath = data.pop('filepath', None)
            aid = None

            if command == 'submission':
                aid = data.pop('assignment-id', None)

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

            if command == 'submission':
                query += ") RETURNING submission_id"
            elif command == 'test':
                query += ") RETURNING test_id"
            else:
                query += ")"

            # TODO - Quick workaround for data being in arrays
            # How to deal with when multiple values available?
            print(data)
            for k in data:
                data[k] = data[k][0]

            print(query)
            print(data)

            if command == 'submission':
                fn = os.path.basename(fileitem.filename)
                cur.execute(query, data)
                ret = cur.fetchone()['submission_id']
                print(ret)
                fpath = sql['basedir'] + 'submission/{0}/{1}/sub/{2}'.format(aid, ret, fn)
                fpath = os.path.normpath(fpath)
                print("fpath: " + fpath)
                os.makedirs(os.path.dirname(fpath), exist_ok=True)
                move(os.path.normpath(sql['basedir'] + fn), fpath)

            elif command == 'test':
                fn = os.path.basename(fileitem.filename)
                cur.execute(query, data)
                ret = cur.fetchone()['test_id']
                print(ret)
                fpath = sql['basedir'] + 'tests/{0}/{1}'.format(ret, fn)
                fpath = os.path.normpath(fpath)
                print("fpath: " + fpath)
                os.makedirs(os.path.dirname(fpath), exist_ok=True)
                move(os.path.normpath(sql['basedir'] + fn), fpath)
            else:
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


            filepath = data.pop('filepath', None)

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

            if command == 'test':
                fn = os.path.basename(fileitem.filename)
                ret = data[idkey]

                print(ret)
                fpath = sql['basedir'] + 'tests/{0}/{1}/'.format(ret, fn)
                fpath = os.path.normpath(fpath)
                print("fpath: " + fpath)
                os.makedirs(os.path.dirname(fpath), exist_ok=True)

                # Clear test directory before uploading new file
                delpath = sql['basedir'] + 'tests/{0}/'.format(ret)
                flist = [x for x in os.listdir(delpath)]
                for file in flist:
                    os.remove(os.path.normpath(delpath + file))

                move(os.path.normpath(sql['basedir'] + fn), fpath)

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
        path = self.path
        if path.startswith('/') and path.endswith('/'):
            path = path.split('/')
            path = path[1:-1]
        elif path.startswith('/') and not path.endswith('/'):
            path = path.split('/')
            path = path[1:]

        # if path isn't length 2, then it's a bad
        # path and we should just stop
        if len(path) != 2:
            self.send_response(404)
            self.end_headers()
            return

        # create cursor for querying db
        cur = conn.cursor()

        command = path[0]
        subcommand = path[1]

        try:
            data = self.rfile.read(int(self.headers['Content-Length'])).decode("UTF-8")
            data = json.loads(data)
        except:
            data = {}

        print(data)

        if subcommand == 'delete':
            table = None
            if command == 'assignment':
                table = 'assignments'
            elif command == 'ce':
                table = 'common_errors'
                #TODO - check if text is file path, delete file if is
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
            elif command == 'ta':
                if 'course-id' in data:
                    table = 'tas_assist_in_courses'
                else:
                    table = 'tas'
                cur.execute("SELECT users.user_id FROM users INNER JOIN tas ON users.user_id=tas.ta_id WHERE users.username=%s", (data['ta'][0],))
                data['ta'][0] = cur.fetchone()['user_id']
            elif command == 'tag':
                table = 'assignments_have_tags'
                if 'tags' in data:
                    cur.execute("SELECT tags.tag_id FROM tags WHERE tags.text=%s", (data['tags'][0],))
                    # TODO - only want to show teacher's own assignments
                    # join to assignments to teachers and filter by name
                    data['tags'][0] = cur.fetchone()['tag_id']
            elif command == 'test':
                table = 'tests'




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


            if command == 'test':
                sym_safe = False
                try:
                    sym_safe = rmtree.avoids_symlink_attacks
                except:
                    pass

                ret = data['test-id']
                delpath = sql['basedir'] + 'tests/{0}/'.format(ret)

                if sym_safe:
                    rmtree(os.path.normpath(delpath))

                else:
                    print("Warning: Test path '{0}' could not be automatically deleted because system does not support symlink attack protection.".format(os.path.normpath(delpath)))

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