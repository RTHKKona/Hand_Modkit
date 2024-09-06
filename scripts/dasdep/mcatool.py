#!/usr/bin/python
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

import argparse
import wave

from lib.util import *
from lib.mca import MCA


def create(filename, args):
    mca = MCA()
    mca.parse_dsp(readFile(filename.replace('wav', 'dsp')))
    log_info(mca)

    mca.mhx = args.mhx
    mca.special = args.special
    mca.loop_start = 0
    mca.loop_end = 0

    if args.loopstart:
        mca.loop_start = args.loopstart
    if args.loopend:
        mca.loop_end = args.loopend

    writeFile(filename.replace('wav', 'mca'), mca.export_mca())


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Extract and create MT Mobile Framework .mca files")
    parser.add_argument("-v", "--verbose", action="count", help="increase output verbosity")
    parser.add_argument("-ls", "--loopstart", action="store", help="set loop start sample", type=int)
    parser.add_argument("-le", "--loopend", action="store", help="set loop end sample", type=int)
    parser.add_argument("-mhx", "--mhx", action="store_true", help="create mhx compatible .mca file")
    parser.add_argument("-special", "--special", action="store_true", help="create special compatible .mca file")
    parser.add_argument("input", nargs="+", help=".mca file to create")

    args = parser.parse_args()

    enable_log(args.verbose)

    for filename in args.input:
        create(filename, args)
