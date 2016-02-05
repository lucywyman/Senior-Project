#!/usr/bin/env python3

# AUTO command line interface
# Created by Nathan Hennig, Lucy Wyman, Andrew Gass
# Oregon State University - Senior Design Project
# 2/4/16
# Resourses:
#   http://stackoverflow.com/questions/9973990/python-cmd-dynamic-docstrings-for-do-help-function
#   http://stackoverflow.com/questions/16826172/filename-tab-completion-in-cmd-cmd-of-python

import cmd, glob, os, requests, sys


# for testing
import logging


# Enabling debugging at http.client level (requests->urllib3->http.client)
# you will see the REQUEST, including HEADERS and DATA, and RESPONSE with HEADERS but without DATA.
# the only thing missing will be the response.body which is not logged.
try: # for Python 3
    from http.client import HTTPConnection
except ImportError:
    from httplib import HTTPConnection
HTTPConnection.debuglevel = 1

logging.basicConfig() # you need to initialize logging, otherwise you will not see anything from requests
logging.getLogger().setLevel(logging.DEBUG)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True









def _append_slash_if_dir(p):
    if p and os.path.isdir(p) and p[-1] != os.sep:
        return p + os.sep
    else:
        return p

# This table is part of decorator to map appropriate
# docstrings (for help) to functions
ttable = {
    "student" : {
        "course view": "course view [<key>=<value>]...\n\tlist all courses being taken"
    },
    "teacher" : {
        "course view": "course view [<key>=<value>]...\n\tlist all courses being taught"
    }
}

def document(user_type=None):
    def doc_decorator(function):
        if user_type and user_type in ttable:
            function.__doc__ = ttable[user_type][function.__doc__]
        return function
    return doc_decorator



class AutoShell(cmd.Cmd):

    # TODO Call server to identify user as student, ta,
    # or teacher.
    user = "student"
    server = "http://127.0.0.1:8000/"

    intro = 'Welcome to the AUTO Universal Testing Organizer (AUTO) shell.\n   Type help or ? to list commands'
    prompt = '>> '


    # TODO make is so this doesn't appear in undoc commands (change header variable?)
    def do_EOF(self, args):
        print("Thanks for using AUTO!\n")
        return True

    def do_course(self, args):
        'Add, View, Update, Delete Courses'
        print("Not implemented")

    def do_assignment(self, args):
        'Add, View, Update, Delete Assignments'
        print("Not implemented")

    def do_tag(self, args):
        'Tag assignments with keywords'
        print("Not implemented")

    def do_test(self, args):
        'Add, View, Update, Delete Tests'
        print("Not implemented")

    def do_students(self, args):
        'Add, View, Delete Students'
        print("Not implemented")

    def do_ta(self, args):
        'Add, View, Delete TAs'
        print("Not implemented")

    def do_group(self, args):
        'Add, View, Delete groups'
        print("Not implemented")

    def do_submission(self, args):
        'Add, View, Update Submissions'
        args = args.split()
        if args[0]=="add":
            try:
                int(args[1])
            except ValueError:
                print("Error: assignment-id must be an integer value.")
                return
            url = self.server + 'submission/'
            data = { "assignment-id": args[1] }
            files = { "file": open(args[2]) }
            r = requests.post(url, files=files, data=data)
            
            # TODO more robust error reporting
            if r.status_code==200:
                print("Submission succeeded!")
            else:
                print("Failed")

    def complete_submission(self, text, line, begidx, endidx):
        before_arg = line.rfind(" ", 0, begidx)
        if before_arg == -1:
            return # arg not found

        fixed = line[before_arg+1:begidx]  # fixed portion of the arg
        arg = line[before_arg+1:endidx]
        pattern = arg + '*'

        completions = []
        for path in glob.glob(pattern):
            path = _append_slash_if_dir(path)
            completions.append(path.replace(fixed, "", 1))
        return completions

    def do_grade(self, args):
        'Alias of submission update'
        print("Not implemented")

    def do_ce(self, args):
        'Add, View, Update, Delete Common Errors'
        print("Not implemented")


def parse(arg):
    'Convert a series of zero or more numbers to an argument tuple'
    return tuple(map(int, arg.split()))


if __name__ == '__main__':
    AutoShell().cmdloop()
