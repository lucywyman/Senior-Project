#!/usr/bin/env python3

# AUTO command line interface
# Created by Nathan Hennig, Lucy Wyman, Andrew Gass
# Oregon State University - Senior Design Project
# 2/4/16
# Resourses:
#   http://stackoverflow.com/questions/9973990/python-cmd-dynamic-docstrings-for-do-help-function
#   http://stackoverflow.com/questions/16826172/filename-tab-completion-in-cmd-cmd-of-python
# http://stackoverflow.com/questions/23749097/override-undocumented-help-area-in-pythons-cmd-module

import cmd, getpass, glob, json, os, requests, sys

import help_strings


# Helper function for Linux Filepath completion
def _append_slash_if_dir(p):
    if p and os.path.isdir(p) and p[-1] != os.sep:
        return p + os.sep
    else:
        return p


    


class AutoShell(cmd.Cmd):

    # TODO Call server to identify user as student, ta,
    # or teacher.
    user = "student"
    username = getpass.getuser()
    server = "http://127.0.0.1:8000/"

    intro = 'Welcome to the AUTO Universal Testing Organizer (AUTO) shell.\n   Type help or ? to list commands'
    prompt = '>> '

    # Override print_topics to prevent undocumented commands from showing up
    # in help.
    undoc_header = None
    def print_topics(self, header, cmds, cmdlen, maxcol):
        if header is not None:
            cmd.Cmd.print_topics(self, header, cmds, cmdlen, maxcol)

    def do_EOF(self, args):
        print("Thanks for using AUTO!\n")
        return True

    #----------------------------------------
    def do_course(self, args):
        'Add, View, Update, Delete Courses'
        print("Not implemented")
        
    def help_course(self):
        self.help_print("course")
    #----------------------------------------
        
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
            data = { "assignment-id": args[1],
                     "onid": self.username
					 }
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
        
    def do_level(self, args):
        args = args.lower()
        if args=="teacher":
            self.user="teacher"
            print("Now a teacher!")
        elif args=="ta":
            self.user="ta"
            print("Now a ta!")
        elif args=="student":
            self.user="student"
            print("Now a student!")
        else:
            print("You could be anything! Even a boat!")
    
    
    # aliases for EOF
    def do_exit(self, args):
        self.do_EOF(args)
        return True
        
    def do_quit(self, args):
        self.do_EOF(args)
        return True

    # Helper function for printing help messages
    def help_print(self, help_target):
        if self.user=="teacher":
                print(help_strings.teacher[help_target])
        elif self.user=="ta":
                print(help_strings.ta[help_target])
        elif self.user=="student":
                print(help_strings.student[help_target])
        else:
                print("Are you a boat? I don't know how to help" + self.user + "s... :(")

if __name__ == '__main__':
    AutoShell().cmdloop()
