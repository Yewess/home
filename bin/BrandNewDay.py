#!/usr/bin/env python3

import sys, os, os.path, tempfile, shutil, time, datetime, re

TODO='ToDo:'
DID='Did:'
TODO_RX = re.compile(r"^{0}\s*".format(TODO))
DID_RX = re.compile(r"^{0}\s*".format(DID))
SEP_START = "^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^\n"
SEP_END =   " ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^\n"
DATE_FMT = "%a %b %d %Y %I:%M:%S %p %Z"
MAX_SEARCH = 100  # lines
DEBUG = os.environ.get('DEBUG', False)

def d(msg):
    if bool(DEBUG):
        print("{0}".format(msg))
        sys.stderr.flush()

def show_usage():
    print("Usage: {0} <file>\n".format(os.path.basename(sys.argv[0])))
    print("Where <file> is a log file to be prefixed with ToDo/Did/DateTime\n")


def get_todo_regex():
    return TODO_RX


def get_did_regex():
    return DID_RX


def get_date_fmt():
    return DATE_FMT


def last_todo(logfile):
    d("Rewinding logfile to beginning, searching for the most recent TODO block")
    logfile.seek(0)
    got_todo = False
    todo_lines = []
    _max = MAX_SEARCH
    for line in logfile:
        _max -= 1
        if _max <= 0:
            raise RuntimeError("Could not find complete TODO section in first {0} lines".format(MAX_SEARCH))
        line = str(line)
        line_no = MAX_SEARCH-_max
        if get_did_regex().search(line):
            d("Found {0} todo lines total after searching {1} lines".format(len(todo_lines), line_no))
            return todo_lines
        elif got_todo:
            if len(line.strip()) > 3:
                d("Found todo: '{0}' at line {1}".format(line.rstrip(), line_no))
                todo_lines.append(line.rstrip())
            else:
                d("Skipping blank/short todo line {0}".format(line_no))
        elif get_todo_regex().search(line):
            d("Found start of todo list at line {0}".format(line_no))
            got_todo = True
    raise RuntimeError("End of file reached while searching for complete todo block")

def last_date(logfile):
    d("Rewinding logfile to beginning, searching for the most recent date entry")
    logfile.seek(0)
    fmt = get_date_fmt()
    _max = MAX_SEARCH
    for line in logfile:
        _max -= 1
        if _max <= 0:
            raise RuntimeError("Could not find a date line in first {0} lines".format(MAX_SEARCH))
        try:
            found_date = datetime.datetime.strptime(str(line.strip()), fmt).date()
            d("Found date line {0}, parsed into {1}".format(MAX_SEARCH-_max, found_date))
            return found_date
        except ValueError:
            continue

def get_prefix(todo):
    d("Formatting new section with {0} todo lines".format(len(todo)))
    fmt = get_date_fmt()
    return ("\n" # blank line
            "{0}\n" # ToDo:
            "{1}" # todo items
            "\n" # blank line
            "\n" # blank line
            "{2}\n" # Did:
            "\n" # blank line
            "\n" # blank line
            "{3}" # start line includes newline
            "{4}\n" # date/time
            "{5}" # end line includes newline
            "\n" # extra blank line
            "".format(TODO, "\n".join(todo), DID,
                      SEP_START, time.strftime(fmt), SEP_END))

if __name__ == "__main__":
    d("Debugging enabled, parsing arguments")
    if len(sys.argv) < 2:
        show_usage()
        sys.exit(1)
    d("Checking if it's Saturday or Sunday")
    weekday = datetime.datetime.now().isoweekday()
    # 0=mon, 1=tue, 2=wed, 3=thu, 4=fri, 5=sat, 6=sun
    if weekday > 5: # After Friday
        d("Exiting, weekends are not workdays")
        sys.exit(0)
    tmp = tempfile.NamedTemporaryFile(mode="wt", encoding='utf8',
                                      prefix=os.path.basename(sys.argv[0]), suffix='.tmp')
    d("Opened temp file {0}".format(tmp.name))
    logfile = open(sys.argv[1], "rt", encoding='utf8')
    d("Opened log file {0}".format(logfile.name))
    if last_date(logfile) == datetime.datetime.now().date():
        d("File already contains entry for today, exiting.")
        sys.exit(0)
    old_todo = last_todo(logfile)
    tmp.write(get_prefix(old_todo))
    tmp.flush()
    d("New entry added, copying old file contents into temp file")
    logfile.seek(0)
    shutil.copyfileobj(logfile, tmp)
    logfile.close()
    tmp.flush()
    d("Creating backup of logfile with ~ suffix")
    shutil.copy(sys.argv[1], sys.argv[1] + '~')
    d("Movin new logfile into place")
    shutil.copy(tmp.name, sys.argv[1])
