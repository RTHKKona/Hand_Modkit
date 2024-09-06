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

import array
import struct

from lib.util import *

class Channel:
    def __init__(self, num_samples):
        self.offset = 0
        self.buffer = array.array('h', [0]) * num_samples
        self.buffer_idx = 0
        self.adpcm_coef = [0 for i in range(16)]
        self.adpcm_history = [0, 0]

class MCA:
    magic = 'MADP'

    def __init__(self):
        self.default()

    def default(self):
        self.wave = None
        self.magic = MCA.magic
        self.version = 5
        self.loop_start = 0
        self.loop_end = 0
        self.loop_flag = False
        self.num_meta = 0

    def parse_dsp(self, dsp):
        self.num_samples  = read_dword(dsp, 0x00);
        self.num_channels = read_dword(dsp, 0x04);
        self.samplerate   = read_dword(dsp, 0x08);
        self.data_size    = read_dword(dsp, 0x0C);

        self.length = float(self.num_samples) / float(self.samplerate)

        self.channel = []
        for chan_idx in range(self.num_channels):
            self.channel.append(Channel(0))
            for i in range(16):
                self.channel[chan_idx].adpcm_coef[i] = struct.unpack_from('<h', dsp, offset=0x10 + chan_idx * 0x20 + i * 2)[0]


        data_offset = 0x10 + self.num_channels * 0x20;
        self.data = dsp[data_offset:data_offset + self.data_size]

    def export_mca(self):
        if self.data == None:
            error('no dsp data loaded')
        if self.special:
            self.version = 4


        mca = bytearray()
        if self.special:
            alloc_block(mca, 0x34)
        elif self.mhx:
            alloc_block(mca, 0x38)
        else:
            alloc_block(mca, 0x30)

        write_block(mca, 0x00, self.magic)
        write_dword(mca, 0x04, self.version)
        write_byte(mca, 0x08, self.num_channels)
        write_byte(mca, 0x0B, 1)
        write_dword(mca, 0x0C, self.num_samples)
        write_dword(mca, 0x10, self.samplerate)

        write_dword(mca, 0x14, self.loop_start)
        write_dword(mca, 0x18, self.loop_end)

        if (self.num_channels == 1):
            if not self.special:
                write_dword(mca, 0x1C, 0x68)
            else:
                write_dword(mca, 0x1C, 0x64)
        else:
            if not self.special:
                write_dword(mca, 0x1C, 0x98)
            else:
                write_dword(mca, 0x1C, 0x94)

        write_dword(mca, 0x20, self.data_size)
        write_float(mca, 0x24, self.length)
        write_dword(mca, 0x28, self.num_meta)

        if self.num_channels == 1:
            write_dword(mca, 0x2C, 0x0A0207DF)
            write_dword(mca, 0x30, 0x000d3109)
        else:
            write_dword(mca, 0x2C, 0x050407E0)
            write_dword(mca, 0x30, 0x00312009)
        write_dword(mca, 0x2C, 0x0)
        write_dword(mca, 0x30, 0x0)
        # write_dword(mca, 0x34, 0x38 + self.num_meta * 0x14 + self.num_channels * 0x30)

        alloc_block(mca, self.num_meta * 0x14)
        coef_offset = alloc_block(mca, self.num_channels * 0x30)

        for chan_idx in xrange(self.num_channels):
            for i in xrange(16):
                offset = coef_offset + chan_idx * 0x30 + i * 2
                mca[offset:offset + 2] = struct.pack('<h', self.channel[chan_idx].adpcm_coef[i])

        if not self.special:
            data_offset = alloc_block(mca, self.data_size, 0x20)
        else:
            data_offset = alloc_block(mca, self.data_size)

        if self.mhx:
            write_dword(mca, 0x34, data_offset)
        elif self.special:
            write_dword(mca, 0x2c, 0x0A0607DD)
            write_dword(mca, 0x30, 0x0006070e)
        else:
            write_dword(mca, 0x2C, data_offset)

        mca[data_offset:data_offset+self.data_size] = self.data

        return mca
