#!/usr/bin/env python

#    bbthumb.py - Creates thumbnails of image(s), and prints BBCode links.
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

import sys
import os
from PIL import Image

def showusage():
    _msg = ("Please specify the base url (ending in a '/') and "
            "path(s) to file(s) to convert\n")
    sys.stderr.write(_msg)
    sys.exit(1)

class ThumbnailException(ValueError):
    pass

class Thumbnail(object):

    image = None
    THUMB_FACT = 0.20
    THUMB_METH = Image.ANTIALIAS
    TOKEN = 'thumbnail'
    SAVE_OPTS = { 'format': 'JPEG',
                  'quality': 25,
                  'optimize': True,
                  'progressive': True }

    def __init__(self, filepath):
        if Thumbnail.TOKEN in filepath or WebSize.TOKEN in filepath:
            raise ThumbnailException(filepath)
        self.image = Image.open(filepath)
        self.filepath = filepath

    def save(self):
        if not os.path.isfile(self.thumb_filepath):
            self.image.thumbnail(self.thumb_size, self.THUMB_METH)
            self.image.save(self.thumb_filepath, **self.SAVE_OPTS)

    @property
    def thumb_size(self):
        return (int(self.image.size[0] * self.THUMB_FACT),
                int(self.image.size[1] * self.THUMB_FACT))

    @property
    def thumb_filepath(self):
        dirname = os.path.dirname(self.filepath)
        return os.path.join(dirname, self.thumb_filename)

    @property
    def thumb_filename(self):
        filepath, extension = os.path.splitext(self.orig_filename)
        return ("%s_%s%s"
                 % (filepath, self.TOKEN, extension))

    @property
    def orig_filename(self):
        return os.path.basename(self.filepath)


class WebSize(Thumbnail):

    THUMB_FACT = 0.60
    TOKEN = 'original'
    SAVE_OPTS = { 'format': 'JPEG',
                  'quality': 50,
                  'optimize': True,
                  'progressive': True }

    @property
    def thumb_filename(self):
        return self.filepath

    @property
    def orig_filename(self):
        filepath, extension = os.path.splitext(self.thumb_filename)
        return "%s_%s%s" % (filepath, self.TOKEN, extension)

    def save(self):
        if self.filepath != self.orig_filename:
            if not os.path.isfile(self.orig_filename):
                os.rename(self.filepath, self.orig_filename)
        #else:  # preserve _original file
        super(WebSize, self).save()


def bburl_thumb(thumbnail, baseurl):
    if baseurl[-1] != '/':
        raise ValueError("Base url does not end in a '/': %s" % baseurl)
    if not baseurl.startswith("http"):
        raise ValueError("Base url does not start with http: %s" % baseurl)
    if not isinstance(thumbnail, Thumbnail):
        raise TypeError("%s is not a Thumbnail: %s"
                        % thumbnail.__class__.__name__)
    fmt = "[URL=%s][IMG]%s[/IMG][/URL]"
    i_url = "%s%s" % (baseurl, thumbnail.orig_filename)
    t_url = "%s%s" % (baseurl, thumbnail.thumb_filename)
    return fmt % (i_url, t_url)


def main(baseurl, filepaths):
    # Throw IO error if any file can't be opened
    for filepath in filepaths:
        open(filepath, "rb")
    for filepath in filepaths:
        for cls in (Thumbnail, WebSize):
            try:
                inst = cls(filepath)
            except ThumbnailException:
                continue
            inst.save()
            if cls == Thumbnail:
                msg = "\n%s\n" % bburl_thumb(inst, baseurl)
                sys.stdout.write(msg)
                sys.stdout.flush()

if __name__ == "__main__":
    if len(sys.argv) < 3:
        showusage()
    main(sys.argv[1], sys.argv[2:])
