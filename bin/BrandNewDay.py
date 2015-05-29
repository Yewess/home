#!/usr/bin/env python

import sys, os.path, tempfile, shutil, time, datetime

TODO_LINE = "ToDo:\n"
DID_LINE = "Did:\n"
SEP_START = "^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^\n"
SEP_END =   " ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^\n"
DATE_FMT = "%a %b %d %Y %I:%M:%S %p %Z"

def show_usage():
    print "Usage:", os.path.basename(sys.argv[0]), "<file>"
    print
    print "Where <file> is a log file to be prefixed with ToDo/Did/DateTime"
    print


def get_todo_line():
    return TODO_LINE


def get_did_line():
    return DID_LINE


def get_todo_str():
    return get_todo_line().strip()


def get_did_str():
    return get_did_line().strip()

def get_date_fmt():
    return DATE_FMT

def last_todo(logfile):
    got_todo = False
    todo_lines = []
    logfile.seek(0)
    for line in logfile:
        if line.strip() == get_did_str():
            return todo_lines
        elif got_todo:
            if len(line.strip()) > 3:
                todo_lines.append(line.rstrip())
        elif line.strip() == get_todo_str():
            got_todo = True
    return ["ERROR IN BRANDNEWDAY.PY"]

def last_date(logfile):
    logfile.seek(0)
    fmt = get_date_fmt()
    for line in logfile:
        try:
            return datetime.datetime.strptime(line.strip(), fmt).date()
        except ValueError:
            continue

def get_prefix(todo):
    fmt = get_date_fmt()
    return ("\n" # blank line
            "%s" # ToDo: includes newline
            "%s" # todo items
            "\n" # blank line
            "\n" # blank line
            "%s" # Did: includes newline
            "\n" # blank line
            "\n" # blank line
            "%s" # start line includes newline
            "%s\n" # date/time
            "%s" # end line includes newline
            "\n" # extra blank line
            % (get_todo_line(), "\n".join(todo), get_did_line(),
               SEP_START, time.strftime(fmt), SEP_END))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        show_usage()
        sys.exit(1)
    weekday = datetime.datetime.now().isoweekday()
    # 0=mon, 1=tue, 2=wed, 3=thu, 4=fri, 5=sat, 6=sun
    if weekday > 5: # After Friday
        # Silently do nothing
        sys.exit(0)
    tmp = tempfile.TemporaryFile()
    logfile = open(sys.argv[1], "rb")
    if last_date(logfile) == datetime.datetime.now().date():
        # Already updated for today, silently exit
        sys.exit(0)
    old_todo = last_todo(logfile)
    tmp.write(get_prefix(old_todo))
    logfile.seek(0)
    for line in logfile:
        tmp.write(line)
    logfile.close()
    shutil.move(sys.argv[1], sys.argv[1] + '~')
    logfile = open(sys.argv[1], "wb")
    tmp.seek(0)
    for line in tmp:
        logfile.write(line)
    logfile.close()
    tmp.close()
