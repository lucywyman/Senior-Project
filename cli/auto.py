#!/usr/bin/env python3

# AUTO command line interface
# Created by Nathan Hennig, Lucy Wyman, Andrew Gass
# Oregon State University - Senior Design Project
# 2/4/16
# Resourses:
#   http://stackoverflow.com/questions/9973990/python-cmd-dynamic-docstrings-for-do-help-function
#   http://stackoverflow.com/questions/16826172/filename-tab-completion-in-cmd-cmd-of-python
#   http://stackoverflow.com/questions/23749097/override-undocumented-help-area-in-pythons-cmd-module

import cmd, getpass, glob, json, logging, os, requests, shlex, sys

import help_strings


# Helper function for Linux Filepath completion
def _append_slash_if_dir(p):
    if p and os.path.isdir(p) and p[-1] != os.sep:
        return p + os.sep
    else:
        return p


# TODO remove this whole section when testing is done, or figure out
# how to bind it into the other logger properly so verbose works
#----------------------------------------------------------------------
# Enabling debugging at http.client level (requests->urllib3->http.client)
# you will see the REQUEST, including HEADERS and DATA, and RESPONSE with HEADERS but without DATA.
# the only thing missing will be the response.body which is not logged.
try: # for Python 3
    from http.client import HTTPConnection
except ImportError:
    from httplib import HTTPConnection
HTTPConnection.debuglevel = 1
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True
#----------------------------------------------------------------------


class AutoShell(cmd.Cmd):

    # TODO Call server to identify user as student, ta,
    # or teacher.
    user = "student"
    username = getpass.getuser()
    server = "http://127.0.0.1:8000"

    intro = 'Welcome to the AUTO Universal Testing Organizer (AUTO) shell.\n   Type help or ? to list commands'
    prompt = '>>> '

    # Override print_topics to prevent undocumented commands from showing up
    # in help.
    undoc_header = None
    def print_topics(self, header, cmds, cmdlen, maxcol):
        if header is not None:
            cmd.Cmd.print_topics(self, header, cmds, cmdlen, maxcol)


    def preloop(self):
        # create logger for AUTO
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

        # create console handler
        self.ch = logging.StreamHandler()
        self.ch.setLevel(logging.WARNING)

        # create formatter
        self.formatter = logging.Formatter("%(asctime)s - %(funcName)s - %(levelname)s: %(message)s")

        # add formatter to console handler
        self.ch.setFormatter(self.formatter)

        # add console handler to logger
        self.logger.addHandler(self.ch)
        
        
    def emptyline(self):
        pass


    def do_verbose(self, args):
        args = args.split()
        if args:
            if args[0]=="on":
                self.ch.setLevel(logging.DEBUG)
                print("Verbose: ON")
            elif args[0]=="off":
                self.ch.setLevel(logging.WARNING)
                print("Verbose: OFF")

    #----------------------------------------
    def do_course(self, args):
        self.logger.debug("START. Args='{0}'".format(args))
        args = parse(args)
        self.logger.debug("Args split. Args='{0}'".format(args))
        if args:
            # course view
            if args[0]=="view":
                self.logger.debug("Entering VIEW mode")
                url = self.server + '/course/view/'
                self.logger.debug("url is '{0}'".format(url))

                validkeys = ["course-id","dept","course-number","num","course-name","name","term","year"]
                self.logger.debug("Entering argument processing")
                # args[1:] skips first entry (which will be view)
                data = parsekv(validkeys, args[1:])
                self.logger.debug("data is '{0}'".format(data))

                self.logger.debug("GETting submission")
                # TODO gracefully handle failure
                r = requests.get(url, json=data)

                # TODO more robust error reporting
                if r.status_code==200:
                    print("Submission succeeded!")
                else:
                    self.logger.error("Failed")
                    
            elif args[0] in ["add", "update", "delete"]:
                if self.user!="teacher":
                    print("\nError: Arguments not valid\n")
                    self.onecmd("help course")
                
                # course add
                elif args[0]=="add":
                    self.logger.debug("Entering ADD mode")
                    url = self.server + '/course/add/'
                    self.logger.debug("url is '{0}'".format(url))
                    
                    validkeys = ["dept","course-number","num","course-name","name","term","year"]
                    self.logger.debug("Entering argument processing")
                    # args[1:] skips first entry (which will be view)
                    data = parsekv(validkeys, args[1:])
                    self.logger.debug("data is '{0}'".format(data))
                    
                    if len(data)<1:
                        print("\nError: 'course add' requires at least one key-value pair\n")
                        self.onecmd("help course")
                    else:
                        self.logger.debug("POSTing submission")
                        # TODO gracefully handle failure
                        r = requests.post(url, json=data)

                        # TODO more robust error reporting
                        if r.status_code==201:
                            print("Submission succeeded!")
                        else:
                            self.logger.error("Failed")
            else:
                print("\nError: Arguments not valid\n")
                self.onecmd("help course")
        self.logger.debug("END")


    def help_course(self):
        self.print_help("course")
    #----------------------------------------

    def do_assignment(self, args):
        'Add, View, Update, Delete Assignments'
        print("Not implemented")

    def help_assignment(self):
        self.print_help("assignment")


    #----------------------------------------

    def do_tag(self, args):
        'Tag assignments with keywords'
        print("Not implemented")

    def help_tag(self):
        self.print_help("tag")

    #----------------------------------------

    def do_test(self, args):
        'Add, View, Update, Delete Tests'
        print("Not implemented")

    def help_test(self):
        self.print_help("test")

    #----------------------------------------

    def do_student(self, args):
        'Add, View, Delete Students'
        print("Not implemented")

    def help_student(self):
        self.print_help("student")

    #----------------------------------------

    def do_ta(self, args):

        print("Not implemented")

    def help_ta(self):
        self.print_help("ta")


    #----------------------------------------

    def do_group(self, args):
        print("Not implemented")

    def help_group(self):
        self.print_help("")

    #----------------------------------------

    def do_submission(self, args):
        self.logger.debug("START. Args='{0}'".format(args))
        args = parse(args)
        self.logger.debug("Args split. Args='{0}'".format(args))
        if args:
            if args[0]=="add" and len(args)>=3:
                self.logger.debug("Entering ADD mode")
                try:
                    # TODO (if time available) - verify that assignment can be
                    # submitted before sending file.
                    int(args[1])
                    self.logger.debug("assignment-id is {0}".format(args[1]))
                except ValueError:
                    print("Error: assignment-id must be an integer value.")
                    return
                url = self.server + '/submission/'
                self.logger.debug("url is '{0}'".format(url))
                data = { "assignment-id": args[1],
                         "onid": self.username
                         }
                self.logger.debug("data is '{0}'".format(data))

                # TODO verify filepath - handle open failure gracefully
                files = { "file": open(args[2], 'rb') }
                self.logger.debug("file is '{0}'".format(args[2]))

                self.logger.debug("POSTing submission")
                # TODO gracefully handle failure
                r = requests.post(url, files=files, data=data)

                # TODO more robust error reporting
                if r.status_code==200:
                    print("Submission succeeded!")
                else:
                    self.logger.error("Failed")
            else:
                print("\nError: Arguments not valid\n")
                self.onecmd("help submission")
        self.logger.debug("END")

    def help_submission(self):
        self.print_help("submission")

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

    #----------------------------------------

    def do_grade(self, args):
        'Alias of submission update'
        print("Not implemented")

    def help_grade(self):
        self.print_help("grade")

    #----------------------------------------

    def do_ce(self, args):
        'Add, View, Update, Delete Common Errors'
        print("Not implemented")

    def help_ce(self):
        self.print_help("ce")

    #----------------------------------------

    # TODO Delete or Comment out for final version
    def do_level(self, args):
        args = parse(args)
        if args:
            if args[0]=="teacher":
                self.user="teacher"
                print("Now a teacher!")
            elif args[0]=="ta":
                self.user="ta"
                print("Now a ta!")
            elif args[0]=="student":
                self.user="student"
                print("Now a student!")
            else:
                print("You could be anything! Even a boat!")
        else:
            print("You are a {0}!".format(self.user))

    #----------------------------------------

    def do_EOF(self, args):
        print("Thanks for using AUTO!\n")
        return True

    # aliases for EOF
    def do_exit(self, args):
        self.onecmd("EOF")
        return True

    def do_quit(self, args):
        self.onecmd("EOF")
        return True


    # Helper function for printing help messages
    def print_help(self, help_target):
        if self.user=="teacher":
                print(help_strings.teacher[help_target])
        elif self.user=="ta":
                print(help_strings.ta[help_target])
        elif self.user=="student":
                print(help_strings.student[help_target])
        else:
                print("Are you a boat? I don't know how to help" + self.user + "s... :(")

def parse(arg):
    return shlex.split(arg)

def parsekv(validkeys, args):
    data = {}
    for arg in args:
        arg = arg.split('=')

        if len(arg)!=2:
            auto.logger.warning("'{0}' is not a valid key-value pair".format(arg))
            continue

        key, value = arg[0], arg[1]

        if key not in validkeys:
            auto.logger.warning("'{0}' is not a valid key".format(arg))
            continue

        data[key] = value
    return data

if __name__ == '__main__':
    auto = AutoShell()
    auto.cmdloop()
