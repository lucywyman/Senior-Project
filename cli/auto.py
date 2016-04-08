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
import argparse
from bs4 import BeautifulSoup
from functools import total_ordering

from multiprocessing.pool import ThreadPool, TimeoutError

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

    CA_BUNDLE = 'ca.cert'

    # TODO Call server to identify user as student, ta,
    # or teacher.
    def __init__(self, user='', password='', verbosity=0):

        self.auth_level = ''
        self.user = user
        self.password = password
        self.new_password = ''
        self.auth = (user, password)
        self.server = "https://vm-cs-cap-g15.eecs.oregonstate.edu:443"
        self.pool = ThreadPool(processes=5)


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


        if verbosity:
            if verbosity>2:
                print("-vv is maximum verbosity")
                print("setting verbosity to -vv")
                self.ch.setLevel(logging.DEBUG)
            elif verbosity==2:
                self.ch.setLevel(logging.DEBUG)
            elif verbosity==1:
                self.ch.setLevel(logging.INFO)
            else:
                self.ch.setLevel(logging.WARNING)

        super(AutoShell, self).__init__()

    intro = 'Welcome to the AUTO Universal Testing Organizer (AUTO) shell.\n   Type help or ? to list commands'
    prompt = '>>> '

    # Override print_topics to prevent undocumented commands from showing up
    # in help.
    undoc_header = None
    def print_topics(self, header, cmds, cmdlen, maxcol):
        if header is not None:
            cmd.Cmd.print_topics(self, header, cmds, cmdlen, maxcol)


    def preloop(self):

        # login
        if self.user and self.password:
            self.onecmd(
                'login as name={0} password={1}'
                .format(self.user, self.password)
                )


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

        # bypass access checking for login command since everyone has access
        # to it, and users initially have no auth_level while logging in
        if command=='login':
            pass
        elif not self.auth_level:
            print('\n*** Unauthorized: Please login first\n')
            self.onecmd("help login")
            return
        elif not self.command_access(self.auth_level, command, args[0]):
            print("\n*** Unauthorized: {0} {1}\n".format(command, args[0]))
            self.logger.debug("END")
            return

        self.logger.debug("Entering {0} mode".format(args[0].upper()))

        #TODO - Add support for multiple values per key (ie student=hennign,luxylu,grepa)
        data = self.command_data(command, args)

        if data==False:
            print("\nError: Arguments not valid\n")
            self.onecmd("help " + command)
            self.logger.debug("END")
            return

        response = self.command_request(command, args[0], data)

        self.logger.info('Response: {0}'.format(response))

        if response==None:
            self.logger.debug("No Resposnse")
            self.logger.debug("END")
            return

        self.command_response(command, args[0], response)

        self.logger.debug("END")
        return


    def command_access(self, auth_level, command, subcommand):
        self.logger.debug("Checking access levels.")
        self.logger.debug("User level is {0}.".format(auth_level))
        self.logger.debug("Access for {0} is {1}".format(auth_level, command_dict.commands[command][subcommand]["access"][auth_level]))

        if not command_dict.commands[command][subcommand]["access"][auth_level]:
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

        if command=='login':
            if subcommand=='as':
                self.user = data['name'][0]
                self.password = data['password'][0]
                self.auth = (self.user, self.password)

            if subcommand=='update':
                self.password = data['password'][0]
                self.new_password = data['new-password'][0]
                self.auth = (self.user, self.password)



        if "filepath" in data:
            # TODO verify filepath - handle open failure gracefully
            #TODO - handle multiples?
            data['filepath'][0] = os.path.normpath(data['filepath'][0])
            files = { "file": open(data['filepath'][0], 'rb') }
            self.logger.debug("file is '{0}'".format(data['filepath'][0]))




            if command=='submission' and subcommand=='add':
                async_req = self.pool.apply_async(
                    self.submission_submit,
                    args=(url, files, data)
                    )
                sys.stdout.write("Waiting for test results. Press any key to cancel... ")
                while True:
                    if kbhit():
                        print("Wait aborted. Check back later for test results using:")
                        print("\tsubmission view assignment-id={0}"
                            .format(data['assignment-id'])
                            )
                        return None

                    try:
                        ret = t.get(.01)
                    except TimeoutError:
                        pass
                    else:
                        return ret

            if subcommand in ['add', 'update']:
                self.logger.debug("POSTing w/file")
                try:
                    r = requests.post(url, files=files, data=data, auth=self.auth, verify=self.CA_BUNDLE)
                except requests.ConnectionError as e:
                    self.logger.warning(
                        'ConnectionError: {0}'.format(e.response)
                        )

        else:
            if subcommand in ['add', 'update', 'link'] or command=='login':
                self.logger.debug("POSTing w/o file")
                try:
                    # send POST request to server
                    r = requests.post(url, json=data, auth=self.auth, verify=self.CA_BUNDLE)
                except requests.ConnectionError as e:
                    self.logger.warning(
                        'ConnectionError: {0}'.format(e.response)
                        )

            elif subcommand == 'view':
                self.logger.debug("GETting")
                try:
                    r = requests.get(url, json=data, auth=self.auth, verify=self.CA_BUNDLE)
                except requests.ConnectionError as e:
                    self.logger.warning(
                        'ConnectionError: {0}'.format(e.response)
                        )

            elif subcommand == 'delete':
                com = command_dict.commands[command][subcommand]
                question = None

                if com["confirmation"]:
                    question = com["confirmation"] + ' Proceed? '

                if question and not query_yes_no(question):
                    self.logger.debug("Operation aborted.")
                    return False

                self.logger.debug("DELETEing")
                try:
                    r = requests.delete(url, json=data, auth=self.auth, verify=self.CA_BUNDLE)
                except requests.ConnectionError as e:
                    self.logger.warning(
                        'ConnectionError: {0}'.format(e.response)
                        )

        return r


    def command_response(self, command, subcommand, response):

        self.logger.info("Response Status Code: {0}"
            .format(response.status_code)
            )

        print()

        if response==None:
            self.logger.warning(
                'ServerError: No response received from server'
                )
            return

        if response.status_code==200: # HTTPStatus.OK
            self.logger.debug("Entered 200 code")

            try:
                data = response.json()
            except ValueError as e:
                self.logger.debug("ValueError: {0}".format(e))
                self.logger.debug("No JSON data in response")
                data = None
            except:
                self.logger.exception("Unexpected Error")
                data = None
            else:
                self.logger.debug("Data: {0}".format(data))

            if command=='login' and data!=None:

                if subcommand=='as':
                    self.auth_level = data['auth_level']
                    print("Logged in as '{0}' with authority level '{1}'\n"
                        .format(self.user, self.auth_level)
                        )

                elif subcommand=='update':
                    self.auth_level = data['auth_level']
                    self.password = self.new_password
                    print('\nPassword successfully updated\n')

                return

            if data==None:
                print(
                    "\nHTTP {0}: Success\n"
                    .format(response.status_code)
                    )
            else:
                self.print_response(
                    command, subcommand, data
                    )

        elif response.status_code==201: # HTTPStatus.CREATED
            self.logger.debug("Entered 201 code")

            if command=='login':

                try:
                    data = response.json()
                except ValueError:
                    print(
                        "\nHTTP {0}: Success\n"
                        .format(response.status_code)
                        )
                else:
                    if subcommand=='new':
                        print('Created new user {0}'
                            .format(data['name'])
                        )
                return


        elif response.status_code==204:
            self.logger.debug("Entered 204 code")
            print(
                "\nHTTP {0}: No results matched your query\n"
                .format(response.status_code)
                    )

        # HTTPStatus.BAD_REQUEST, HTTPStatus.UNAUTHORIZED,
        # HTTPStatus.FORBIDDEN, HTTPStatus.NOT_FOUND
        elif response.status_code in [400,401,403, 404]:
            self.logger.debug("Entered 400,401,403 code")

            print(
                    '\nError code: {0} - {1}'
                    .format(
                        response.status_code,
                        response.reason
                        )
                    )

            if command=='login':
                if subcommand=='as':
                    self.auth_level = ''
                    print("Login attempt failed. Please try again.\n")

                elif subcommand=='update':
                    self.auth_level = ''
                    print("Password update failed. Please try again.\n")

                else:
                    print()


            return

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

    def do_login(self, args):
        self.command_exec("login", args)

    def help_login(self):
        self.print_help("login")

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
                self.auth_level="teacher"
                print("Now a teacher!")
            elif args[0]=="ta":
                self.auth_level="ta"
                print("Now a ta!")
            elif args[0]=="student":
                self.auth_level="student"
                print("Now a student!")
            else:
                print("You could be anything! Even a boat!")
        else:
            if self.auth_level:
                print("You are a {0}!".format(self.auth_level))
            else:
                print("No user level. Login command access only.")

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

        self.logger.debug("Help Target: {0}".format(help_target))

        if command_dict.commands.get(help_target):

            access_granted = False
            syn_wrapper = textwrap.TextWrapper(initial_indent='\t', width=80, subsequent_indent='\t\t')
            wrapper = textwrap.TextWrapper(initial_indent='\t\t', width=80, subsequent_indent='\t\t')

            for key in command_dict.commands[help_target]:
                if self.auth_check_helper(help_target, key):
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
                    if self.auth_check_helper(help_target, key):
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
                    if self.auth_check_helper(help_target, key):
                        print('\t' + help_target + ' ' + key)
                        print(wrapper.fill(com['help']))
                        print()

                print()
                print('OPTIONS')
                print()
                options_list = []
                for key in command_dict.commands[help_target]:
                    com = command_dict.commands[help_target][key]
                    if self.auth_check_helper(help_target, key):
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

    def auth_check_helper(self, help_target, key):
        """For print_help, to allow a single place
        for exceptions to auth checking
        """

        if (
            command_dict.commands[help_target][key]['access']
            .get(self.auth_level)
            or help_target=='login'
            ):
            return True

        else:
            return False

    def print_response(self, command, subcommand, json):

        self.logger.debug("Data: {0}".format(json))

        data = json

        cols = [
            x for x in sql_dict.sql[command][subcommand]['view_order']
            if x in data[0]
            ]
        self.logger.debug("Cols: {0}".format(cols))


        sort_order = [
            x for x in
            sql_dict.sql[command][subcommand]['sort_order'] if x in data[0]
            ]
        self.logger.debug("Sort Order: {0}".format(sort_order))


        col_widths = [
            max([len(str(row[key])) for row in data] + [len(str(key))])+4
            for key in cols
            ]
        self.logger.debug("Column Widths: {0}".format(col_widths))

        print(
            "|".join(str(val).center(col_widths[pos])
            for pos,val in enumerate(cols))
            )

        print(
            "|".join(str("="*(col_widths[pos]-2)).center(col_widths[pos])
            for pos,val in enumerate(cols))
            )

        Min = MinType()
        try:
            data.sort(key = lambda x: [x[key] or Min for key in sort_order])
        except TypeError:
            self.logger.exception("Sorting failed")
        else:
            self.logger.debug("Sorted Data: {0}".format(data))

        for row in data:
            print(
                "|".join(
                    str(row[val]).center(col_widths[pos])
                    for pos,val in enumerate(cols)
                    )
                )


    def submission_submit(self, url, files, data):

        self.logger.debug("POSTing Submission")
        try:
            r = requests.post(url, files=files, data=data, verify=self.CA_BUNDLE)
        except requests.ConnectionError as e:
            self.logger.warning(
                'ConnectionError: {0}'.format(e.response)
                )
            return None
        else:
            return r



try:
    from msvcrt import kbhit, getch
except:
    import termios, fcntl, sys, os
    def kbhit(t):
        fd = sys.stdin.fileno()

        oldterm = termios.tcgetattr(fd)
        newattr = termios.tcgetattr(fd)
        newattr[3] = newattr[3] & ~termios.ICANON & ~termios.ECHO
        termios.tcsetattr(fd, termios.TCSANOW, newattr)

        oldflags = fcntl.fcntl(fd, fcntl.F_GETFL)
        fcntl.fcntl(fd, fcntl.F_SETFL, oldflags | os.O_NONBLOCK)


        try:
            c = sys.stdin.read(1)
            if c!=None:
                return True

        except IOError: pass

        finally:
            termios.tcsetattr(fd, termios.TCSAFLUSH, oldterm)
            fcntl.fcntl(fd, fcntl.F_SETFL, oldflags)
            return False






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

@total_ordering
class MinType(object):
    def __le__(self, other):
        return True

    def __eq__(self, other):
        return (self is other)

if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    parser.add_argument("-v", "--verbosity", action="count",
                    help="Specify output verbosity")

    parser.add_argument('-u', '--user', default='',
                        help='User name to login with')
    parser.add_argument('-p', '--password', default='',
                        help='password to login with')
    args = parser.parse_args()


    auto = AutoShell(
        user=args.user,
        password=args.password,
        verbosity=args.verbosity
        )
    auto.cmdloop()
