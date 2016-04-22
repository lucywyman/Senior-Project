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
                            basedir +
                            'submission/{0}/{1}/'
                            .format(
                                int(test['assignment_id']),
                                int(test['submission_id'])
                                )
                            )
        for test in tests:
            testpath = os.path.normpath(basedir + 'tests/{}'.format(int(test['test_id'])))
            
            with os.listdir(testpath) as file:
                test['testFile'] = os.path.normpath(testpath + '/' + file)#
                break;
            with os.listdir(subpath)[0] as file:
                test['subFile'] = os.path.normpath(subpath + '/' + file)
                break;
    
        print(tests)
    
        return tests

    #function to execute test
    def runProtected(self,files,sub_ID):
    
        resultpath = os.path.normpath(
                basedir +
                'submission/{0}/{1}/results'
                .format(
                    int(files['assignment_id']),
                    int(files['submission_id'])
                    )
                )
    
        if not os.path.exists(resultpath):
            os.makedirs(resultpath)
    
        if not os.path.exists(self.username):
            os.makedirs(self.username)
    
    
        shutil.copy(files['subFile'],os.path.normpath('./'+self.username+'/'))
        shutil.copy(files['testFile'],os.path.normpath('./'+self.username+'/'))
        shutil.copy(os.path.normpath('interfaces/py_test_osu.py'),os.path.normpath('./'+self.username+'/'))
        os.chdir(os.path.normpath('./'+self.username+'/'))
        os.chmod(os.path.split(files['subFile'])[-1],0o0777)
        os.chmod(os.path.split(files['testFile'])[-1],0o0777)
        os.chmod(os.path.normpath('./py_test_osu.py'),0o0777)
        # TODO change from submission id to test-id. Output already in specific submission folder
        # test id more useful
        try:
            result = subprocess.check_output(["su",self.username,"-c",os.path.normpath('./test.py'),self.cvars,files['submission_id'],files['test_id']],timeout=5,shell=True)
            error = 0
        except subprocess.CalledProcessError as e:
            result = e.output
            retcode = e.returncode   
        os.unlink(os.path.split(files['subFile'])[-1])
        os.unlink(os.path.split(files['testFile'])[-1])
        os.unlink('py_test_osu.py')
        os.chdir('..')
        return result, retcode
    
    def run(self):
        while 1:
            sub_ID = self.q.get()
            files = query(sub_ID)
            for row in files:
                result,retcode = runProtected(row,sub_ID)
                if(retcode!=0):
                    cur.execute("""
                        INSERT INTO submissions_have_results (submission_id, test_id, results)
                        VALUES (%s, %s, %s)
                        """, (row['submission_id'], row['test_id'], '{"TAP":"","Tests":[],"Errors":['+retcode+','+result+'],"Grade":"-1"}')
                        )
                    cur.close()
                self.q.task_done()
               
# functions for herald
# Init returns the FIFO queue; the python Queue object is threadsafe!
def herald_init(testers):
    q = queue.Queue()
    for i in range(testers):
        subprocess.call(["userdel","-rf","tester"+str(i)+"user"])
        subprocess.check_call(["useradd","-p","pass"+str(i),"tester"+str(i)+"user"])
    return q

def herald(q,sub_ID):
    # should we timeout here, and use a maxsize?
    q.put(sub_ID)