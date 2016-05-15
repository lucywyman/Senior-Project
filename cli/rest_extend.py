import threading
import queue
import socket
import select
import sys
import subprocess
import signal
import time
import json
import shutil
import stat
import string
import os
import psycopg2
import psycopg2.extras
import configparser
from pwd import getpwnam

# class for tester threads
class testerThread (threading.Thread):
    def __init__(self,ID,q,cvars):
        threading.Thread.__init__(self)
        self.ID = ID
        self.username = 'tester'+str(ID)+'user'
        self.q = q
        #change this to use cvars read from config
        self.cvars = cvars
        self.conn = psycopg2.connect(cvars, cursor_factory= psycopg2.extras.RealDictCursor)
        self.conn.autocommit = True
        print('Tester ' + str(ID) + ' running!')

    def query(self,id):
        # create cursor for querying db
        cur = self.conn.cursor()

        cur.execute("""
            SELECT
                tests.test_id, tests.name, tests.time_limit,
                submissions.submission_id, versions_have_tests.version_id,
                versions.assignment_id
            FROM tests
            INNER JOIN versions_have_tests
            ON versions_have_tests.test_id=tests.test_id
            INNER JOIN submissions
            ON submissions.version_id=versions_have_tests.version_id
            INNER JOIN versions
            ON versions.version_id=submissions.version_id
            WHERE submission_id=%s
            """, (id,)
            )

        tests = cur.fetchall()

        cur.close()

        #Path database stores the submission at
        subpath = os.path.normpath(
            config['Directories']['subdir'].format(
                assignment_id=tests[0]['assignment_id'],
                submission_id=tests[0]['submission_id']
                )
            )
        for test in tests:
            testpath = os.path.normpath(
                config['Directories']['testdir']
                .format(test_id=int(test['test_id']))
                )

            # why was this 'with os.listdir(testpath)[0] as file:'?
            # with is for opening files
            # here we are working with a list of files from a directory
            for file in os.listdir(testpath):
                test['testFile'] = os.path.normpath(os.path.join(testpath, file))
                # right now we only support one file per test or submission,
                # so we break after the first iteration of the loop
                # written in loop form because eventually we would like tobytes
                # support multiple files
                break;
            for file in os.listdir(subpath):
                test['subFile'] = os.path.normpath(os.path.join(subpath, file))
                break;

        print(tests)

        return tests

    #function to execute test
    def runProtected(self,files,sub_ID):

        print("{} running {}".format(self.username, files))
        # obsolete since plan is to store in db now?
        # resultpath = os.path.normpath(
            # config['Directories']['resultdir'].format(
                # assignment_id=files['assignment_id'],
                # submission_id=files['submission_id']
                # )
            # )

        # if not os.path.exists(resultpath):
            # os.makedirs(resultpath)
            
        userpath = os.path.normpath(
            config['Directories']['userdir'].format(
                username=self.username
                )
            )

        if not os.path.exists(userpath):
            os.makedirs(userpath)

        print('subfile: {0}, {1}'.format(files['subFile'],userpath))
        shutil.copy(files['subFile'],userpath)
        shutil.copy(files['testFile'],userpath)
        shutil.copy(
            os.path.normpath(os.path.join(
                config['Directories']['srcdir'],
                'interfaces/py_test_osu.py'
                )
            ),
            userpath
        )
        

        uid = getpwnam(self.username)[2]
        
        os.chmod(
            os.path.join(
                userpath,
                os.path.split(files['subFile'])[-1]
                ),
            0o0777
            )
        os.chmod(
            os.path.join(
                userpath,
                os.path.split(files['testFile'])[-1]
                ),
            0o0777
            )    
        os.chmod(
            os.path.join(
                userpath,
                './py_test_osu.py'
                ),
            0o0777
            )
        # TODO change from submission id to test-id. Output already in specific submission folder
        # test id more useful
        # [
                    # os.path.normpath(os.path.join(userpath, 'test.py')),
                    # self.cvars,
                    # str(files['submission_id']),
                    # str(files['test_id'])
                # ],
                
        exec_string = "{0} {1} {2} {3}".format(
            os.path.normpath(os.path.join(userpath, 'test.py')),
            self.cvars,
            str(files['submission_id']),
            str(files['test_id'])
            )
        try:
            print("running process")
            result = subprocess.check_output(
                exec_string,
                preexec_fn = lambda: os.setuid(uid),
                timeout=5,
                shell=True
                )
            # changed error to retcode. is that right?
            retcode = 0
        except subprocess.CalledProcessError as e:
            result = e.output
            retcode = e.returncode
        
        os.unlink(
            os.path.join(
                userpath,
                os.path.split(files['subFile'])[-1]
                )
            )
        os.unlink(
            os.path.join(
                userpath,
                os.path.split(files['testFile'])[-1]
                )
            )
        os.unlink(
            os.path.join(
                userpath,
                './py_test_osu.py'
                )
            )

        print("returning from runProtected")
        return result, retcode

    def run(self):
        while 1:
            sub_ID = self.q.get()
            print("task started")
            files = self.query(sub_ID)
            for row in files:
                result,retcode = self.runProtected(row,sub_ID)
                if(retcode!=0):
                    cur = self.conn.cursor()
                    cur.execute("""
                        INSERT INTO submissions_have_results (submission_id, test_id, results)
                        VALUES (%s, %s, %s)
                        """, (row['submission_id'], row['test_id'], '{{"TAP":"","Tests":[],"Errors":[{0},{1}],"Grade":"-1"}}'.format(retcode, result))
                        )
                    cur.close()
                    
                else:
                    print(result)

            print("task done")
            self.q.task_done()

# functions for herald
# Init returns the FIFO queue; the python Queue object is threadsafe!

def change_user(username):

    from pwd import getpwnam

    print("Username is: {}".format(username))
    uid = getpwnam(username)[2]
    gid = getpwnam(username)[3]
    print(uid,gid)

    def set_ids():
    
        uid = getpwnam(username)[2]
        gid = getpwnam(username)[3]
        
        os.setuid(uid)
        os.setgid(gid)

    print("returning preexec_fn")
    return set_ids


def herald_init(testers):

    global config
    config = configparser.ConfigParser()
    config.read('general.cfg')

    q = queue.Queue()
    for i in range(testers):
        subprocess.call(["userdel","-rf","tester"+str(i)+"user"])
        subprocess.check_call(["useradd","-p","pass"+str(i),"tester"+str(i)+"user"])
    return q

def herald(q,sub_ID):
    # should we timeout here, and use a maxsize?
    q.put(sub_ID)
