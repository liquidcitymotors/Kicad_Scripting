#!/usr/bin/env python3
#
# Hacky script to quantize a KiCAD eeschema file back onto a standard grid
#
# Useful if someone somehow moved some components off grid and you want to clean it up.
#
# Usage is kicad-regrid.py <schematic file>
#
# Outputs <schematic file>-regrid.sch. I recommend NOT OPENING the regrid file directly in KiCAD as it assumes a new project
# with that name exists, and you'll probably get a bunch of errors. Just rename it over the original schematic
# (the script doesn't modify in place just in case you didn't back the schematic up or put it in source control or something.)
#
# Probably has lots of bugs. I've used it on two schematics from KiCAD v4.0.0 (approx).
#
# Copyright (C) 2015 Angus Gratton. BSD 3-clause License ie http://opensource.org/licenses/BSD-3-Clause
#
import sys, re, io

# how many mils do you want to quantize to? KiCAD default is 50 mils.
GRID = 50

if len(sys.argv) == 1:
    print("Usage %s <schematic file>" % (sys.argv[0],))
    schfile = input("Which schematic?")
else:
    schfile = sys.argv[1]

outfile = schfile.replace(".sch", "-regrid.sch")

if outfile == schfile:
    print("File name not a .sch file?")
    sys.exit(1)

out = open(outfile, "w")

def quantize_groups(match, idx_x, idx_y):
        x = float(match.group(idx_x))
        y = float(match.group(idx_y))
        x = int(round(x / GRID)) * GRID
        y = int(round(y / GRID)) * GRID
        return x,y

in_comp = False
is_wire = False

# schematic files can contain \r inline, so need to only match LFs
inbuf = io.TextIOWrapper(open(schfile, "rb"), newline='\n')

for line in inbuf.readlines():
    def match(expr):
        return re.match(expr, line)

    # auto-detect line endings as KiCAD uses CRLF or LF depending on platform
    end = "\n"
    if line.endswith("\r\n"):
        end = "\r\n"

    if line == "$Comp"+end:
        in_comp = True
    elif line == "$EndComp"+end:
        in_comp = False

    if in_comp:
        position = match(r"P (\d+) +(\d+)")
        if position:
            x,y = quantize_groups(position, 1, 2)
            line = "P %d %d" % (x,y)

        field = match(r'F (\d+ ".+?" .+?) +(\d+) +(\d+) +(.+)'+end)
        if field:
            x,y = quantize_groups(field, 2, 3)
            line = "F %s %d %d %s" % (field.group(1), x, y, field.group(4))

        thingy = match(r'(\t1 +)(\d+) +(\d+)'+end)
        if thingy:
            x,y = quantize_groups(thingy, 2, 3)
            line = "%s%d %d" % (thingy.group(1), x, y)

    else: # not in_comp
        label = match("Text Label (\d+) +(\d+)(.+)"+end)
        if label:
            x, y = quantize_groups(label, 1, 2)
            line = "Text Label %d %d %s" % (x,y,label.group(3))

        nc = match("NoConn ~ (\d+) +(\d+)")
        if nc:
            x, y, = quantize_groups(nc, 1, 2)
            line = "NoConn ~ %d %d" % (x,y)

        if line == "Wire Wire Line"+end:
            is_wire = True
        elif is_wire:
            wire = match("\t(\d+) +(\d+) +(\d+) +(\d+)")
            if not wire:
                raise Exception("Bad wire line %s" % line)
            x1,y1 = quantize_groups(wire, 1, 2)
            x2,y2 = quantize_groups(wire, 3, 4)
            line = "\t%d %d %d %d" % (x1,y1,x2,y2)
            is_wire = False

        conn = match("Connection ~ +(\d+) +(\d+)")
        if conn:
            x,y = quantize_groups(conn, 1, 2)
            line = "Connection ~ %d %d" % (x,y)

    if not line.endswith(end):
        line += end
    out.write(line)

print("Done! Output written to %s" % outfile)