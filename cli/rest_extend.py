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
            test['testPath'] = testpath;
            test['subPath'] = subpath;
            # I've commented out these 13 lines because we now support
            # multiple files. It's been moved to the copy section of
            # runProtected
            ## why was this 'with os.listdir(testpath)[0] as file:'?
            ## with is for opening files
            ## here we are working with a list of files from a directory
            #for file in os.listdir(testpath):
            #    test['testFile'] = os.path.normpath(os.path.join(testpath, file))
            #    # right now we only support one file per test or submission,
            #    # so we break after the first iteration of the loop
            #    # written in loop form because eventually we would like tobytes
            #    # support multiple files
            #    break;
            #for file in os.listdir(subpath):
            #    test['subFile'] = os.path.normpath(os.path.join(subpath, file))
            #    break;

        print(tests)

        return tests

    # Helper function for runProtected.
    # Moves all the files in srcdir
    # to userpath, given them 777 perms.
    # Expected use is for test files,
    # submission files, interface files
    def copyPerm(self,srcdir,userpath):
        for file in os.listdir(srcdir):
            srcfile = os.path.normpath(os.path.join(srcdir,file))


            if os.path.isfile(srcfile):
                shutil.copy(srcfile,userpath)
                os.chmod(os.path.join(userpath,file),0o0777)
            else:
                print("Skipped: '{}'".format(srcfile))



    #function to execute test
    def runProtected(self,files,sub_ID):

        print("{} running {}".format(self.username, files))
        ##obsolete since plan is to store in db now?
        # back to using result path!
        resultpath = os.path.normpath(
            config['Directories']['resultdir'].format(
                assignment_id=files['assignment_id'],
                submission_id=files['submission_id']
                )
            )


        userpath = os.path.normpath(
            config['Directories']['userdir'].format(
                username=self.username
                )
            )

        uid = getpwnam(self.username)[2]
        gid = getpwnam(self.username)[3]

        if not os.path.exists(resultpath):
            os.makedirs(resultpath)
        os.chown(resultpath, uid, gid)

        if not os.path.exists(userpath):
            os.makedirs(userpath)
        os.chown(userpath, uid, gid)

        print('subdir: {0}, {1}'.format(files['subPath'],userpath))
        # Generate interface files path
        interfaceDir = os.path.normpath(os.path.join(config['Directories']['srcdir'],'interfaces'))
        # File moves and permissions
        self.copyPerm(files['subPath'],userpath)
        self.copyPerm(files['testPath'],userpath)
        self.copyPerm(interfaceDir,userpath)



        # TODO change from submission id to test-id. Output already in specific submission folder
        # test id more useful
        # [
                    # os.path.normpath(os.path.join(userpath, 'test.py')),
                    # self.cvars,
                    # str(files['submission_id']),
                    # str(files['test_id'])
                # ],
        #
        #exec_string = "{0} {1} {2} {3}".format(
        #    os.path.normpath(os.path.join(userpath, 'test.py')),
        #    self.cvars,
        #    str(files['submission_id']),
        #    str(files['test_id'])
        #    )

        # Get time limit
        time_limit = int(config['Tester']['run_time_limit'])

        cur = self.conn.cursor()
        cur.execute("""
            SELECT time_limit
            FROM tests
            WHERE test_id=%s
            """, (files['test_id'],)
            )

        test_time_limit = int(cur.fetchone().get("time_limit", 0))
        cur.close()

        if test_time_limit is not None and test_time_limit > 0:
            time_limit = int(test_time_limit)

        # another new exec_string! for make files
        exec_string = "make -C {0} runtest SUBID={1!s} TESTID={2!s} RESULTDIR={3!s} CPATH={4!s}".format(
            os.path.normpath(userpath),
            files['submission_id'],
            files['test_id'],
            resultpath,
            os.path.normpath(userpath)
            )
        print("Exec_string: '{}'".format(exec_string))

        # NOTE: calling setuid before setgid will result in an error if the new
        # uid lacks authority to change the gid
        def change_user():
            os.setgid(gid)
            os.setuid(uid)

        try:
            print("running process")
            result = subprocess.check_output(
                exec_string,
                preexec_fn = change_user,
                timeout = time_limit,
                shell = True
                )
            retcode = 0
        except subprocess.CalledProcessError as e:
            result = e.output
            retcode = e.returncode

        # clean up any remaining processes
        subprocess.call(["killall", "-KILL", "-u", self.username])

        # clean up temporary files
        for file in os.listdir(userpath):
            pfile = os.path.normpath(os.path.join(userpath,file))
            try:
                if os.path.isfile(pfile):
                    os.unlink(pfile)
                elif os.path.isdir(pfile): shutil.rmtree(pfile)
            except Exception as e:
                print(e)

        print("returning from runProtected")
        return result, retcode, resultpath

    def run(self):
        while 1:
            sub_ID = self.q.get()
            print("task started")
            files = self.query(sub_ID)
            for row in files:
                result,retcode,resultpath = self.runProtected(row,sub_ID)
                if(retcode!=0):
                    cur = self.conn.cursor()
                    cur.execute("""
                        INSERT INTO submissions_have_results (submission_id, test_id, results)
                        VALUES (%s, %s, %s)
                        """, (row['submission_id'], row['test_id'], '{{"TAP":"","Tests":[],"Errors":[{0},"{1}"],"Grade":"-1"}}'.format(retcode, result.decode('utf-8')))
                        )
                    cur.close()

                else:
                    print(result)
                    # first try opening the file
                    try:
                      resfile = open(os.path.normpath(os.path.join(resultpath,str(row['test_id']))),'r')
                      # then try parsing it
                      try:
                        jres = json.load(resfile)
                      # if parse fails, record
                      except Exception as e:
                        print(e)
                        jres = json.loads('{{"TAP":"","Tests":[],"Errors":[{0},{1},"Output JSON Corrupt"],"Grade":"-1"}}'.format(retcode, result))
                    # if opening fails, record it
                    except Exception as e:
                      print(e)
                      jres = json.loads('{{"TAP":"","Tests":[],"Errors":[{0},{1},"Output file could not be opened"],"Grade":"-1"}}'.format(retcode, result))
                    # whatever happened grabbing the output file, put the resulting json in the DB
                    cur = self.conn.cursor()
                    cur.execute("""
                        INSERT INTO submissions_have_results (submission_id, test_id, results)
                        VALUES (%s, %s, %s)
                        """, (row['submission_id'], row['test_id'], json.dumps(jres))
                        )
                    cur.close()

            print("task done")
            self.q.task_done()





# functions for herald
# Init returns the FIFO queue; the python Queue object is threadsafe!
def herald_init(testers):

    global config
    config = configparser.ConfigParser()
    config.read('general.cfg')

    q = queue.Queue()

    subprocess.call(["groupadd","testers"])
    for i in range(testers):
        subprocess.call(["userdel","-rf","tester"+str(i)+"user"])
        subprocess.check_call(["useradd","-p","pass"+str(i),"tester"+str(i)+"user","-g","testers"])
    return q

def herald(q,sub_ID):
    # should we timeout here, and use a maxsize?
    q.put(sub_ID)