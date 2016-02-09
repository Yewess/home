#!/usr/bin/env python

#   Application to download all alloyavenue user attachments into a directory
#   Copyright (C) 2016 Chris Evich <chris-yewess@anonomail.me>

#   This library is free software; you can redistribute it and/or
#   modify it under the terms of the GNU Lesser General Public
#   License as published by the Free Software Foundation; either
#   version 2.1 of the License, or (at your option) any later version.

#   This library is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#   Lesser General Public License for more details.

#   You should have received a copy of the GNU Lesser General Public
#   License along with this library; if not, write to the Free Software
#   Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import requests
import hashlib
import re
import getpass
import sys
import os
import os.path

url_base = 'http://www.alloyavenue.com'
url_login = '%s/vb/login.php' % url_base
url_profile = '%s/vb/profile.php' % url_base
url_dload = '%s/vb/attachment.php' % url_base

if len(sys.argv) > 1:
    login = sys.argv[1]
else:
    login = raw_input('Enter username: ')

if len(sys.argv) > 2:
    password = sys.argv[2]
else:
    password = getpass.getpass('Enter password: ')

if len(sys.argv) > 3:
    outputdir = sys.argv[3]
else:
    outputdir = raw_input('Enter destination directory: ')

def login_data(user, passwd):
    pwhash = hashlib.md5(passwd).hexdigest()
    return {'do': 'login',
            'vb_login_username': user,
            'vb_login_md5password': pwhash,
            'vb_login_md5password_utf': pwhash.encode('utf8'),
            'securitytoken': 'guest',
            's': '',
            'vb_login_password': '',
            'url': url_profile}

def log(msg):
    sys.stderr.write(msg)
    sys.stderr.flush()


params = {'do': 'login'}
sess = requests.Session()
req = sess.post(url_login, params=params, data=login_data(login, password))
req.raise_for_status()

# Need session key for entire duration
cookie_jar = req.cookies
cookie_dough = requests.utils.dict_from_cookiejar(cookie_jar)
s = cookie_dough['bb_sessionhash']
payload = {'do': 'editattachments', 'page': '1', 's': s}
req = sess.get(url_profile, params=payload)
req.raise_for_status()

mobj = re.search(r'Page (?P<startpage>\d+) of (?P<endpage>\d+)', req.content)
if not mobj:
    raise ValueError("Could not find page range in content")
last_page = int(mobj.group('endpage'))

log("Reading attachment IDs from %d pages" % last_page)
sponge = re.compile(r'.*attachmentid=(?P<attachmentid>\d+)'
                    r'.*target="attachment">(?P<filename>.*)</a>.*')
attachmentid_filenames = {}
for page_num in xrange(1, last_page + 1):
    payload = {'do': 'editattachments', 'page': str(page_num), 's': s}
    req = sess.get(url_profile, params=payload)
    req.raise_for_status()

    for mobj in sponge.finditer(req.content):
        log(".")
        attachmentid_filenames[mobj.group('attachmentid')] = mobj.group('filename')
    if not mobj:
        raise ValueError("Could not find attachments in content")

with open(os.path.join(outputdir, "attachment_filenames.csv"), 'wb') as _file:
    for attachmentid, filename in attachmentid_filenames.iteritems():
        _file.write("%s,%s\n" % (attachmentid, filename))

log("\n")
log("Found %d attachments, downloading" % len(attachmentid_filenames))
for attachmentid, filename in attachmentid_filenames.iteritems():
    payload = {'attachmentid': attachmentid, 's': s}
    req = sess.get(url_dload, params=payload, stream=True)
    req.raise_for_status()
    destpath = os.path.join(outputdir, "%s#%s" % (attachmentid,filename))
    if os.path.isfile(destpath):
        log("(overwriting %s)" % filename)
    else:
        log(".")
    with open(destpath, 'wb') as _file:
        for chunk in req:
            _file.write(chunk)
log("\n")
