#!/usr/bin/env python3
# (c) 2019 Marvin Löbel
# This code is licensed under MIT license (see LICENSE for details)

import sys
import os
import subprocess
import re
import argparse

CEND      = '\33[0m'
CBOLD     = '\33[1m'
CITALIC   = '\33[3m'
CURL      = '\33[4m'
CBLINK    = '\33[5m'
CBLINK2   = '\33[6m'
CSELECTED = '\33[7m'

CBLACK  = '\33[30m'
CRED    = '\33[31m'
CGREEN  = '\33[32m'
CYELLOW = '\33[33m'
CBLUE   = '\33[34m'
CVIOLET = '\33[35m'
CBEIGE  = '\33[36m'
CWHITE  = '\33[37m'

CBLACKBG  = '\33[40m'
CREDBG    = '\33[41m'
CGREENBG  = '\33[42m'
CYELLOWBG = '\33[43m'
CBLUEBG   = '\33[44m'
CVIOLETBG = '\33[45m'
CBEIGEBG  = '\33[46m'
CWHITEBG  = '\33[47m'

CGREY    = '\33[90m'
CRED2    = '\33[91m'
CGREEN2  = '\33[92m'
CYELLOW2 = '\33[93m'
CBLUE2   = '\33[94m'
CVIOLET2 = '\33[95m'
CBEIGE2  = '\33[96m'
CWHITE2  = '\33[97m'

CGREYBG    = '\33[100m'
CREDBG2    = '\33[101m'
CGREENBG2  = '\33[102m'
CYELLOWBG2 = '\33[103m'
CBLUEBG2   = '\33[104m'
CVIOLETBG2 = '\33[105m'
CBEIGEBG2  = '\33[106m'
CWHITEBG2  = '\33[107m'

def colorize(text, colorcode):
    if sys.stdout.isatty():
        return colorcode + str(text) + CEND
    else:
        return str(text)

re_error = re.compile("^!|Error")
re_warning = re.compile("Warning")
re_full = re.compile("Overfull|Underfull")
re_path = re.compile("(\\./.*?\\.(pygtex|pygstyle|tex|pdf|png|toc|sty|w18))")
re_run = re.compile("Run number [0-9]+ of rule")

todo_words = ["TODO", "FIXME", "todo", "fixme", "Todo", "Fixme"]
re_todo = re.compile("|".join(todo_words))


parser = argparse.ArgumentParser(
    description='''
Wraps a latex commandline, and parses its output to produce
more readable warnings. Example: `%(prog)s -a latexmk -pdf foo.tex`
    ''',
    usage='%(prog)s [options] <latex commandline>...'
)
parser.add_argument('-w', '--warnings', action='store_true',
                    help='output warnings.')
parser.add_argument('-e', '--errors', action='store_true',
                    help='output errors.')

parser.add_argument('-b', '--warn-box', action='store_true',
                    help='output overfull and underfull box warnings.')
parser.add_argument('-t', '--warn-todo', action='store_true',
                    help='output todo warnings.')
parser.add_argument('-f', '--all-files', action='store_true',
                    help='print all processed file paths, not just *.tex.')

parser.add_argument('-n', '--no-raw', action='store_true',
                    help='do not output the raw stdout and stderr of the wrapped process.')
parser.add_argument('-l', '--last-run', action='store_true',
                    help='only output warnings from the last run. This conflicts with -i.')
parser.add_argument('-i', '--interleaved', action='store_true',
                    help='print the output interleaved with the raw output. '
                    'This allows interactive and endless commandlines.')

parser.add_argument('-a', '--all', action='store_true',
                    help='enables all generally useful warnings. implies -webt.')
parser.add_argument('-V', '--verbose', action='store_true',
                    help='enables all possible warnings. implies -af.')

(args, cmd) = parser.parse_known_args()

# Optional warnings
print_full_boxes = args.warn_box  or args.all or args.verbose
print_todo       = args.warn_todo or args.all or args.verbose
print_warnings   = args.warnings  or args.all or args.verbose
print_errors     = args.errors    or args.all or args.verbose

# Optional warnings, verbose
print_all_files  = args.all_files             or args.verbose

# More complicated features
print_no_raw      = args.no_raw
print_last_run    = args.last_run
print_interleaved = args.interleaved

# Setup line processing environment
def reset_run_state():
    global last_run_buffer
    global last_file
    global current_file
    last_run_buffer = ""
    last_file = None
    current_file = "asdf"
reset_run_state()

def rprint(s):
    global last_run_buffer
    if not print_last_run:
        print("{}".format(s))
    else:
        last_run_buffer += "{}\n".format(s)

def handle_line(line):
    global last_run_buffer
    global last_file
    global current_file

    if re_run.match(line):
        reset_run_state()
        print(colorize(line.strip(), CBEIGEBG))

    def print_warning(warn_text):
        global last_file
        global current_file
        global print_all_files

        if current_file != last_file:
            if not print_all_files:
                rprint("File {}".format(colorize(last_file, CGREEN)))
            current_file = last_file
        rprint("  " + warn_text.strip())

    for m in re_path.findall(line):
        last_file_candidate = str(m[0])
        if print_all_files:
            last_file = last_file_candidate
            rprint("File {}".format(colorize(last_file, CGREEN)))
        if last_file_candidate.endswith(".tex"):
            last_file = last_file_candidate
            if print_todo and os.path.isfile(last_file):
                with open(last_file, 'r') as f:
                    for i,line2 in enumerate(f.readlines()):
                        if re_todo.search(line2):
                            for todo_word in todo_words:
                                line2 = line2.replace(todo_word, colorize(todo_word, CVIOLET))
                            print_warning("{} on line {}: {}".format(colorize("Todo", CVIOLET), i, line2))

    found = False
    if print_errors and re_error.search(line):
        line = line.replace("Error", colorize("Error", CRED))
        if line.startswith("!"):
            line = colorize("Error", CRED) + ": " + line
        found = True
    if print_warnings and re_warning.search(line):
        line = line.replace("Warning", colorize("Warning", CYELLOW))
        found = True
    if print_full_boxes and re_full.search(line):
        line = line.replace("Overfull", colorize("Overfull", CBLUE))
        line = line.replace("Underfull", colorize("Underfull", CBLUE))
        found = True

    if found:
        print_warning(line)

def print_header_line():
    print(colorize("---latex_warnings output---", CREDBG))

try:
    # Ensure latex command does not cause early line breaks
    env = os.environ.copy()
    env["max_print_line"] = "10000"

    # Run command
    process = subprocess.Popen(cmd,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT,
                            env=env)

    if print_interleaved:
        print_header_line()
    output = []
    for line in iter(process.stdout.readline, b''):
        clean_line = line.decode("utf-8", "backslashreplace")
        if not print_no_raw:
            print(clean_line.strip())
        if print_interleaved:
            handle_line(clean_line)
        else:
            output.append(clean_line)

    process.stdout.close()
    returncode = process.wait()

    if not print_interleaved:
        print_header_line()
        for line in output:
            handle_line(line)

    if print_last_run:
        print(last_run_buffer)

    exit(returncode)
except KeyboardInterrupt:
    exit(1)

exit(0)
