#!/bin/bash

# Display the section of an ansible log preceding a "Play Recap", containing the last failed task
set -ex
ANSIBLE_LOG="${ANSIBLE_LOG:-$1}"
TASK_PRECEEDING_FATAL_TASK=3
PLAY_TASK_RE="${PLAY_TASK_RE:-TASK.+[\\*]+}"
if [ $ANSIBLE_LOG == - ]; then # Need to search multiple times
    ANSIBLE_LOG=$(mktemp -p "" $(basename $0)_XXXXXXXX)
    trap "rm -f $ANSIBLE_LOG" EXIT
    cat - >> "$ANSIBLE_LOG"
elif [ ! -r "$ANSIBLE_LOG" ]; then
    echo "Error: Need path to ansible log file, or '-' for stdin" && exit 1
fi
# Print offset from EOF, of a non-ignored fatal task followed by PLAY_TASK_IGNORE_RE
fatal_task_eof_ofst() {
    tac "$ANSIBLE_LOG" | awk --source "
        BEGIN{ FATAL_FOUND = 0; }
        /\\.\\.\\.ignoring/{ FATAL_FOUND-- }
        /fatal\\W+.+\\W+FAILED!/{ FATAL_FOUND++ }
        /$PLAY_TASK_RE/{ if (FATAL_FOUND > 0) { print FNR; exit 0 } }
        END{ if (FATAL_FOUND <= 0) { exit -1 } else { exit 0 } }
    "
}
# Print offset from EOF, TASK_PRECEEDING_TASK-th task preceding task at line $1
pre_fatal_task_eof_ofst() {
    SKIP_LINES=$1
    [ -n $1 ] || exit 4
    tac "$ANSIBLE_LOG" | tail --lines "+$SKIP_LINES" | awk --source "
        BEGIN{ PFT = $TASK_PRECEEDING_FATAL_TASK }
        /$PLAY_TASK_RE/{ if (PFT <= 0) {print FNR + $SKIP_LINES - 1; exit 0} else PFT--; }
        END { if (PFT) {print FNR + $SKIP_LINES - 1} }
    "
}
# Print offset from line after $1, of next task, play/recap, or EOF
post_fatal_ofst() {
    SKIP_LINES=$[$1 + 2]  # One line past task
    cat "$ANSIBLE_LOG" | tail --lines "+$SKIP_LINES" | awk --source "
        BEGIN{ FOUND = 0 }
        /$PLAY_TASK_RE/{ FOUND++; print FNR - 1; exit 0 }
        /PLAY /{ FOUND++; print FNR - 1; exit 0 }
        END{ if (!FOUND) print FNR }
    "
}
LIF=$(wc -l $ANSIBLE_LOG | cut -d " " -f 1)
FATAL_TASK_EOF_OFST=$(fatal_task_eof_ofst || echo "-1")
[ $FATAL_TASK_EOF_OFST -ge 0 ] || exit 0  # no non-ignored fatal task found
PRE_FATAL_TASK_EOF_OFST=$(pre_fatal_task_eof_ofst $FATAL_TASK_EOF_OFST)
START_BOF_OFST=$[LIF - PRE_FATAL_TASK_EOF_OFST + 1]
POST_FATAL_OFST=$(post_fatal_ofst $[LIF - FATAL_TASK_EOF_OFST])
PRE_TO_FATAL_DELTA=$[(LIF - FATAL_TASK_EOF_OFST) + POST_FATAL_OFST - 4]
tail --lines "+$START_BOF_OFST" "$ANSIBLE_LOG" | head "-$PRE_TO_FATAL_DELTA"
