#!/usr/bin/env python

#    bbsnr.py - Search and replace attachemnts with bbcode links
#    Copyright (C) 2015  Christopher Evich <chris-bbthumb@anonomail.me>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

import re
from sys import stdin
import os.path
from csv import reader

_TABLECACHE = None
_ATTACHRE = re.compile(
    r'\[ATTACH(?:=\w+)?\]\s*(?P<attachmentid>\d+)\s*\[/ATTACH\]',
    re.IGNORECASE)
_URL = 'https://spideroak.com/share/OI2HUMDSG5XTG/foundry/home/chris/Pictures/Forge/first_photos/%s'
_REPLFMT = '[URL=%s][IMG]%s[/IMG][/URL]'
_LINKFMT = '[URL=%s]%s[/URL]'

def attachtable(filepath):
    global _TABLECACHE
    if _TABLECACHE is None:
        table = {}
        with open(filepath, 'rb') as csvfile:
            for attachmentid, filename in reader(csvfile, skipinitialspace=True):
                table[int(attachmentid)] = '%d#%s' % (int(attachmentid), filename)
        _TABLECACHE = table
    return _TABLECACHE

def readentry():
    print "-------------------Block of text (empty to exit)-------------------"
    print
    return stdin.read()

def thumbnailfilename(filename):
    filename, extension = os.path.splitext(filename)
    return '%s%s%s' % (filename, '_thumbnail', extension)

def doreplacements(entry, mapping):
    def repl(mobj):
        attachmentid = int(mobj.group('attachmentid'))
        filename = mapping[attachmentid]
        imgurl = _URL % filename.replace('#', '%23')
        thumnailfile = thumbnailfilename(filename)
        if os.path.isfile(thumnailfile):
            thmurl = _URL % thumnailfile.replace('#', '%23')
            return _REPLFMT % (imgurl, thmurl)
        else:
            url = _URL % filename.replace('#', '%23')
            return _LINKFMT % (url, filename)
    return _ATTACHRE.sub(repl, entry)

def main():
    stdinput = readentry()
    while stdinput.strip():
        newentry = doreplacements(stdinput.strip(),
                                  attachtable('attachment_filenames.csv'))
        print
        print "-------------------New Entry-------------------"
        print newentry
        stdinput = readentry()

if __name__ == '__main__':
    main()
