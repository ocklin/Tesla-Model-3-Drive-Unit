# This file is part of the stm32-sine project.
#
# Copyright (C) 2021 David J. Fiddes <D.J@fiddes.net>
# Copyright (C) 2022 Bernd Ocklin <bernd@ocklin.de>
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

import csv
import re

# takes logic files with SPI 16bit analyzer exported from Logic as CSV
infile = '/Users/bo/Downloads/spi-mcureset.csv'

meanings = [
  {"L": "Device configuration 0", "S": "DEVCFG0"},
  {"L": "Device configuration 1", "S": "DEVCFG1"},
  {"L": "Device configuration 2", "S": "DEVCFG2"},
  {"L": "Protection register", "S": "PROTCFG"},
  {"L": "Protected System configuration request 0", "S": "SYSPCFG0"},
  {"L": "Protected System configuration request 1", "S": "SYSPCFG1"},
  {"L": "Protected Watchdog configuration request 0", "S": "WDCFG0"},
  {"L": "Protected Watchdog configuration request 1", "S": "WDCFG1"},
  {"L": "Protected Functional watchdog configuration request 0", "S": "FWDCFG"},
  {"L": "Protected Window watchdog configuration request 0", "S": "WWDCFG0"},
  {"L": "Protected Window watchdog configuration request 1", "S": "WWDCFG1"},
  {"L": "System configuration 0 status", "S": "RSYSPCFG0"},
  {"L": "System configuration 1 status", "S": "RSYSPCFG1"},
  {"L": "Watchdog configuration 0 status", "S": "RWDCFG0"},
  {"L": "Watchdog configuration 1 status", "S": "RWDCFG1"},
  {"L": "Functional watchdog configuration status", "S": "RFWDCFG"},
  {"L": "Window watchdog configuration 0 status", "S": "RWWDCFG0"},
  {"L": "Window watchdog configuration 1 status", "S": "RWWDCFG1"},
  {"L": "Wake timer configuration 0", "S": "WKTIMCFG0"},
  {"L": "Wake timer configuration 1", "S": "WKTIMCFG1"},
  {"L": "Wake timer configuration 2", "S": "WKTIMCFG2"},
  {"L": "Device control request", "S": "DEVCTRL"},
  {"L": "Device control inverted request", "S": "DEVCTRLN"},
  {"L": "Window watchdog service command", "S": "WWDSCMD"},
  {"L": "Functional watchdog response command", "S": "FWDRSP"},
  {"L": "Functional watchdog response command with synchronization", "S": "FWDRSPSYNC"},
  {"L": "Failure status flags", "S": "SYSFAIL"},
  {"L": "Init error status flags", "S": "INITERR"},
  {"L": "Interrupt flags", "S": "IF"},
  {"L": "System status flags ", "S": "SYSSF"},
  {"L": "Wakeup status flags", "S": "WKSF"},
  {"L": "SPI status flags", "S": "SPISF"},
  {"L": "Monitor status flags 0", "S": "MONSF0"},
  {"L": "Monitor status flags 1", "S": "MONSF1"},
  {"L": "Monitor status flags 2", "S": "MONSF2"},
  {"L": "Monitor status flags 3", "S": "MONSF3"},
  {"L": "Over temperature failure status flags", "S": "OTFAIL"},
  {"L": "Over temperature warning status flags", "S": "OTWRNSF"},
  {"L": "Voltage monitor status", "S": "VMONSTAT"},
  {"L": "Device status", "S": "DEVSTAT"},
  {"L": "Protection status ", "S": "PROTSTAT"},
  {"L": "Window watchdog status", "S": "WWDSTAT"},
  {"L": "Functional watchdog status 0", "S": "FWDSTAT0"},
  {"L": "Functional watchdog status 1", "S": "FWDSTAT1"},
  {"L": "ABIST control0 ", "S": "ABIST_CTRL0"},
  {"L": "ABIST control1", "S": "ABIST_CTRL1"},
  {"L": "ABIST select 0 ", "S": "ABIST_SELECT0"},
  {"L": "ABIST select 1", "S": "ABIST_SELECT1"},
  {"L": "ABIST select 2", "S": "ABIST_SELECT2"},
  {"L": "Global testmode", "S": "GTM"},
  {"L": "Buck switching frequency change", "S": "TLF35584_BCK_FREQ_CHANGE"},
  {"L": "Buck Frequency spread", "S": "TLF35584_BCK_FRE_SPREAD"},
  {"L": "Buck main control", "S": "TLF35584_BCK_MAIN_CTRL"}
]

def hasOddParity(value):
    value ^= value >> 8
    value ^= value >> 4
    value ^= value >> 2
    value ^= value >> 1
    return value & 1


with open(infile, newline='') as csvfile:
    spifile = csv.reader(csvfile, delimiter=',')

    next(spifile)

    cnt = 0
    bmosi = ""
    bmiso = ""

    start = 1
    tsOffset = 0

    for row in spifile:

        # print(row)

        times = row[0]
        str = row[2]

        ts = float(times)

        if start:
          tsOffset = ts
          start = 0
          ts = 0
        else:
          ts -= tsOffset

        #r = re.match("^MOSI.\w(0x..).\w+MISO.\w(0x..)$", str)
        r = re.search("MOSI: (0x....);  MISO: (0x....)", str)
        
        bmosi = r.group(1)
        bmiso = r.group(2)

        # print(bmosi, bmiso, str)

        mosi = int(bmosi, 16) 
        miso = int(bmiso, 16) 

        # print(cnt, bmosi, bmiso)

        isWrite = 0
        rw = "R"
        if mosi & 0x8000:
          rw = "W"
          isWrite = 0x8000

        data = (mosi & 0x01FE) >> 1
        cmd  = (mosi & 0x7E00) >> 9

        cmdso = (miso & 0x7E00) >> 9
        dataso = (miso & 0x01FE) >> 1

        # print(bmosi, "{0:b}".format(mosi), hex(cmd), hex(data))
        print("[" + "{:.4f}".format(ts) + "]", bmosi, rw, 
            "0x{:02X}".format(cmd),
            "{:10s}".format(meanings[cmd]["S"]), 
            "0x{:02X}".format(data), "             # " + meanings[cmd]["L"])

        print("        ", bmiso, " ", 
            "0x{:02X}".format(cmdso), "          ",
            "0x{:02X}".format(dataso), "{:08b}b".format(dataso))


        out = isWrite | ((cmd << 9) & 0x7E00) | ((data << 1) & 0x01FE)
        if hasOddParity(out):
          out |= 0x0001

        # print(hex(out))

        print()
