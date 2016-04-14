#!/usr/local/bin/python3.4

import socket
import select
import sys
import subprocess
import time
import json
import shutil
import stat
import string
import os
import psycopg2
import psycopg2.extras

basedir = 'c:/Senior/cli/logs/'

# Connect to an existing database
conn = psycopg2.connect("dbname=postgres user=postgres password=killerkat5", cursor_factory= psycopg2.extras.RealDictCursor)
conn.autocommit = True

def query(id):

    # create cursor for querying db
    cur = conn.cursor()

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


    for test in tests:
        testpath = os.path.normpath( basedir + 'tests/{}'.format(int(test['test_id'])))
        subpath = os.path.normpath(
            basedir +
            'submission/{0}/{1}/'
            .format(
                int(test['assignment_id']),
                int(test['submission_id'])
                )
            )
        for file in os.listdir(testpath):
            test['testFile'] = os.path.normpath(testpath + '/' + file)
            break;
        for file in os.listdir(subpath):
            test['subFile'] = os.path.normpath(subpath + '/' + file)
            break;

    print(tests)

    return tests

def runProtected(files,sub_ID):

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

    if not os.path.exists('tester0User'):
        os.makedirs('tester0User')


    shutil.copy(files['subFile'],os.path.normpath('./tester0User/'))
    shutil.copy(files['testFile'],os.path.normpath('./tester0User/'))
    shutil.copy(os.path.normpath('interfaces/py_test_osu.py'),os.path.normpath('./tester0User/'))
    os.chdir(os.path.normpath('./tester0User/'))
    os.chmod(os.path.split(files['subFile'])[-1],0o0777)
    os.chmod(os.path.split(files['testFile'])[-1],0o0777)
    os.chmod(os.path.normpath('./py_test_osu.py'),0o0777)
    # TODO change from submission id to test-id. Output alreadying in specific submission folder
    # test id more useful
    subprocess.call(os.path.normpath('./test.py'),stdout=open('tapresult - ' + str(sub_ID) + '.txt','w'),shell=True)
    shutil.copy('tapresult - ' + str(sub_ID) + '.txt',os.path.normpath(resultpath))
    os.unlink(os.path.split(files['subFile'])[-1])
    os.unlink(os.path.split(files['testFile'])[-1])
    os.unlink('py_test_osu.py')
    os.unlink('tapresult - ' + str(sub_ID) + '.txt')
    os.chdir('..')

id = sys.argv[1]
c = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
k = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
r = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
#c.bind("\0recvPort" + id)
c.bind(('127.0.0.1', 6000 + int(id)))
print("Bound listen port {0}".format(6000 + int(id)))
#k.bind("\0killPort" + id)
k.bind(('127.0.0.1', 7000 + int(id)))
c.listen(1)
k.listen(1)
while 1:
    readlist,writelist,exceptlist = select.select([c,k],[],[])
    for avail in readlist:
        #test branch
        if avail is c:
            h = c.accept()[0]
            msg = h.recv(256)
            h.close()
            dmsg = msg.decode()
            print(dmsg)
            sub_ID = json.loads(dmsg)["sub_ID"]
            files = query(sub_ID)
            for row in files:
                try:
                    runProtected(row,sub_ID)
                except Exception as e:
                    print(e)
                    raise
                else:
                    o = socket.socket(socket.AF_INET,socket.SOCK_STREAM);
                    o.connect(('127.0.0.1', 9002))      #'\0rePort')
                    o.send(msg)
                    o.close()
        #kill branch
        elif avail is k:
            print("Tester" + id + " recieved kill signal")
            remv = k.accept()[0]
            k.close()
            exit()


