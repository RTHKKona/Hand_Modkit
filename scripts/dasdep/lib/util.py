# Copyright 2016 dasding
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from struct import *
import os
import json
import sys
import types

class ANSI:
    RESET   = ''
    RED     = ''
    GREEN   = ''
    YELLOW  = ''
    BLUE    = ''
    MAGENTA = ''
    CYAN    = ''
    WHITE   = ''
    UNDERLINE = ''

LOGGING = 0

def color(msg, color):
    return color + msg + ANSI.RESET

def find(path, pattern):
	for e in os.listdir(path):
		file = os.path.join(path, e)
		if os.path.isdir(file):
			for subfile in find(file, pattern):
				yield subfile
		elif file.find(pattern) > -1:
			yield file


def readFile(path):
    log_loading(path)
    try:
        f = open(path, 'rb')
        c = bytearray(f.read())
        f.close()
        return c
    except IOError:
        error('Loading ' + path)


def writeFile(path, c):
    log_saving(path)
    try:
        f = open(path, 'wb')
        f.write(c)
        f.close()
    except IOError:
        error('Saving ' + path)

def readJSON(path):
    raw = str(readFile(path))
    try:
        return json.loads(raw)
    except:
        error('JSON Error')

def byteswap(data):
    s = bytearray()
    for x in xrange(0, len(data), 4):
        s += data[x:x+4][::-1]
    return s

def read_char(buf, offset):
    return chr(buf[offset])


def read_block(buf, offset, length):
    return str(buf[offset:offset + length])


def read_byte(buf, offset):
    return buf[offset]


def read_word(buf, offset):
    return unpack_from('<H', buf, offset=offset)[0]


def read_dword(buf, offset):
    return unpack_from('<I', buf, offset=offset)[0]

def read_dword_be(buf, offset):
    return unpack_from('>I', buf, offset=offset)[0]


def read_float(buf, offset):
    return unpack_from('<f', buf, offset=offset)[0]


def read_word_array(buf, offset, length):
    a = []
    for i in xrange(length):
        word = read_word(buf, offset)
        a.append(word)
        offset += 2
    return a


def read_dword_array(buf, offset, length):
    a = []
    for i in xrange(length):
        word = read_dword(buf, offset)
        a.append(word)
        offset += 4
    return a


def read_ascii_string(buf, offset, maxlength=-1):
    s = ''
    length = 0
    while length != maxlength:
        character = buf[offset + length]
        if character == 0x00:
            break
        s += chr(character)
        length += 1
    return s

def read_string(buf, offset, maxlength=-1):
    s = u''
    length = 0
    while length != maxlength:
        byte1 = read_char(buf, offset)
        byte2 = read_char(buf, offset + 1)
        if ord(byte1) == 0x00 and ord(byte2) == 0x00:
            break
        s += (byte1 + byte2).decode('utf-16le')
        offset += 2
        length += 1
    return s


def write_byte(buf, offset, value):
    buf[offset] = value


def write_word(buf, offset, value):
    buf[offset:offset + 2] = pack('<H', value)


def write_dword(buf, offset, value):
    buf[offset:offset + 4] = pack('<I', value)


def write_float(buf, offset, value):
    buf[offset:offset + 4] = pack('<f', value)


def write_block(buf, offset, value):
    buf[offset:offset + len(value)] = value


def write_word_array(buf, offset, arr):
    for idx in xrange(len(arr)):
        write_word(buf, offset + idx * 2, arr[idx])
    return buf


def write_ascii_string(buf, s):
    buf += bytearray(s + '\x00')


def write_string(buf, offset, s):
    s = s.encode('utf-16le')
    buf[offset:offset+len(s)] = s

def alloc_block(buf, length, alignment=0):
    # align blockstart
    if (alignment > 0):
        buf += '\x00' * (len(buf) % alignment)
    addr = len(buf)
    buf += '\x00' * length
    return addr


def to_json(obj):
    return json.dumps(obj, default=lambda o: o.__dict__, sort_keys=True, indent=4)


def to_csv(arr, delim='\t'):
    s = ''
    for row in arr:
        line = ''
        if isinstance(row, list):
            line = delim.join(row)
        if isinstance(row, basestring):
            line = ''.join(row)
        s += line.replace('\n', '\\n').replace('\r', '\\r') + '\n'
    return s[:-1]  # trim trailing newline

def from_csv(string):
    table = []
    for row in string.split('\n'):
        row = row.replace('\\n', '\n')
        table.append(row)
    return table

def enable_log(level):
    global LOGGING
    LOGGING = level


def log(msg):
    if LOGGING > 0:
        print(msg)


def log_info(msg):
    if LOGGING > 1:
        print(msg)

def log_warn(msg):
    print(color("Warning:", ANSI.YELLOW) + msg)


def log_saving(fn):
    log(color('Saving ', ANSI.BLUE) + fn + '...')


def log_loading(fn):
    log(color('Loading ', ANSI.YELLOW) + fn + '...')


def error(msg):
    print(color('Error ', ANSI.RED) + msg)
    sys.exit()


def dump_obj(obj):
    s = ""
    for attr in obj.__dict__:
        value = obj.__dict__[attr]
        if type(value) == list:
            pass
        else:
            s += "{0:10}: {1}\n".format(attr, value)
    return s[:-1]
