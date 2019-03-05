#!/usr/bin/env python3
# (c) 2019 Marvin Löbel
# This code is licensed under MIT license (see LICENSE for details)

import sys
import os
import subprocess
import re

re_warning = re.compile("Warning|Error")
re_full = re.compile("Overfull|Underfull")
re_path = re.compile("(\\./.*?\\.(pygtex|pygstyle|tex|pdf|png|toc|sty|w18))")
re_run = re.compile("Run number [0-9]+ of rule")

todo_words = ["TODO", "FIXME", "todo", "fixme", "Todo", "Fixme"]
re_todo = re.compile("|".join(todo_words))

cmd = sys.argv[1:]

verbose = False
if len(cmd) > 0 and cmd[0] == "-V":
    verbose = True
    cmd = cmd[1:]

print_all_files = verbose
print_full_boxes = verbose

print("Wrapper script executes: {}".format(cmd))

env = os.environ.copy()
env["max_print_line"] = "10000"

process = subprocess.Popen(cmd,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT,
                           env=env)

output = []
for line in iter(process.stdout.readline, b''):
    clean_line = line.decode("utf-8", "backslashreplace")
    output.append(clean_line)
    print(clean_line.strip()),

process.stdout.close()
returncode = process.wait()

print("---Warnings and Errors ---------------------------------------------------------")

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

last_file = None
current_file = "asdf"
for line in output:
    if re_run.match(line):
        print(colorize(line.strip(), CBEIGEBG))

    def print_warning(warn_text):
        global last_file
        global current_file
        global print_all_files

        if current_file != last_file:
            if not print_all_files:
                print("File {}".format(colorize(last_file, CGREEN)))
            current_file = last_file
        print("  " + warn_text.strip())

    for m in re_path.findall(line):
        last_file_candidate = str(m[0])
        if print_all_files:
            last_file = last_file_candidate
            print("File {}".format(colorize(last_file, CGREEN)))
        if last_file_candidate.endswith(".tex"):
            last_file = last_file_candidate
            if os.path.isfile(last_file):
                with open(last_file, 'r') as f:
                    for i,line2 in enumerate(f.readlines()):
                        if re_todo.search(line2):
                            for todo_word in todo_words:
                                line2 = line2.replace(todo_word, colorize(todo_word, CVIOLET))
                            print_warning("{} on line {}: {}".format(colorize("Todo", CVIOLET), i, line2))

    if re_warning.search(line):
        line = line.replace("Warning", colorize("Warning", CYELLOW))
        line = line.replace("Error", colorize("Error", CRED))
        print_warning(line)
    if print_full_boxes and re_full.search(line):
        line = line.replace("Overfull", colorize("Overfull", CBLUE))
        line = line.replace("Underfull", colorize("Underfull", CBLUE))
        print_warning(line)

exit(returncode)
