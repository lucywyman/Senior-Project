#!/usr/bin/python

import http.server
import socketserver
from socketserver import ThreadingMixIn
import threading
import socket
import argparse
import json
import psycopg2
import psycopg2.extras
import command_dict
from datetime import datetime, timedelta
import db_graph
from sql_dict import sql
import os
import cgi
import ast
from shutil import move, rmtree
import stat
import logging
from sys import platform, exit
from passlib.hash import pbkdf2_sha512
import ssl
import queue
import rest_extend
import configparser


# private file with HTTP response codes
from HTTPStatus import HTTPStatus

class RESTfulHandler(http.server.BaseHTTPRequestHandler):

    def __init__(self, *args, **kwargs):

        self.uid = None

        # create logger for RESTfulHandler
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

        if not getattr(self.logger, 'handler_set', None):
            # create console handler
            self.ch = logging.StreamHandler()
            self.ch.setLevel(logLevel)

            # create formatter
            self.formatter = logging.Formatter(
                "%(asctime)s - %(funcName)s - %(levelname)s: %(message)s"
                )

            # add formatter to console handler
            self.ch.setFormatter(self.formatter)

            # add console handler to logger
            self.logger.addHandler(self.ch)

            self.logger.handler_set = True

        super(RESTfulHandler, self).__init__(*args, **kwargs)

    def do_GET(self):
        """Serve a GET request."""
        self.logger.info("START")

        path = self.parse_path()

        # end response if serving favicon or path is wrong length
        if self.favicon_check(path) or not self.path_check(path, 2):
            self.logger.info("END")
            return

        command = path[0]
        subcommand = path[1]

        # create cursor for querying db
        cur = conn.cursor()

        self.uid = self.basic_auth()
        # end response if authorization failed
        if not self.uid:
            self.logger.info("END")
            return

        auth_level = self.get_auth_level(self.uid)
        # end response if unable to determine level
        if not auth_level:
            self.logger.info("END")
            return

        # end response if auth_level is not authorized
        # to use command subcommand
        if not self.check_auth_level(command, subcommand, auth_level):
            self.logger.info("END")
            return

        data = self.get_data()[0]


        # build list of attributes to select and tables to join
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


        # empty out data dictionary and fill with renamed data keys
        data = {}
        for key in tmp:
            data[key] = tmp[key]


        # check for applicable optional attributes in data and
        # update select and table appropriately
        for key, value in sql[command][subcommand]['optional'].items():
            if any(i in key for i in data.keys()):
                for row in value:
                    if row[0] not in tables:
                        tables += [row[0]]
                    select.append(row)


        # This list comphresion filters out any joins involving user
        # that do not join to the allowed table.
        if 'allowed' in sql[command][subcommand]:
            for row in sql[command][subcommand]['allowed']:
                if row[1] not in tables:
                    tables += [row[1]]
        self.logger.debug(tables)


        # Generate list of joins
        tmp = db_graph.generate_joins(
            db_graph.graph,
            sql[command][subcommand]['table'],
            tables
            )
        self.logger.debug(tmp)

        # remove assignments join path and manually add
        # teachers_teach_courses join path
        # both paths have cost of two, but assignments path hides courses
        # with no associated assignments
        if command == 'course':
            not_allowed = ['assignments', 'tas', 'tas_assist_in_courses',
                           'tas_assigned_students']
            tmp = [x for x in tmp
                if (x[0] not in not_allowed)
                and (x[1] not in not_allowed)
                ]
            tmp.insert(
                0,
                [
                    'courses',
                    'teachers_teach_courses',
                    'course_id',
                    'course_id'
                ]
                )
            tmp.insert(
                0,
                [
                    'teachers_teach_courses',
                    'teachers',
                    'teacher_id',
                    'teacher_id'
                ]
                )
            tmp.insert(
                0,
                [
                    'teachers',
                    'users',
                    'teacher_id',
                    'user_id'
                ]
                )

        join_set = ([x for x in tmp
            if (any(y[0] for y in tmp if (y[0]=='users' or y[1]=='users')))
               and (
                (
                    (x[0]=='users') and
                    (x[1] in [z[1] for z
                        in sql[command][subcommand]['allowed']]
                        )
                    )
               or
               (
                    (x[1]=='users') and
                    (x[0] in [z[1] for z
                        in sql[command][subcommand]['allowed']]
                        )
                    )
               )
               or ((x[0]!='users') and (x[1]!='users'))
            ])


        query = """SELECT DISTINCT """

        # generate list of keys to select
        if (sql[command][subcommand]['allowed']
            and len(sql[command][subcommand]['allowed'])>0
            ):

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




        # This algorithm is designed to keep going over possible
        # joins until a pass is made where no joins are used.
        # This allows us to assume that the list of joins is unordered
        # and as long as one new join is made each pass, that
        # opens the oppurtunity for new joins to be made in the
        # following pass
        while join_size_new != join_size_old:

            join_size_old = len(used_tables) + len(used_users)
            for join in join_set:

                if (join[0] in used_tables) != (join[1] in used_tables):

                    if (
                        join[0] == 'users'
                        and len(sql[command][subcommand]['allowed']) > 0
                        ):

                        tmp = [
                            x[2] for x in
                            sql[command][subcommand]['allowed']
                            if x[1]==join[1]
                            ]

                        if tmp and tmp[0] not in used_users:
                            if command=='student':
                                join_type = " RIGHT JOIN "
                            else:
                                join_type = " INNER JOIN "
                            query += (
                                join_type + join[0] + " AS "
                                + tmp[0] + " ON " + tmp[0] + "."
                                + join[2] + "=" + join[1] + "."
                                + join[3] + " "
                                )
                            used_users.append(tmp[0])

                    elif (
                        join[1] == 'users'
                        and len(sql[command][subcommand]['allowed']) > 0
                        ):

                        tmp = [
                            x[2] for x in
                            sql[command][subcommand]['allowed']
                            if x[1]==join[0]
                            ]

                        if tmp and tmp[0] not in used_users:
                            if command=='student':
                                join_type = " RIGHT JOIN "
                            else:
                                join_type = " INNER JOIN "
                            query += (
                                join_type + join[1] + " AS "
                                + tmp[0] + " ON " + tmp[0] + "." + join[3]
                                + "=" + join[0] + "." + join[2] + " "
                                )
                            used_users.append(tmp[0])

                    # TODO - test join needs to be RIGHT and LAST to avoid
                    # filtering out tests not linked to courses
                    elif join[0] in used_tables and join[0]!='users':
                        if command=='test' and join[1]=='tests':
                                join_type = " RIGHT JOIN "
                        else:
                                join_type = " INNER JOIN "
                        query += (
                            join_type + join[1] + " ON " + join[0]
                            + "." + join[2] + "=" + join[1] + "."
                            + join[3] + " "
                            )
                        used_tables.append(join[1])

                    elif join[1] in used_tables and join[1]!='users':
                        if command=='test' and join[1]=='tests':
                                join_type = " RIGHT JOIN "
                        else:
                                join_type = " INNER JOIN "
                        query += (
                            + "." + join[2] + "=" + join[1] + "."
                            + join[3] + " "
                            )
                        used_tables.append(join[0])


            join_size_new = len(used_tables) + len(used_users)

        # if allowed table exists and is longer than one,
        # we need to use id numbers instead of onids
        if (sql[command][subcommand]['allowed']
            and len(sql[command][subcommand]['allowed']) > 0
            ):
            if 'teacher_id' in data:
                cur.execute("""
                    SELECT users.user_id FROM users
                    INNER JOIN teachers ON users.user_id=teachers.teacher_id
                    WHERE users.username=%s
                    """, (data['teacher_id'][0],)
                    )
                data['teacher_id'][0] = cur.fetchone()['user_id']
            if 'student_id' in data:
                cur.execute("""
                    SELECT users.user_id FROM users
                    INNER JOIN students ON users.user_id=students.student_id
                    WHERE users.username=%s
                    """, (data['student_id'][0],)
                    )
                data['student_id'][0] = cur.fetchone()['user_id']
            if 'ta_id' in data:
                cur.execute("""
                    SELECT users.user_id FROM users
                    INNER JOIN tas ON users.user_id=tas.ta_id
                    WHERE users.username=%s
                    """, (data['ta_id'][0],)
                    )
                try:
                    data['ta_id'][0] = cur.fetchone()['user_id']
                except TypeError:
                    self.send_error(
                        HTTPStatus.NOT_FOUND,
                        'TA {0} not found'
                        .format(data['ta_id'][0])
                        )
                    self.end_headers()
                    self.logger.info("END")
                    return

        #check data to build where clause
        self.logger.debug(select)

        self.logger.debug(data)

        length = len(data)

        self.logger.debug("Length is: {0}".format(length))

        # Limit results to what user is authorized to see
        # i.e. A TA using course view will only see courses
        # they are assisting in
        if sql[command]['view']['limit'].get(auth_level, None):
            query += " WHERE " + sql[command]['view']['limit'][auth_level]
        else:
            msg = (
                "ERROR: Limit not found for {0} at auth_level: {1}"
                .format(command, auth_level)
                )
            self.logger.debug(msg)
            self.send_error(
                        HTTPStatus.NOT_FOUND,
                        msg
                        )
            self.end_headers()
            self.logger.info("END")
            return


        # if allowed table exists and is longer than one,
        # we need to use id numbers instead of onids
        condition = None
        if (sql[command][subcommand]['allowed']
            and len(sql[command][subcommand]['allowed']) > 0
            ):

            tmp = sql[command][subcommand]['allowed']
            self.logger.debug(
                "Allowed for {0} {1} is {2}"
                .format(
                    command,
                    subcommand,
                    tmp)
                )
            if length > 0:
                condition = " AND " + " AND ".join(
                    ["{0}.{1}=%({2})s".format(a[2], b[1], b[2])
                        for a in tmp for b in select
                        if (a[0]==b[0]) and (a[1]==b[3]) and (b[1]!=b[2])
                        and (b[2] in data)
                        ]
                    +
                    ["{0}.{1}=%({2})s".format(x[0], x[1], x[1])
                        for x in select if (x[1] in data)
                        and (x[1] == x[2])
                        ]
                    )
        else:
            if length > 0:
                condition = " AND " + " AND ".join(
                    ["{0}.{1}=%({2})s".format(x[0], x[1], x[1]) for x
                        in select if (x[1] in data) and (x[1] == x[2])
                        ]
                    +
                    ["{0}.{1}=%({2})s".format(x[0], x[1], x[2]) for x
                        in select if (x[2] in data) and (x[1]=='username')
                        and (x[1] != x[2])
                        ]
                    )

        if condition != None:
            query += condition

        # TODO - Quick workaround for data being in arrays
        # How to deal with when multiple values available?
        for k in data:
            data[k] = data[k][0]

        # Set uid for limiting query results
        data['uid'] = self.uid

        # execute query
        self.logger.info(query)
        self.logger.debug(data)
        cur.execute(query, data)

        result = cur.fetchall()
        self.logger.debug(result)

        if result:
            self.send_response(HTTPStatus.OK)

        else:
            self.send_response(HTTPStatus.NO_CONTENT)

        self.send_header('Content-type', 'application/json')
        self.end_headers()

        # transform datetime objects to strings for transmission
        for entry in result:
            if 'submission_date' in entry:
                entry['submission_date'] = (
                    entry['submission_date'].strftime('%x %X')
                    )
            if 'begin_date' in entry:
                try:
                    entry['begin_date'] = (
                        entry['begin_date'].strftime('%x %X')
                        )
                except:
                    pass
            if 'end_date' in entry:
                try:
                    entry['end_date'] = entry['end_date'].strftime('%x %X')
                except:
                    pass


        # send result as json string
        result = json.dumps(result)

        self.wfile.write(bytes(result, 'UTF-8'))

        self.logger.info("END")


    def do_POST(self):
        """Serve a POST request.

        Most database insertions and changes are done through POST requests.

        The basic organization is:
            Preparation
                Get path, user id, authorization level etc.
            Login Command and link/unlink Subcommand
                The login command and link/unlink subcommands are handled
                seperately from the rest of the commands/subcommands
                because they do not fit the same pattern.

            Add and Update Subcommands
                Add and update each have their own if block, each of
                which is further divided into if blocks for each command.
                I took this approach since the code for each subcommand
                is relative similar across the set of commands.

                Preprocessing
                    Preprocessing consists mostly of specifying which table to
                    target, and fixing any problems with the data, such as
                    changing a user name to a user id.

                Query Building
                    The query is built based on preprocessing selections and
                    available data.

                    NOTE: User supplied data is securely inserted using module
                    supplied method, in order to prevent injection attacks.

                Query Execution
                    Any commands requiring processing beyond query execution
                    are handled here. If the command didn't require cleanup
                    then the query is simply executed


        """
        #####################
        # Preparation Section
        #####################
        self.logger.info("START")

        path = self.parse_path()

        # end response path is wrong length
        if not self.path_check(path, 2):
            self.logger.info("END")
            return

        command = path[0]
        subcommand = path[1]

        if command=='login' and subcommand=='new':
            self.create_user()
            self.logger.info("END")
            return

        # create cursor for querying db
        cur = conn.cursor()

        self.uid = self.basic_auth()
        # end response if authorization failed
        if not self.uid:
            self.logger.info("END")
            return

        auth_level = self.get_auth_level(self.uid)
        # end response if unable to determine level
        if not auth_level:
            self.logger.info("END")
            return

        data, fileitem = self.get_data()


        ###################
        # Login Section
        ###################
        if command=='login':
            # login as user
            # at this point the user has already been authenticated
            # so we simply send a response letting them know their
            # auth_level
            if subcommand=='as':

                self.logged_in(data, self.uid, auth_level)

                self.logger.info("END")
                return

            # update user password
            # user has already been authenticated with old password
            # so we can simply hash and insert the new password here
            if subcommand=='update':
                hash = pbkdf2_sha512.encrypt(data['new-password'][0])

                try:
                    cur.execute("""
                        UPDATE users
                        SET auth=%s
                        WHERE user_id=%s
                        """, (hash, self.uid)
                        )
                except:
                    self.send_error(
                        HTTPStatus.BAD_REQUEST,
                        'failed to update password for user {0}'
                        .format(data['name'][0])
                        )
                    raise
                else:
                    self.logged_in(data, self.uid, auth_level)

                self.logger.info("END")
                return


        # end response if auth_level is forbidden
        # from using command subcommand
        if not self.check_auth_level(command, subcommand, auth_level):
            self.logger.info("END")
            return

        # check that current user is associated with data
        # they are attempting to add/update
        if not self.uid_access_check(command, subcommand, auth_level, data):
            self.logger.info("END")
            return

        ######################
        # Link/Unlink Section
        ######################
        if subcommand == 'link' or subcommand == 'unlink':
            table = None

            if command == 'test':

                data = self.test_link(command, subcommand, data)

                if data == None:
                    self.logger.info("END")
                    return

            # TODO - implment other links such as CE link



        # TODO - add logic to replace test update with test add
        # if test is already being used by a version.

        ###################
        # Add Section
        ###################
        if subcommand == 'add':
            table = None
            aid = None

            if command == 'assignment':
                table = 'assignments'
                #TODO implement tags

                # default begin date for assigments is today
                if 'begin' in data:
                    data['begin'][0] = datetime.strptime(
                        data['begin'][0], '%x %X'
                        )
                else:
                    data['begin'] = []
                    data['begin'] = [
                        datetime.now()
                        .replace(
                            hour=0,
                            minute=0,
                            second=0,
                            microsecond=0
                            )
                        ]

                # default end is 11:59:59 pm 14 days after begin date
                if 'end' in data:
                    data['end'][0] = datetime.strptime(
                        data['end'][0], '%x %X'
                        )
                else:
                    data['end'] = []
                    data['end'] = [
                        (datetime.now() + timedelta(days=14))
                        .replace(
                            hour=23,
                            minute=59,
                            second=59,
                            microsecond=0
                            )
                        ]

                # default submission limit is 0 (unlimited submissions)
                if 'limit' not in data:
                    data['limit'] = []
                    data['limit'] = [0]

                # default late submission limit is 0 days
                if 'late' not in data:
                    data['late'] = []
                    data['late'] = [0]

                # default feedback level is 1
                if 'level' not in data:
                    data['level'] = []
                    data['level'] = [1]


            elif command == 'ce':
                table = 'common_errors'


            elif command == 'course':
                table = 'courses'
                if 'dept' in data:
                    cur.execute("""
                        SELECT depts.dept_id
                        FROM depts
                        INNER JOIN courses ON courses.dept_id=depts.dept_id
                        WHERE depts.dept_name=%s
                        """, (data['dept'][0],)
                        )
                    try:
                        data['dept'][0] = cur.fetchone()['dept_id']
                    except TypeError:
                        self.logger.info(
                            "Department {0} not found"
                            .format(
                                data['dept'][0]
                                )
                            )
                        self.send_error(
                            HTTPStatus.NOT_FOUND,
                            "Department {0} not found".format(data['dept'][0])
                            )
                        return

            elif command == 'group':
                table = 'tas_assigned_students'
                # convert onids to user_ids
                # TODO - This doesn't support multiples as it should
                cur.execute("""
                    SELECT users.user_id FROM users
                    INNER JOIN students ON users.user_id=students.student_id
                    WHERE users.username=%s
                    """, (data['student'][0],)
                    )
                data['student'][0] = cur.fetchone()['user_id']
                cur.execute("""
                    SELECT users.user_id FROM users
                    INNER JOIN tas ON users.user_id=tas.ta_id
                    WHERE users.username=%s
                    """, (data['ta'][0],)
                    )
                data['ta'][0] = cur.fetchone()['user_id']


            elif command == 'student':
                table = 'students_take_courses'
                # convert onids to user_ids
                # TODO - This doesn't support multiples as it should
                cur.execute("""
                    SELECT users.user_id FROM users
                    INNER JOIN students ON users.user_id=students.student_id
                    WHERE users.username=%s
                    """, (data['student'][0],)
                    )
                data['student'][0] = cur.fetchone()['user_id']


            elif command == 'submission':
                table = 'submissions'

                # Assignment-id needs to be removed from the data set before
                # the query is built, since version_id is tracked, not
                # assignment-id
                aid = data.pop('assignment-id', None)[0]

                cur.execute("""
                    SELECT MAX(versions.version_id) AS max_version
                    FROM versions
                    GROUP BY versions.assignment_id
                    HAVING assignment_id=%s
                    """, (aid,)
                    )
                data['version']= []
                data['version'].append(cur.fetchone()['max_version'])


            elif command == 'ta':
                if 'course-id' in data:
                    table = 'tas_assist_in_courses'
                else:
                    table = 'tas'
                cur.execute("""
                    SELECT users.user_id FROM users
                    WHERE users.username=%s
                    """, (data['ta'][0],)
                    )
                data['ta'][0] = cur.fetchone()['user_id']


            elif command == 'tag':
                table = 'assignments_have_tags'
                # TODO - insert ignore tags before getting tag_id
                # make sure they exist) (this may require delete,
                # then insert for postgre?)
                cur.execute("""
                    SELECT tags.tag_id FROM tags
                    WHERE tags.text=%s
                    """, (data['tags'][0],)
                    )

                data['tags'][0] = cur.fetchone()['tag_id']


            elif command == 'test':
                table = 'tests'
                data['teacher'] = [self.uid]

                if 'assignment-id' in data.keys():
                    aid = data.pop('assignment-id', None)[0]


            ######################################
            # Add Query Building Section
            ######################################
            filepath = data.pop('filepath', None)


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
            elif command == 'course':
                query += ") RETURNING course_id"
            elif command == 'assignment':
                query += ") RETURNING assignment_id"
            elif command == 'ce':
                query += ") RETURNING ce_id"
            else:
                query += ")"

            # TODO - Quick workaround for data being in arrays
            # How to deal with when multiple values available?
            self.logger.debug(data)
            for k in data:
                data[k] = data[k][0]

            self.logger.debug(query)
            self.logger.debug(data)


            ######################################
            # Add Query Execution Section
            ######################################
            if command == 'submission':
                # After a new submission is added, we need to
                # move the submission from its temporary location
                # and call the tester on it.

                # add submission
                cur.execute(query, data)

                # move submission
                fn = os.path.basename(fileitem.filename)
                ret = cur.fetchone()['submission_id']

                delpath, subpath, temppath = self.get_path(
                    ret, fn, self.uid, aid
                    )

                move(temppath, subpath)

                # call tester
                if self.submit(ret) == 0:
                    self.logger.debug(
                        "Submission successfully sent to tester!"
                        )
                else:
                    self.logger.debug("Submission to tester failed!")


            elif command == 'test':

                # Add test to database
                cur.execute(query, data)
                ret = cur.fetchone()['test_id']
                self.logger.debug("TestID: {0}".format(ret))

                # Move test file to appropriate location
                fn = os.path.basename(fileitem.filename)

                delpath, fpath, temppath = self.get_path(
                    ret, fn, self.uid
                    )

                move(temppath, fpath)

                # if assignment-id was set, link new test to that assignment
                if aid:
                    data['assignment-id'] = [aid]
                    data['test-id'] = [ret]
                    self.test_link('test', 'link', data)

                    if data == None:
                        self.logger.info("END")
                        return



            elif command == 'course':

                # add new course to database
                cur.execute(query, data)

                # add current user as instructor for new course
                ret = cur.fetchone()['course_id']
                self.logger.debug("New CourseID {0}".format(ret))
                cur.execute("""
                    INSERT INTO teachers_teach_courses (teacher_id, course_id)
                    VALUES (%s, %s)
                    """, (self.uid, ret)
                    )

            elif command == 'assignment':

                # add new assignment to database
                cur.execute(query, data)

                # add current user as instructor for new assignment
                ret = cur.fetchone()['assignment_id']
                self.logger.debug("New AssignmentID: {0}".format(ret))
                cur.execute("""
                    UPDATE assignments
                    SET teacher_id=%s
                    WHERE assignment_id=%s
                    """, (self.uid, ret)
                    )

                # create first version of assignment
                cur.execute("""
                    INSERT INTO versions (assignment_id)
                    VALUES (%s)
                    """, (ret,)
                    )

            elif command == 'ce':

                # add new common error to database
                cur.execute(query, data)

                # add current user as owner for new common error
                ret = cur.fetchone()['ce_id']
                self.logger.debug("New ceID: {0}".format(ret))
                cur.execute("""
                    UPDATE common_errors
                    SET teacher_id=%s
                    WHERE ce_id=%s
                    """, (self.uid, ret)
                    )
            else:
                try:
                    cur.execute(query, data)
                except psycopg2.IntegrityError:
                    # TODO Send error message here.
                    self.logger.exception("IntegrityError exception caught")


        ######################################
        # Update Subcommand Section
        ######################################
        if subcommand == 'update':
            idkey = None
            table = None


            if command == 'assignment':
                idkey = 'assignment-id'
                table = 'assignments'
                #TODO implement tags

                data['teacher'] = [self.uid]

                if 'begin' in data:
                    data['begin'][0] = datetime.strptime(
                        data['begin'][0], '%x %X'
                        )
                if 'end' in data:
                    data['end'][0] = datetime.strptime(
                        data['end'][0], '%x %X'
                        )


            elif command == 'ce':
                idkey = 'ce-id'
                table = 'common_errors'


            elif command == 'course':
                idkey = 'course-id'
                table = 'courses'
                if 'dept' in data:
                    cur.execute("""
                        SELECT depts.dept_id FROM depts
                        INNER JOIN courses ON courses.dept_id=depts.dept_id
                        WHERE depts.dept_name=%s
                        """, (data['dept'][0],)
                        )
                    data['dept'][0] = cur.fetchone()['dept_id']


            elif command == 'grade' or command == 'submission':
                #TODO - how is this affected by edge case where multiple
                # students create one submission? Also students submission
                # add needs to support students keyword
                idkey = 'submission'
                if 'assignment-id' in data:
                    # get student id from onid
                    cur.execute("""
                        SELECT users.user_id FROM users
                        INNER JOIN students
                        ON users.user_id=students.student_id
                        WHERE users.username=%s
                        """, (data['student'][0],)
                        )
                    data['student'][0] = cur.fetchone()['user_id']
                    # use assignment-id and student-id to select
                    # correct submission-id


                    cur.execute("""
                        SELECT MAX(S.submission_id)
                        FROM submissions AS S
                        INNER JOIN students_create_submissions AS C
                        ON S.submission_id=C.submission_id
                        INNER JOIN versions AS V
                        ON S.version_id=V.version_id
                        WHERE
                            V.assignment_id=%s
                            AND C.student_id=%s
                        """, (data['assignment-id'][0], data['student'][0],)
                        )
                    data['submission'] = []
                    data['submission'].append(cur.fetchone()['max'])
                    # remove unused keys
                    data.pop('assignment-id')
                    data.pop('student')
                table = 'submissions'


            elif command == 'test':
                idkey = 'test-id'
                table = 'tests'


            ######################################
            # Update Query Building Section
            ######################################
            filepath = data.pop('filepath', None)

            # -1 is because an update command must include an idkey
            length = len(data) - 1
            keys = data.keys()

            query = "UPDATE " + table + " SET "
            for opt in keys:
                if opt != idkey:
                    query += (
                        command_dict.options[opt]['key'] +
                        "=%(" + opt + ")s"
                        )
                    length -= 1
                    if length > 0:
                        query += ", "
            query += (
                " WHERE " + command_dict.options[idkey]['key'] +
                "=%(" + idkey + ")s"
                )


            # TODO - Quick workaround for data being in arrays
            # How to deal with when multiple values available?
            for k in data:
                data[k] = data[k][0]


            ######################################
            # Update Query Execution Section
            ######################################
            if command == 'test':
                # TODO - Add logic to do test add instead of test
                # update if test is linked to any versions.

                if fileitem is not None:
                    fn = os.path.basename(fileitem.filename)
                    ret = data[idkey]

                    delpath, fpath, temppath = self.get_path(
                        ret, fn, self.uid
                        )

                    # Clear test directory before uploading new file
                    flist = [x for x in os.listdir(delpath)]
                    for file in flist:
                        os.remove(os.path.normpath(
                            os.path.join(delpath, file)
                            )
                        )

                    move(temppath, fpath)

            print(query)
            print(data)
            cur.execute(query, data)

        self.send_response(HTTPStatus.OK)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

        # TODO - Add better confirmation message
        # result = cur.fetchall()
        # print(json.dumps(result, indent=2))
        # result = json.dumps(result)

        # self.wfile.write(bytes(result, 'UTF-8'))

        self.logger.info("END")

    def do_DELETE(self):
        """Serve a DELETE request"""
        self.logger.info("START")

        path = self.parse_path()

        # end response if path is wrong length
        if not self.path_check(path, 2):
            self.logger.info("END")
            return

        command = path[0]
        subcommand = path[1]
        self.logger.debug("Command: {}, Subcommand: {}".format(command,subcommand))

        # create cursor for querying db
        cur = conn.cursor()

        self.uid = self.basic_auth()
        # end response if authorization failed
        if not self.uid:
            self.logger.info("END")
            return

        auth_level = self.get_auth_level(self.uid)
        # end response if unable to determine level
        if not auth_level:
            self.logger.info("END")
            return

        # end response if auth_level is not authorized
        # to use command subcommand
        if not self.check_auth_level(command, subcommand, auth_level):
            self.logger.info("END")
            return

        data = self.get_data()[0]
        self.logger.debug("Data: {}".format(data))

        # check that current user is associated with data
        # they are attempting to delete
        if not self.uid_access_check(command, subcommand, auth_level, data):
            self.logger.info("END")
            return


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
                    cur.execute("""
                        SELECT users.user_id FROM users
                        INNER JOIN students
                        ON users.user_id=students.student_id
                        WHERE users.username=%s
                        """, (data['student'][0],)
                        )
                    data['student'][0] = cur.fetchone()['user_id']
                cur.execute("""
                    SELECT users.user_id FROM users
                    INNER JOIN tas
                    ON users.user_id=tas.ta_id
                    WHERE users.username=%s
                    """, (data['ta'][0],)
                    )
                data['ta'][0] = cur.fetchone()['user_id']
            elif command == 'student':
                table = 'students_take_courses'
                # convert onids to user_ids
                # TODO - This doesn't support multiples as it should
                cur.execute("""
                    SELECT users.user_id FROM users
                    INNER JOIN students
                    ON users.user_id=students.student_id
                    WHERE users.username=%s
                    """, (data['student'][0],)
                    )
                data['student'][0] = cur.fetchone()['user_id']
            elif command == 'ta':
                if 'course-id' in data:
                    table = 'tas_assist_in_courses'
                else:
                    table = 'tas'
                cur.execute("""
                    SELECT users.user_id FROM users
                    INNER JOIN tas ON users.user_id=tas.ta_id
                    WHERE users.username=%s
                    """, (data['ta'][0],)
                    )
                data['ta'][0] = cur.fetchone()['user_id']
            elif command == 'tag':
                table = 'assignments_have_tags'
                if 'tags' in data:
                    cur.execute("""
                        SELECT tags.tag_id FROM tags
                        WHERE tags.text=%s
                        """, (data['tags'][0],)
                        )
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
                delpath, fpath, temppath = self.get_path(
                    ret, '', self.uid
                    )

                if sym_safe:
                    rmtree(delpath)

                else:
                    self.logger.warning(
                        "Test path '{0}' could not be automatically"
                        " deleted because system does not support"
                        " symlink attack protection."
                        .format(delpath)
                        )

            self.logger.info(query)
            self.logger.debug(data)
            cur.execute(query, data)

        self.send_response(HTTPStatus.OK)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

        self.logger.info("END")



    def parse_path(self):
        # split path into components
        path = self.path
        if path.startswith('/') and path.endswith('/'):
            path = path.split('/')
            path = path[1:-1]
        elif path.startswith('/') and not path.endswith('/'):
            path = path.split('/')
            path = path[1:]

        return path

    def favicon_check(self, path):
        if len(path)==1 and path[0]=='favicon.ico':

            self.logger.debug("FAVICON CHECK")

            try:
                f = open('favicon.ico', 'rb')
            except OSError:
                self.send_error(
                    HTTPStatus.NOT_FOUND,
                    "File not found"
                    )
                return True
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "image/x-icon")
            fs = os.fstat(f.fileno())
            self.send_header("Content-Length", str(fs[6]))
            self.send_header(
                "Last-Modified", self.date_time_string(fs.st_mtime)
                )
            self.end_headers()
            self.wfile.write(f.read())
            f.close()

            return True

        return False


    def path_check(self, path, length):
        if len(path) != length:
            self.send_error(
                HTTPStatus.NOT_FOUND
                )
            self.end_headers()
            return False

        return True


    def get_data(self):

        data = {}
        fileitem = None

        self.logger.debug("Headers: {0}".format(self.headers))

        if self.headers.get('content-type') == 'application/json':

            self.logger.info("Data Type: JSON")

            try:
                data = self.rfile.read(
                    int(self.headers.get('content-length'))
                    ).decode("UTF-8")
                data = json.loads(data)
                self.logger.info("Data Loaded")
                self.logger.debug("Data: {0}".format(data))

            except ValueError as e:
                self.logger.info("ValueError: {0}".format(e.message))
                data = {}

            return data, None

        elif 'multipart/form-data' in self.headers.get('content-type'):

            self.logger.info("Data Type: multipart/form-data")

            # parse multipart/form-data into cgi.FieldStorage
            # data structure for ease of use.
            form = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={'REQUEST_METHOD':'POST',}
                         )

            data, fileitem = self.process_form(form)

        self.logger.debug("Data: {0}".format(data))
        self.logger.debug("FileItem: {0}".format(fileitem))
        return data, fileitem

    def process_form(self, form):
        variable = ""
        value = ""
        data = {}

        self.logger.debug("Form Keys: {0}".format(form.keys()))
        self.logger.debug("Processing Form Keys")
        for key in form.keys():
            if key not in ['file', 'filepath']:
                variable = str(key)
                value = str(form.getvalue(variable))
                self.logger.debug("Variable: {0}, value: {1}"
                    .format(variable, value)
                    )

                # TODO Lists should result in mutiple sends from
                # cli, so this should eventually be removed. Fixes
                # items coming in quoted array or makes item into
                # array.
                try:
                    data[variable] = ast.literal_eval(value)
                except SyntaxError as e:
                    self.logger.info(
                        "SyntaxError: {0} ({1}, {2})"
                            .format(e.msg, variable, value)
                        )
                    data[variable] = [str(value)]
                except ValueError as e:
                    self.logger.info(
                        "ValueError: ({0}, {1})"
                            .format(variable, value)
                        )
                    data[variable] = [str(value)]

                if type(data[variable]) != type([]):
                    data[variable] = [str(value)]

        fileitem = self.get_file(form)

        return data, fileitem

    def get_file(self, form):

        self.logger.debug(cgi.print_form(form))
        fileitem = form['file']

        self.logger.debug("FileItem: {}".format(fileitem))

        # Test if the file was uploaded
        if fileitem is not None and fileitem.filename:
            fn = os.path.basename(fileitem.filename)

            delpath, fpath, temppath = self.get_path(
                    '', fn, self.uid
                    )

            with open(temppath, 'wb') as f:
                f.write(fileitem.file.read())
            self.logger.debug('File "' + fn + '" saved to {0}'
                .format(temppath, fn)
                )
        else:
            # multipart/form-data should only be used when uploading
            # files. If there is no file, something went seriously wrong
            self.logger.warning('Error: No file was uploaded!')

        return fileitem

    def basic_auth(self):
        """Verifies authorization and returns user_id on success.

        Database stores hashed password for each user. We need hash
        the sent password and verify it against the stored hash.

        """


        fail_msg = "The username/password combination you entered is invalid"

        authorized = False

        authorization = self.headers.get("authorization")
        if authorization:
            authorization = self.parse_auth(authorization)
        else:
            self.logger.debug('AuthError: authorization header missing')
            self.send_error(
                HTTPStatus.UNAUTHORIZED,
                'authorization header missing'
                )
            return None

        cur = conn.cursor()
        cur.execute("""
            SELECT users.user_id, users.auth FROM users
            WHERE users.username=%s
            """, (authorization[0],)
            )
        result = cur.fetchone()

        if result:
            authorized = pbkdf2_sha512.verify(
                authorization[1],   # password
                result['auth']      # stored hash
                )
        else:
            self.logger.debug(
                'AuthError: user {0} not found'.format(authorization[0])
                )
            self.send_error(
                HTTPStatus.UNAUTHORIZED,
                fail_msg
                )
            return None

        if not authorized:
            self.logger.debug(
                'AuthError: user {0} entered incorrect password'
                .format(authorization[0])
                )
            self.send_error(
                HTTPStatus.UNAUTHORIZED,
                fail_msg
                )
            return None

        else:
            self.logger.info(
                'User: {0}, UID: {1}, successfully authorized'
                .format(authorization[0], result['user_id'])
                )

            return result['user_id']


    def parse_auth(self, authorization):

        # Modified from basic library code in Python 3.5 server.py
        # https://hg.python.org/cpython/file/3.5/Lib/http/server.py
        # lines 1038-1054
        authorization = authorization.split()
        if len(authorization) == 2:
            import base64, binascii
            if authorization[0].lower() == "basic":
                try:
                    authorization = authorization[1].encode('ascii')
                    authorization = base64.decodebytes(authorization).decode('ascii')
                except (binascii.Error, UnicodeError):
                    self.logger.debug(
                        'AuthError: Unable to decode auth string'
                        )
                    return None
                else:
                    authorization = authorization.split(':')
                    if len(authorization) == 2:
                        return authorization
            else:
                self.logger.debug(
                        'AuthError: auth type {0} instead of \'basic\''
                    .format(authorization[0].lower())
                    )
                return None

        else:
            self.logger.debug(
                    'AuthError: expected length 2, got len({0})'
                .format(len(authorization))
                )
            return None

    def get_auth_level(self, uid):

        cur = conn.cursor()

        cur.execute("""
            SELECT teachers.teacher_id from teachers
            WHERE teacher_id=%s
            """, (uid,)
            )
        if cur.fetchone():
            self.logger.debug(
                "UID: {0} authorized as teacher"
                .format(uid)
                )
            return 'teacher'


        cur.execute("""
            SELECT tas.ta_id from tas
            WHERE ta_id=%s
            """, (uid,)
            )
        if cur.fetchone():
            self.logger.debug(
                "UID: {0} authorized as ta"
                .format(uid)
                )
            return 'ta'


        cur.execute("""
            SELECT students.student_id from students
            WHERE student_id=%s
            """, (uid,)
            )
        if cur.fetchone():
            self.logger.debug(
                "UID: {0} authorized as student"
                .format(uid)
                )
            return 'student'

        self.logger.debug(
            "Error: UID {0} has no authorization level"
            .format(uid)
            )
        self.send_error(
            HTTPStatus.UNAUTHORIZED,
            "missing authorization level"
            )
        return None

    def check_auth_level(self, command, subcommand, auth_level):

        com = command_dict.commands[command][subcommand]['access']

        if com[auth_level]:
            return True

        self.logger.debug(
                'AuthError: auth_level {0} is not'
                ' authorized to use command {1} {2}'
                .format(auth_level, command, subcommand)
                )
        self.send_error(
            HTTPStatus.UNAUTHORIZED,
            'auth_level {0} is not authorized to use command {1} {2}'
            .format(auth_level, command, subcommand)
            )
        return False


    def submit(self, id):

        rest_extend.herald(self.server.q,id)
        return 0

    ##  s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    ##  try:
    ##      s.connect(('127.0.0.1', 9000))     #'\0recvPort')):
    ##  except:
    ##      # TODO - handle errors instead
    ##      raise
    ##  else:
    ##      msg = '{"sub_ID":' + str(id) + '}'
    ##      self.logger.debug(msg)
    ##      msg = msg.encode()
    ##      self.logger.debug(msg)
    ##      s.send(msg)
    ##      s.close()
    ##      return 1
    ##
    ##  return 0


    def create_user(self):

        data = self.get_data()[0]
        data['name'] = data['name'][0]
        data['password'] = data['password'][0]

        self.logger.debug(
                'Data: {0}'
                .format(data)
                )
        cur = conn.cursor()

        # confirm that user name is available
        cur.execute("""
            SELECT users.user_id, users.auth FROM users
            WHERE users.username=%(name)s
            """, data
            )
        result = cur.fetchone()

        if not result:
            self.logger.debug(
                'user {0} not found, attempting to create'
                .format(data['name'])
                )
            data['hash'] = pbkdf2_sha512.encrypt(data['password'])
            cur.execute("""
                INSERT INTO users (username, auth)
                VALUES (%(name)s, %(hash)s)
                RETURNING user_id
                """, data
                )
            new_id = cur.fetchone()['user_id']
            if new_id:
                self.logger.debug(
                    'user {0} created with UID {1}'
                    .format(data['name'], new_id)
                    )

                # add new user to students
                cur.execute("""
                    INSERT INTO students (student_id)
                    VALUES (%s)
                    """, (new_id,)
                    )

                response = {}
                response['name'] = data['name']
                response['user_id'] = new_id
                self.send_response(HTTPStatus.CREATED)

                self.send_header('Content-type', 'application/json')
                self.end_headers()
                response = json.dumps(response)

                self.wfile.write(bytes(response, 'UTF-8'))
            else:
                self.logger.debug(
                    'LoginError: user {0} creation failed'
                    .format(data['name'])
                    )
                self.send_error(
                    HTTPStatus.BAD_REQUEST,
                    'user {0} creation failed - contact administrator'
                    .format(data['name'])
                    )
            return

        else:
            self.logger.debug(
                'LoginError: user {0} already exists, could not create'
                .format(
                    data['name']
                    )
                )
            self.send_error(
                HTTPStatus.BAD_REQUEST,
                'user {0} already exists, could not create'
                .format(data['name'])
                )

        return

    def logged_in(self, data, uid, auth_level):
        self.send_response(HTTPStatus.OK)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

        response = {}

        try:
            response['name'] = data['name'][0]
        except KeyError:
            pass

        response['auth_level'] = auth_level
        response['uid'] = uid

        response = json.dumps(response)
        self.wfile.write(bytes(response, 'UTF-8'))

    def test_link(self, command, subcommand, data):


        # TODO - this should really be done as one transaction
        # to avoid possible race conditions
        # easiest solution may be to open new database connection with
        # out setting autocommit on it
        # the global connection object (conn) is shared by all threads, so
        # turning off autocommit temporarily might have unintended results


        # create cursor for querying db
        cur = conn.cursor()

        # get most current version number
        cur.execute("""
            SELECT MAX(versions.version_id)
            FROM versions
            WHERE versions.assignment_id=%s
            """, (data['assignment-id'][0],)
            )

        data['version'] = []
        data['version'] = [cur.fetchone()['max']]

        self.logger.debug("Version: {0}".format(data['version']))


        # check to see if target test is already linked or not linked
        # to current assignment version
        cur.execute("""
            SELECT test_id FROM versions_have_tests
            WHERE version_id=%s AND test_id=%s
            """, (data['version'][0], data['test-id'][0])
            )

        result = cur.fetchone()

        if subcommand == 'link' and result:
            msg = (
                "Test {0} already linked to Assignment {1}, Version {2}."
                " Cannot relink."
                .format(
                    data['test-id'][0],
                    data['assignment-id'][0],
                    data['version'][0]
                    )
                )
            self.logger.debug(msg)
            self.logger.debug("Aborting...")
            self.send_error(
                HTTPStatus.FORBIDDEN,
                msg
                )
            self.end_headers()
            return None

        elif subcommand == 'unlink' and not result:
            msg = (
                "Test {0} is not linked to Assignment {1}, Version {2}."
                " Cannot unlink."
                .format(
                    data['test-id'][0],
                    data['assignment-id'][0],
                    data['version'][0]
                    )
                )
            self.logger.debug(msg)
            self.logger.debug("Aborting...")
            self.send_error(
                HTTPStatus.FORBIDDEN,
                msg
                )
            self.end_headers()
            return None


        # check to see if any submissions have be recieved for current version
        cur.execute("""
            SELECT submissions.submission_id FROM submissions
            WHERE submissions.version_id=%s
            """, (data['version'][0],)
            )

        # if submissions are found, we need a new version
        if cur.fetchone():

            self.logger.debug(
                "Current version has submissions. Creating new version."
                )

            # create new version of assignment
            cur.execute("""
                INSERT INTO versions (assignment_id)
                VALUES (%s)
                RETURNING version_id
                """, (data['assignment-id'][0],)
                )

            if type(data['version']) is type([]):
                data['old-version'] = data['version']
            else:
                data['old-version'] = [data['version']]

            data['version'] = [cur.fetchone()['version_id']]

            self.logger.debug(
                "Old Version: {0}, New Version: {1}"
                .format(
                    data['old-version'],
                    data['version']
                    )
                )

            # copy all tests into new version
            cur.execute("""
                INSERT INTO versions_have_tests (version_id, test_id)
                SELECT %s, versions_have_tests.test_id
                FROM versions_have_tests
                WHERE versions_have_tests.version_id=%s
                """, (data['version'][0], data['old-version'][0])
                )
        else:
            self.logger.debug(
                "Current version has no submissions. Updating current version."
                )

        self.logger.debug("Data: {0}".format(data))
        self.logger.debug(
            "Command: {0}, Subcommand: {1}"
            .format(
                command,
                subcommand
                )
            )

        # link test
        if subcommand == 'link':

            cur.execute("""
                INSERT INTO versions_have_tests (version_id, test_id)
                VALUES (%s, %s)
                """, (data['version'][0], data['test-id'][0])
                )

        # unlink test
        elif subcommand == 'unlink':

            cur.execute("""
                DELETE FROM versions_have_tests
                WHERE version_id=%s AND test_id=%s
                """, (data['version'][0], int(data['test-id'][0]))
                )

        data.pop('old-version', None)
        return data


    def get_path(self, id, filename, uid, aid=None):
        """ Build commonly used paths.

        A small set of paths are used regulary with different
        arguments. This helper function formats, normalizes and
        returns this path set. The directories for said paths are
        also created if they do not yet exist.

        delpath: delete path, location of file to be deleted

        fpath: file path, location where test file is stored

        temppath: temporary path, location where user submitted
            files are stored until moved to final locations.

        subpath: submission path, the location where assignment
            submissions are stored.

        """

        subpath = None
        delpath = config['Directories']['testdir'].format(
            test_id=id
            )
        fpath = config['Directories']['testdir'].format(
            test_id=id
            )
        temppath = config['Directories']['tempdir'].format(
            user_id=uid
            )

        if aid:
            subpath = config['Directories']['subdir'].format(
                assignment_id=aid,
                submission_id=id
            )

        paths = [delpath, fpath, temppath, subpath]
        path_names = ["delpath", "fpath", "temppath", "subpath"]

        for num, path in enumerate(paths):
            if path:
                paths[num] = os.path.normpath(path)
                res = os.makedirs(path, exist_ok=True)
                self.logger.debug(
                    "Creating {0}: {1}, Result: {2}"
                    .format(path_names[num], path, res)
                    )

        delpath, fpath, temppath, subpath = paths

        fpath = os.path.join(fpath, filename)
        temppath = os.path.join(temppath, filename)
        if subpath:
            subpath = os.path.join(subpath, filename)

        self.logger.debug("delpath: {0}".format(delpath))
        self.logger.debug("fpath: {0}".format(fpath))
        self.logger.debug("temppath: {0}".format(temppath))
        self.logger.debug("subpath: {0}".format(subpath))

        if subpath:
            return delpath, subpath, temppath
        else:
            return delpath, fpath, temppath


    def uid_access_check(self, command, subcommand, auth_level, data):
        """ Check uid against command/subcommand.

        Users should only be able to view/update/delete data
        connected to them. For example a student should only
        see courses they are enrolled in and a teacher should only
        be able to delete their own courses.

        Returns True on success and None on failure."""

        # create cursor for querying db
        cur = conn.cursor()

        assignment_query = """
            SELECT *
            FROM assignments
            INNER JOIN teachers_teach_courses
                ON assignments.course_id=teachers_teach_courses.course_id
            WHERE
                teachers_teach_courses.teacher_id=%(uid)s
                AND
                assignments.assignment_id=%(assignment_id)s
            """

        ce_query = """
            SELECT *
            FROM common_errors
            WHERE teacher_id=%(uid)s AND ce_id=%(ce_id)s
            """

        course_query = """
            SELECT *
            FROM teachers_teach_courses
            WHERE
                teacher_id=%(uid)s
                AND
                course_id=%(course_id)s
            """

        ta_assists_query = """
            SELECT *
            FROM tas_assist_in_courses
            WHERE
                course_id=%(course_id)s
                AND
                ta_id=%(ta_id)s
            """

        name_to_uid_query = """
            SELECT users.user_id
            FROM users
            WHERE users.username=%(name)s
            """

        student_in_course_query = """
            SELECT *
            FROM students_take_courses
            WHERE
                student_id=%(student_id)s
                AND
                course_id=%(course_id)s
            """

        submission_query_ta = """
            SELECT *
            FROM submissions
            INNER JOIN versions
                ON submissions.version_id=versions.version_id
            INNER JOIN assignments
                ON versions.assignment_id=assignments.assignment_id
            INNER JOIN tas_assist_in_courses
                ON assignments.course_id=tas_assist_in_courses.course_id
            WHERE
                tas_assist_in_courses.ta_id=%(uid)s
                AND
                submissions.submission_id=%(submission)s
            """

        submission_query_teacher = """
            SELECT *
            FROM submissions
            INNER JOIN versions
                ON submissions.version_id=versions.version_id
            INNER JOIN assignments
                ON versions.assignment_id=assignments.assignment_id
            INNER JOIN teachers_teach_courses
                ON assignments.course_id=teachers_teach_courses.course_id
            WHERE
                teachers_teach_courses.teacher_id=%(uid)s
                AND
                submissions.submission_id=%(submission)s
            """

        submission_query_student = """
            SELECT assignments.course_id
            FROM assignments
            INNER JOIN students_take_courses
                ON assignments.course_id=students_take_courses.course_id
            WHERE
                students_take_courses.student_id=%(uid)s
                AND
                assignments.assignment_id=%(assignment_id)s
            """

        test_query = """
            SELECT * FROM tests
            WHERE teacher_id=%(uid)s AND test_id=%(test_id)s
            """





        if subcommand == "link" or subcommand == "unlink":

            if command == "test":

                # check for ownership of test and assignment
                cur.execute(
                    assignment_query,
                    {'uid':self.uid, 'assignment_id': data['assignment-id'][0]}
                    )
                assignment_id_result = cur.fetchone()


                cur.execute(
                    test_query,
                    {'uid': self.uid, 'test_id': data['test-id'][0]}
                    )
                test_id_result = cur.fetchone()

                self.logger.debug(
                    "Assignment check: {}, Test check: {}"
                    .format(
                        bool(assignment_id_result),
                        bool(test_id_result)
                        )
                    )
                if assignment_id_result is None or test_id_result is None:
                    if assignment_id_result is None and test_id_result is None:
                        msg = (
                            "Neither AssignmentID {} or TestID {} are owned by "
                            "TeacherID: {}"
                            .format(
                                data['assignment-id'][0],
                                data['test-id'][0],
                                self.uid
                                )
                            )
                    elif assignment_id_result is None:
                        msg = (
                            "AssignmentID {} is not owned by TeacherID {}"
                            .format(
                                data['assignment-id'][0],
                                self.uid
                                )
                            )
                    elif test_id_result is None:
                        msg = (
                            "TestID {} is not owned by TeacherID {}"
                            .format(
                                data['test-id'][0],
                                self.uid
                                )
                            )
                    self.logger.info(msg)
                    self.abort_response(HTTPStatus.FORBIDDEN, msg)
                    return None


        if subcommand == 'add':

            if command == 'assignment':

                if auth_level == 'teacher':
                    # check for ownership of course
                    cur.execute(
                        course_query,
                        {'uid':self.uid, 'course_id': data['course-id'][0]}
                        )
                    course_id_result = cur.fetchone()

                    if course_id_result is None:
                        msg = (
                            "CourseID {} is not owned by TeacherID {}"
                            .format(
                                data['course-id'][0],
                                self.uid
                                )
                            )
                        self.logger.info(msg)
                        self.abort_response(HTTPStatus.FORBIDDEN, msg)
                        return None


            elif command == 'ce':
                pass


            elif command == 'course':
                pass

            elif command == 'group':

                # get student and ta user ids
                cur.execute(name_to_uid_query, {'name': data['student'][0]})
                student_id = cur.fetchone()['user_id']

                cur.execute(name_to_uid_query, {'name': data['ta'][0]})
                ta_id = cur.fetchone()['user_id']

                if auth_level == 'teacher':
                    # check for ownership of course
                    cur.execute(
                        course_query,
                        {'uid': self.uid, 'course_id': data['course-id'][0]}
                        )
                    course_id_result = cur.fetchone()

                    # check for student in course
                    cur.execute(
                        student_in_course_query,
                        {'student_id': student_id, 'course_id': data['course-id'][0]}
                        )
                    student_in_course_result = cur.fetchone()

                    # check for ta assisting in course
                    cur.execute(
                        ta_assists_query,
                        {'course_id': data['course-id'][0], 'ta_id': ta_id}
                        )
                    ta_assists_result = cur.fetchone()

                    if course_id_result is None:
                        msg = (
                            "CourseID {} is not owned by TeacherID {}"
                            .format(
                                data['course-id'][0],
                                self.uid
                                )
                            )
                        self.logger.info(msg)
                        self.abort_response(HTTPStatus.FORBIDDEN, msg)
                        return None

                    if student_in_course_result is None:
                        msg = (
                            "StudentID {} is not in CourseID {}"
                            .format(
                                student_id,
                                data['course-id'][0]
                                )
                            )
                        self.logger.info(msg)
                        self.abort_response(HTTPStatus.FORBIDDEN, msg)
                        return None

                    if ta_assists_result is None:
                        msg = (
                            "TA {} is not assigned to CourseID {}"
                            .format(
                                ta_id,
                                data['course-id'][0]
                                )
                            )
                        self.logger.info(msg)
                        self.abort_response(HTTPStatus.FORBIDDEN, msg)
                        return None


            elif command == 'student':

                if auth_level == 'teacher':
                    # check for ownership of course
                    cur.execute(
                        course_query,
                        {'uid':self.uid, 'course_id': data['course-id'][0]}
                        )
                    course_id_result = cur.fetchone()

                    if course_id_result is None:
                        msg = (
                            "CourseID {} is not owned by TeacherID {}"
                            .format(
                                data['course-id'][0],
                                self.uid
                                )
                            )
                        self.logger.info(msg)
                        self.abort_response(HTTPStatus.FORBIDDEN, msg)
                        return None


            elif command == 'submission':

                # get course id
                cur.execute("""
                    SELECT course_id
                    FROM assignments
                    WHERE assignment_id=%s
                    """, (data['assignment-id'][0],)
                    )
                course_id = cur.fetchone()
                if course_id is not None:
                    course_id = course_id['course_id']

                # check for student in course
                cur.execute(
                    submission_query_student,
                    {'uid': self.uid, 'assignment_id': data['assignment-id'][0], 'course_id': course_id}
                    )
                student_assignment_result = cur.fetchone()

                if student_assignment_result is None:
                    msg = (
                        "StudentID {} is not in CourseID {} and can not submit to AssignmentID {}"
                        .format(
                            self.uid,
                            course_id,
                            data['assignment-id'][0]
                            )
                        )
                    self.logger.info(msg)
                    self.abort_response(HTTPStatus.FORBIDDEN, msg)
                    return None


            elif command == 'ta' and 'course-id' in data:

                if auth_level == 'teacher':
                    # check for ownership of course
                    cur.execute(
                        course_query,
                        {'uid':self.uid, 'course_id': data['course-id'][0]}
                        )
                    course_id_result = cur.fetchone()

                    if course_id_result is None:
                        msg = (
                            "CourseID {} is not owned by TeacherID {}"
                            .format(
                                data['course-id'][0],
                                self.uid
                                )
                            )
                        self.logger.info(msg)
                        self.abort_response(HTTPStatus.FORBIDDEN, msg)
                        return None


            elif command == 'tag':
                # TODO - Test this once adding tags is implemented
                if auth_level == 'teacher':
                    # check for ownership of course for assignment to be tagged
                    cur.execute(
                        assignment_query,
                        {'uid':self.uid, 'course_id': data['assignment-id'][0]}
                        )
                    assignment_id_result = cur.fetchone()

                    if assignment_id_result is None:
                        msg = (
                            "AssignmentID {} is not owned by TeacherID {}"
                            .format(
                                data['assignment-id'][0],
                                self.uid
                                )
                            )
                        self.logger.info(msg)
                        self.abort_response(HTTPStatus.FORBIDDEN, msg)
                        return None


            elif command == 'test':
                pass


        if subcommand == 'update' or subcommand == 'delete':

            if command == 'assignment':

                # check for ownership of assignment
                cur.execute(
                    assignment_query,
                    {'uid':self.uid, 'assignment_id': data['assignment-id'][0]}
                    )
                assignment_id_result = cur.fetchone()

                if assignment_id_result is None:
                    msg = (
                        "AssignmentID {} is not owned by TeacherID {}"
                        .format(
                            data['assignment-id'][0],
                            self.uid
                            )
                        )
                    self.logger.info(msg)
                    self.abort_response(HTTPStatus.FORBIDDEN, msg)
                    return None


            elif command == 'ce':

                # check for ownership of common_error
                cur.execute(
                    ce_query,
                    {'uid':self.uid, 'ce_id': data['ce-id'][0]}
                    )
                ce_id_result = cur.fetchone()

                if ce_id_result is None:
                    msg = (
                        "CommonErrorID {} is not owned by TeacherID {}"
                        .format(
                            data['ce-id'][0],
                            self.uid
                            )
                        )
                    self.logger.info(msg)
                    self.abort_response(HTTPStatus.FORBIDDEN, msg)
                    return None

            elif command == 'course':

                # check for ownership of course
                cur.execute(
                    course_query,
                    {'uid':self.uid, 'course_id': data['course-id'][0]}
                    )
                course_id_result = cur.fetchone()

                if course_id_result is None:
                    msg = (
                        "CourseID {} is not owned by TeacherID {}"
                        .format(
                            data['course-id'][0],
                            self.uid
                            )
                        )
                    self.logger.info(msg)
                    self.abort_response(HTTPStatus.FORBIDDEN, msg)
                    return None


            elif command == 'group':

                if auth_level == 'teacher':
                    # check for ownership of course
                    cur.execute(
                        course_query,
                        {'uid':self.uid, 'course_id': data['course-id'][0]}
                        )
                    course_id_result = cur.fetchone()

                    if course_id_result is None:
                        msg = (
                            "CourseID {} is not owned by TeacherID {}"
                            .format(
                                data['course-id'][0],
                                self.uid
                                )
                            )
                        self.logger.info(msg)
                        self.abort_response(HTTPStatus.FORBIDDEN, msg)
                        return None


            elif command == 'grade' or command == 'submission':

                sub_id = None
                if 'assignment-id' in data:
                    # get student id from onid
                    cur.execute("""
                        SELECT users.user_id FROM users
                        INNER JOIN students
                        ON users.user_id=students.student_id
                        WHERE users.username=%s
                        """, (data['student'][0],)
                        )
                    student_id = cur.fetchone()['user_id']
                    # use assignment-id and student-id to select
                    # correct submission-id


                    cur.execute("""
                        SELECT MAX(S.submission_id)
                        FROM submissions AS S
                        INNER JOIN students_create_submissions AS C
                        ON S.submission_id=C.submission_id
                        INNER JOIN versions AS V
                        ON S.version_id=V.version_id
                        WHERE
                            V.assignment_id=%s
                            AND C.student_id=%s
                        """, (data['assignment-id'][0], student_id,)
                        )
                    sub_id = []
                    sub_id.append(cur.fetchone()['max'])
                    sub_id = sub_id[0]


                if sub_id is None:
                    sub_id = data['submission'][0]

                if auth_level == 'ta':
                    query = submission_query_ta
                    msg = (
                            "TA {} is not assisting SubmissionID {}'s course"
                            .format(
                                self.uid,
                                sub_id
                                )
                            )
                elif auth_level == 'teacher':
                    query = submission_query_teacher
                    msg = (
                            "TeacherID {} is not an instructor SubmissionID {}'s course"
                            .format(
                                self.uid,
                                sub_id
                                )
                            )

                # check that TA/teacher is assisting/teaching in the course that owns
                # the assignment that owns the submission
                cur.execute(
                    query,
                    {'uid':self.uid, 'submission': sub_id}
                    )
                submission_id_result = cur.fetchone()

                if submission_id_result is None:
                    self.logger.info(msg)
                    self.abort_response(HTTPStatus.FORBIDDEN, msg)
                    return None


            elif command == 'student':

                if auth_level == 'teacher':
                    # check for ownership of course
                    cur.execute(
                        course_query,
                        {'uid':self.uid, 'course_id': data['course-id'][0]}
                        )
                    course_id_result = cur.fetchone()

                    if course_id_result is None:
                        msg = (
                            "CourseID {} is not owned by TeacherID {}"
                            .format(
                                data['course-id'][0],
                                self.uid
                                )
                            )
                        self.logger.info(msg)
                        self.abort_response(HTTPStatus.FORBIDDEN, msg)
                        return None

            elif command == 'ta' and 'course-id' in data:

                if auth_level == 'teacher':
                    # check for ownership of course
                    cur.execute(
                        course_query,
                        {'uid':self.uid, 'course_id': data['course-id'][0]}
                        )
                    course_id_result = cur.fetchone()

                    if course_id_result is None:
                        msg = (
                            "CourseID {} is not owned by TeacherID {}"
                            .format(
                                data['course-id'][0],
                                self.uid
                                )
                            )
                        self.logger.info(msg)
                        self.abort_response(HTTPStatus.FORBIDDEN, msg)
                        return None

            elif command == 'tag':

                if auth_level == 'teacher':
                    # check for ownership of assignment
                    cur.execute(
                        assignment_query,
                        {'uid':self.uid, 'assignment_id': data['assignment-id'][0]}
                        )
                    assignment_id_result = cur.fetchone()

                    if assignment_id_result is None:
                        msg = (
                            "AssignmentID {} is not owned by TeacherID {}"
                            .format(
                                data['assignment-id'][0],
                                self.uid
                                )
                            )
                        self.logger.info(msg)
                        self.abort_response(HTTPStatus.FORBIDDEN, msg)
                        return None


            elif command == 'test':

                # check that Teacher owns test
                cur.execute(
                    test_query,
                    {'uid': self.uid, 'test_id': data['test-id'][0]}
                    )
                test_id_result = cur.fetchone()

                if test_id_result is None:
                    msg = (
                        "TestID {} is not owned by TeacherID {}"
                        .format(
                            data['test-id'][0],
                            self.uid
                            )
                        )
                    self.logger.info(msg)
                    self.abort_response(HTTPStatus.FORBIDDEN, msg)
                    return None


        self.logger.debug(
            "UID {} passed uid_auth_check for {}/{}"
            .format(
                self.uid,
                command,
                subcommand
                )
            )
        return True

    def abort_response(self, http_error, msg):
        self.logger.info("Aborting...")
        self.send_error(
            http_error,
            msg
            )
        self.end_headers()
        return



class ThreadingHTTPServer(ThreadingMixIn, http.server.HTTPServer):
    def __init__(self,server_address,HandlerClass,q):
        super(ThreadingHTTPServer, self).__init__(server_address,HandlerClass)
        self.q = q

# http.server.test is an internal http.server function
# https://hg.python.org/cpython/file/3.4/Lib/http/server.py
def test(
    HandlerClass=http.server.BaseHTTPRequestHandler,
    ServerClass=http.server.HTTPServer,
    protocol="HTTP/1.0",
    port=443,
    bind=""
    ):
    """Test the HTTP request handler class.

    This runs an HTTP server on port 443 (or the port argument).

    """
    server_address = (bind, port)
    # conf option later!
    cvars = "dbname=postgres user=postgres password=killerkat5"
    testerCount = 4
    #herald_init returns a q
    q = rest_extend.herald_init(testerCount)
    HandlerClass.protocol_version = protocol
    httpd = ServerClass(server_address, HandlerClass,q)

    tthread = []
    for i in range(testerCount):
        tthread.append(rest_extend.testerThread(i,q,cvars))
        tthread[i].daemon = True
        tthread[i].start()
    # add ssl
    httpd.socket = ssl.wrap_socket(
        httpd.socket,
        keyfile  = os.path.normpath(
            'domains/vm-cs-cap-g15.eecs.oregonstate.edu.key'
            ),
        certfile = os.path.normpath(
            'domains/vm-cs-cap-g15.eecs.oregonstate.edu.cert'
            ),
        server_side=True
        )

    sa = httpd.socket.getsockname()
    print("Serving HTTPS on", sa[0], "port", sa[1], "...")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nKeyboard interrupt received, exiting.")
        httpd.server_close()
        exit(0)

def custom_init():

    global config
    config = configparser.ConfigParser()
    config.read('general.cfg')

    # Connect to an existing database
    global db_conn
    db_conn = (
        "dbname={dbname} "
        "user={user} "
        "password={password}"
        .format(
            dbname   = config['Database']['dbname'],
            user     = config['Database']['user'],
            password = config['Database']['password']
            )
        )

    global conn
    conn = psycopg2.connect(
        db_conn,
        cursor_factory = psycopg2.extras.RealDictCursor
        )
    conn.autocommit = True

    global logLevel
    logLevel = logging.WARNING


    # ensure that file directory exists
    os.makedirs(os.path.normpath(config['Directories']['basedir']), exist_ok=True)


if __name__ == '__main__':

    custom_init()

    handler = RESTfulHandler

    parser = argparse.ArgumentParser()

    parser.add_argument("-v", "--verbosity", action="count",
                    help="Specify output verbosity")
    parser.add_argument('--bind', '-b', default='', metavar='ADDRESS',
                        help='Specify alternate bind address '
                             '[default: all interfaces]')
    parser.add_argument('port', action='store',
                        default=443, type=int,
                        nargs='?',
                        help='Specify alternate port [default: 443]')
    args = parser.parse_args()

    if args.verbosity:
        if args.verbosity>2:
            print("-vv is maximum verbosity")
            print("setting verbosity to -vv")
            logLevel = logging.DEBUG
        elif args.verbosity==2:
            logLevel = logging.DEBUG
        elif args.verbosity==1:
            logLevel = logging.INFO



    test(
        HandlerClass=handler,
        ServerClass=ThreadingHTTPServer,
        port=args.port,
        bind=args.bind
        )