#!/usr/bin/env python3

# AUTO command line interface
# Created by Nathan Hennig, Lucy Wyman, Andrew Gass
# Oregon State University - Senior Design Project
# 2/4/16
# Resourses:
#   http://stackoverflow.com/questions/9973990/python-cmd-dynamic-docstrings-for-do-help-function
#   http://stackoverflow.com/questions/16826172/filename-tab-completion-in-cmd-cmd-of-python
#   http://stackoverflow.com/questions/23749097/override-undocumented-help-area-in-pythons-cmd-module
#   http://stackoverflow.com/questions/3041986/python-command-line-yes-no-input

import cmd, getpass, glob, json, logging, os, requests, shlex, sys

import command_dict, sql_dict
import re, textwrap

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


    def command_exec(self, command, args):
        self.logger.debug("START. Args='{0}'".format(args))
        args = parse(args)
        self.logger.debug("Args split. Args='{0}'".format(args))

        if not args:
            print("\nError: Arguments not valid\n")
            self.onecmd("help " + command)
            self.logger.debug("END")
            return

        if not self.command_access(self.user, command, args[0]):
            print("\nError: Arguments not valid\n")
            self.logger.debug("END")
            return

        self.logger.debug("Entering {0} mode".format(args[0].upper()))

        #TODO - Add support for multiple values per key (ie student=hennign,luxylu,grepa)
        data = self.command_data(command, args)

        if data == False:
            print("\nError: Arguments not valid\n")
            self.onecmd("help " + command)
            self.logger.debug("END")
            return

        response = self.command_request(command, args[0], data)

        if response == False:
            self.logger.debug("END")
            return

        self.command_response(command, args[0], response)

        self.logger.debug("END")
        return


    def command_access(self, user, command, subcommand):
        self.logger.debug("Checking access levels.")
        self.logger.debug("User level is {0}.".format(user))
        self.logger.debug("Access for {0} is {1}".format(user, command_dict.commands[command][subcommand]["access"][user]))

        if not command_dict.commands[command][subcommand]["access"][user]:
            self.logger.debug("Access denied.")
            return False

        self.logger.debug("Access granted.")
        return True


    def command_data(self, command, args):
        self.logger.debug("Entering argument processing.")
        com = command_dict.commands[command][args[0]]

        self.logger.debug("Valid keys include {0}, {1}, {2}.".format(com["required"], com["required2"], com["optional"]))
        validkeys = com["required"] + com["required2"] + com["optional"]

        # args[1:] skips first entry (which will be a subcommand)
        data = parsekv(validkeys, args[1:])
        self.logger.debug("data is '{0}'".format(data))

        self.logger.debug("Verifying that required options are present.")
        keys = data.keys()

        required = False
        if set(com["required"]).issubset(keys):
            required = True
        elif com["required2"] and set(com["required2"]).issubset(keys):
            required = True

        if not required:
            self.logger.debug("Not all required arguments given.")
            return False

        #TODO - Verify value types

        return data


    def command_request(self, command, subcommand, data):
        url = self.server + '/' + command + '/' + subcommand + '/'
        self.logger.debug("url is '{0}'".format(url))

        r = None
        files = {}

        if "filepath" in data:
            # TODO verify filepath - handle open failure gracefully
            #TODO - handle multiples?
            data['filepath'][0] = os.path.normpath(data['filepath'][0])
            files = { "file": open(data['filepath'][0], 'rb') }
            self.logger.debug("file is '{0}'".format(data['filepath'][0]))

            if subcommand in ['add', 'update']:
                self.logger.debug("POSTing")
                # TODO gracefully handle failure
                r = requests.post(url, files=files, data=data)

        else:
            if subcommand in ['add', 'update', 'link']:
                self.logger.debug("POSTing")
                # TODO gracefully handle failure
                r = requests.post(url, json=data)

            elif subcommand == 'view':
                self.logger.debug("GETting")
                # TODO gracefully handle failure
                r = requests.get(url, json=data)

            elif subcommand == 'delete':
                com = command_dict.commands[command][subcommand]
                question = None

                if com["confirmation"]:
                    question = com["confirmation"] + ' Proceed? '

                if question and not query_yes_no(question):
                    self.logger.debug("Operation aborted.")
                    return False

                self.logger.debug("DELETEing")
                # TODO gracefully handle failure
                r = requests.delete(url, json=data)

        return r


    def command_response(self, command, subcommand, response):
        # TODO more robust error reporting
        print()
        if response.status_code==200:
            try:
                self.print_response(command, subcommand, response.json())
            except:
                print("\nNo response")
        else:
            self.logger.error("Failed")

    #----------------------------------------

    def do_assignment(self, args):
        self.command_exec("assignment", args)

    def help_assignment(self):
        self.print_help("assignment")

    #----------------------------------------

    def do_ce(self, args):
        self.command_exec("ce", args)

    def help_ce(self):
        self.print_help("ce")

    #----------------------------------------

    def do_course(self, args):
        self.command_exec("course", args)


    def help_course(self):
        self.print_help("course")
    #----------------------------------------

    def do_grade(self, args):
        self.command_exec("grade", args)

    def help_grade(self):
        self.print_help("grade")

    #----------------------------------------

    def do_group(self, args):
        self.command_exec("group", args)

    def help_group(self):
        self.print_help("group")

    #----------------------------------------

    def do_student(self, args):
        self.command_exec("student", args)

    def help_student(self):
        self.print_help("student")

    #----------------------------------------

    def do_submission(self, args):
        self.command_exec("submission", args)

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

    def do_ta(self, args):
        self.command_exec("ta", args)

    def help_ta(self):
        self.print_help("ta")

    #----------------------------------------

    def do_tag(self, args):
        self.command_exec("tag", args)

    def help_tag(self):
        self.print_help("tag")

    #----------------------------------------

    def do_test(self, args):
        self.command_exec("test", args)

    def complete_test(self, text, line, begidx, endidx):
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

    def help_test(self):
        self.print_help("test")

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

    # TODO - add pagination for long helps
    def print_help(self, help_target):
        if command_dict.commands.get(help_target):
            access_granted = False
            syn_wrapper = textwrap.TextWrapper(initial_indent='\t', width=80, subsequent_indent='\t\t')
            wrapper = textwrap.TextWrapper(initial_indent='\t\t', width=80, subsequent_indent='\t\t')
            for key in command_dict.commands[help_target]:
                if command_dict.commands[help_target][key]['access'].get(self.user):
                    access_granted = True
            if access_granted:
                
                print()
                print('NAME')
                print()
                print('\t' + help_target)
                print()
                print()
                print('SYNOPSIS')
                print()
                
                # print subcommands
                for key in command_dict.commands[help_target]:
                    com = command_dict.commands[help_target][key]
                    if com['access'].get(self.user):
                        req1 = None
                        req2 = None
                        req3 = None
                        options = ""
                        if com.get('required'):
                            req1 = " ".join(['{0}=<value>'.format(x) for x in com['required']])
                            req1 = '(' + req1 + ')'
                        if com.get('required2'):
                            req2 = " ".join(['{0}=<value>'.format(x) for x in com['required2']])
                            req2 = '(' + req2 + ')'
                        if com.get('optional'):
                            options = " ".join(['{0}=<value>'.format(x) for x in com['optional']])
                            options = '[' + options + ']'
                        
                        if req1 and req2:
                            req3 = '(' + req1 + '|' + req2 + ')'
                        
                        
                        if req1 and not req2:
                            syn = help_target + ' ' + key + ' ' + req1 + ' ' + options
                        elif not req1 and req2:
                            syn = help_target + ' ' + key + ' ' + req2 + ' ' + options
                        elif req3:
                            syn = help_target + ' ' + key + ' ' + req3 + ' ' + options
                        else:
                            syn = help_target + ' ' + key + ' ' + options
                            
                        print(syn_wrapper.fill(syn))
                        print()
                
                print()
                print('DESCRIPTION')
                print()
             
                for key in command_dict.commands[help_target]:
                    com = command_dict.commands[help_target][key]
                    if com['access'].get(self.user):
                        print('\t' + help_target + ' ' + key)
                        print(wrapper.fill(com['help']))
                        print()
                        
                print()
                print('OPTIONS')
                print()
                options_list = []
                for key in command_dict.commands[help_target]:
                    com = command_dict.commands[help_target][key]
                    if com['access'].get(self.user):
                        options_list += com['required'] + com['required2'] + com['optional']
                
                options_list = list(set(options_list))
                options_list.sort()
                
                for opt in options_list:
                    print('\t' + opt)
                    print(wrapper.fill(command_dict.options[opt]['help']))
                    print()
                
                print()
                
                        
                
            else:
                print('\n**** Access denied\n')
        else:
            print('\n**** Command not found\n')

    def print_response(self, command, subcommand, json):
        
        self.logger.debug("Data is: {0}".format(json))
    
        data = json
        
        cols = sql_dict.sql[command][subcommand]['view_order']
 
        col_widths = [max([len(str(row[key])) for row in data] + [len(str(key))])+4 for key in cols]
        
        print("|".join(str(val).center(col_widths[pos]) for pos,val in enumerate(cols)))
        
        print("|".join(str("="*(col_widths[pos]-2)).center(col_widths[pos]) for pos,val in enumerate(cols)))
        
        data.sort(key = sql_dict.sql[command][subcommand]['sort_order'])
        
        for row in data:
            print("|".join(str(row[val]).center(col_widths[pos]) for pos,val in enumerate(cols)))

        
        
        
def parse(arg):
    pattern = re.compile(r'''((?:[^\s"']|"[^"]*"|'[^']*')+)''')
    return pattern.split(arg)[1::2]

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

        value = value.split(',')

        data[key] = value

    for key in data:
        for id, value in enumerate(data[key]):
            if ((value.startswith('"') and value.endswith('"'))
                or (value.startswith("'") and value.endswith("'"))):
                data[key][id] = value[1:-1]

    return data

def query_yes_no(question, default="no"):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    """
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")

if __name__ == '__main__':
    auto = AutoShell()
    auto.cmdloop()
