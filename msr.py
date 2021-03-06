#!/usr/bin/env python3

import io
import json

# aarch64.json from https://raw.githubusercontent.com/NeatMonster/AMIE/master/aarch64.json

with open('aarch64.json', 'rb') as h:
    amie = json.load(h)


msrx = amie['registers']['encodings']['MSR|MRS']

msrs = {}

# example: "VBAR_EL3": ["11", "110", "1100", "0000", "000"],
#                        op0   op1    cn      cm      op2
for regname, bits in msrx.items():
    msrs[regname] = ''.join(bits)

regs = {}

# some regs have wildcard bits, represented by x's. Compute these first so that
# if there are named registers that fall within that range, they can overwrite
# them later
for regname, bits in filter(lambda x: 'x' in x[1], msrs.items()):
    # skip unnamed MSRs due to startup time increase if we add 15k registers
    if regname == 'S3_<op1>_<Cn>_<Cm>_<op2>': continue

    low = int(bits.replace('x', '0'), 2)
    high = int(bits.replace('x', '1'), 2)

    for ii in range(low, high + 1):
        regs[ii] = regname

# compute non-wildcard msrs and overwrite any earlier names
for regname, bits in filter(lambda x: 'x' not in x[1], msrs.items()):
    key = int(bits, 2)
    regs[key] = regname

# io.open to prevent windows newlines...
with io.open('src/msr.h', 'w', newline='\n') as h:
    h.write('// this file is autogenerated by msr.py\n')
    h.write('// do not edit\n')
    h.write('\n')
    h.write('#include <map>\n')
    h.write('using namespace std;\n')
    h.write('\n')
    h.write('map<uint32_t, const char *> msr = {\n');

    for key, val in regs.items():
        h.write('    {0x%06x, "%s"},\n' % (key, val))

    h.write('};\n')
