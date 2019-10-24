#synthesise-constellation.py v2.0
# by Goldtiger997, original version here
#   http://www.conwaylife.com/forums/viewtopic.php?p=68370#p68370
# v2.0 update by Arie Paap, Oct 2019
# Changelog:
#   - Use sjk component format for glider collisions
#   - Extend 3G collisions and include a subset of 4G collisions

import os
import re
import math
import golly as g

g.setrule("B3/S23")

# Files with glider collisions data. This file contains the 2G collisions
compFiles = ["3Gcols.sjk", "4Gcols.sjk"]

def main():
    apgcode = canonise()
    
    compFormat = re.compile('^([a-z0-9_]*)>([ 0-9\/-]+)>{}$'.format(apgcode))
    cols = []
    # 2G collisions
    for line in twoGcols.splitlines():
        m = compFormat.search(line)
        if m: cols.append(m.groups())
    # 3G and 4G collisions
    for cFile in compFiles:
        with open(cFile) as cF:
            for line in cF:
                m = compFormat.search(line)
                if m:
                    mg = m.groups()
                    if mg[0]:
                        g.warn('Non-empty starting target in glider collision - Not implemented')
                        continue
                    cols.append(mg)
    if cols:
        # g.note(str(cols[:20]))
        cols = [reconstruct(col[1]) for col in cols]
        # g.note(str(cols[:20]))
        Ncols = len(cols)
        g.new("solutions")
        g.show("{} collisions found".format(Ncols))
        g.setname(apgcode)
        if Ncols < 25:
            N = 5
        else:
            N = math.ceil(math.sqrt(Ncols)) + 1
        offset = 100
        for i, col in enumerate(cols):
            g.putcells(col, int((i % N) * offset), int((i // N) * offset))
        g.fit()
    else:
        g.note("No glider collisions found for that constellation. Better luck next time")

twoGcols = """
>9 -1//7 -1/>xp2_7
>9 -1/1 2//>xp2_7
>8 0/-4 3//>xp2_7
>8 0///6 -2>xs6_696
>9 -2//6 -1/>xp2_s01110szw222
>9 -3/6 0//>xp2_s01110szw222
>6 0///4 -3>xp2_s01110szw222
>7 0//3 0/>xs4_33
>9 -2//6 -2/>xs4_33
>9 -3//6 -2/>xs4_33
>8 0/-6 3//>xs4_33
>8 -3/4 1//>xs4_33
>7 0///0 -2>xs4_33
>8 -1//6 0/>xs7_2596
>9 -1//6 -1/>xs5_253
>9 -1/-2 3//>xs24_y1696z2552wgw2552zy1343
>9 -2/1 2//>xs24_y1696z2552wgw2552zy1343
>9 -1/-3 3//>xs24_y1696z2552wgw2552zy1343
>9 0//4 0/>xs24_y1696z2552wgw2552zy1343
>9 -1//8 -1/>xs24_y1696z2552wgw2552zy1343
>8 0/-3 3//>xs16_0ggydgj3zop1yd11
>9 -2//8 -2/>xs8_6996
>9 -2/2 2//>xs8_6996
>6 -1/0 2//>xs8_rr
>8 0///4 -2>xs8_33w66
>9 -2/-1 2//>xp2_ggg07y270gggzy0ey2e
>8 -1///4 -3>xp2_7zw6952
>8 -1///0 -2>xp2_7zw6952
>9 -1/-4 3//>xs12_2552zy2696
>9 -1/-5 3//>xp2_xccy3252zgw8kicz3
>9 -3/4 1//>xs7_178c
>9 -3//5 -2/>xs16_ooy033zy1ooy033
>8 0//6 0/>xp2_yj2552z696ycezy0888y41110s0111zw70ggg07yh696zzybg8gzyb121
"""

r270 = ( 0, -1,  1,  0)
r180 = (-1,  0,  0, -1)
r090 = ( 0,  1, -1,  0)

def reconstruct(gstr, stepback=2):
    """Reconstruct a pattern representing a glider set from its (canonical)
    string. The transformation is assumed to be the identity. Returns a single
    Golly cell list with all gliders at <stepback> gen prior to canonical time.
    """
    fields, at, trans_str = gstr.partition("@")
    res = []
    glider = g.parse("bo$2bo$3o") # SE
    # Process transformation
    # XXX unimplemented (but not required here)
    t, o, shift_x, shift_y = 0, "identity", 0, 0
    # Step back to separate gliders (same as Shinjuku uses for realising syntheses)
    t += stepback
    # Process glider sets
    for i, field in enumerate(gstr.split("/")):
        salvo = []
        for (time, lane) in zip(*[iter(field.split())] * 2):
            time, lane = - int(time) - t - 4, int(lane)
            dist, time = time // 4, time % 4
            salvo += g.evolve(g.transform(glider, dist, dist - lane), time)
        if   i == 1: salvo = g.transform(salvo, 0, 0, r270[0], r270[1], r270[2], r270[3]) # "rot270"
        elif i == 2: salvo = g.transform(salvo, 0, 0, r180[0], r180[1], r180[2], r180[3]) # "rot180"
        elif i == 3: salvo = g.transform(salvo, 0, 0, r090[0], r090[1], r090[2], r090[3]) # "rot90"
        res += salvo
    return g.transform(res, shift_x, shift_y)

def bijoscar(maxsteps):
    initpop = int(g.getpop())
    initrect = g.getrect()
    if (len(initrect) == 0):
        return 0
    inithash = g.hash(initrect)
    
    for i in xrange(maxsteps):
    
        g.run(1)
        
        if (int(g.getpop()) == initpop): 
        
            prect = g.getrect()
            phash = g.hash(prect)
            
            if (phash == inithash):
            
                period = i + 1
                
                if (prect == initrect):
                    return period
                else:
                    return -period 
    return -1


def canonise():
    
    p = bijoscar(6)
    
    representation = "#"
    for i in range(abs(p)):
        rect = g.getrect()
        representation = compare_representations(representation, canonise_orientation(rect[2], rect[3], rect[0], rect[1], 1, 0, 0, 1))
        representation = compare_representations(representation, canonise_orientation(rect[2], rect[3], rect[0]+rect[2]-1, rect[1], -1, 0, 0, 1))
        representation = compare_representations(representation, canonise_orientation(rect[2], rect[3], rect[0], rect[1]+rect[3]-1, 1, 0, 0, -1))
        representation = compare_representations(representation, canonise_orientation(rect[2], rect[3], rect[0]+rect[2]-1, rect[1]+rect[3]-1, -1, 0, 0, -1))
        representation = compare_representations(representation, canonise_orientation(rect[3], rect[2], rect[0], rect[1], 0, 1, 1, 0))
        representation = compare_representations(representation, canonise_orientation(rect[3], rect[2], rect[0]+rect[2]-1, rect[1], 0, -1, 1, 0))
        representation = compare_representations(representation, canonise_orientation(rect[3], rect[2], rect[0], rect[1]+rect[3]-1, 0, 1, -1, 0))
        representation = compare_representations(representation, canonise_orientation(rect[3], rect[2], rect[0]+rect[2]-1, rect[1]+rect[3]-1, 0, -1, -1, 0))
        g.run(1)
    
    if (p<0):
        prefix = "q"+str(abs(p))
    elif (p==1):
        prefix = "s"+str(g.getpop())
    else:
        prefix = "p"+str(p)
    
    return "x"+prefix+"_"+representation

# A subroutine used by canonise:
def canonise_orientation(length, breadth, ox, oy, a, b, c, d):
    
    representation = ""
    
    chars = "0123456789abcdefghijklmnopqrstuvwxyz"
    
    for v in xrange(int((breadth-1)/5)+1):
        zeroes = 0
        if (v != 0):
            representation += "z"
        for u in xrange(length):
            baudot = 0
            for w in xrange(5):
                x = ox + a*u + b*(5*v + w)
                y = oy + c*u + d*(5*v + w)
                baudot = (baudot >> 1) + 16*g.getcell(x, y)
            if (baudot == 0):
                zeroes += 1
            else:
                if (zeroes > 0):
                    if (zeroes == 1):
                        representation += "0"
                    elif (zeroes == 2):
                        representation += "w"
                    elif (zeroes == 3):
                        representation += "x"
                    else:
                        representation += "y"
                        representation += chars[zeroes - 4]
                zeroes = 0     
                representation += chars[baudot]
    return representation

# Compares strings first by length, then by lexicographical ordering.
# A hash character is worse than anything else.
def compare_representations(a, b):
    
    if (a == "#"):
        return b
    elif (b == "#"):
        return a
    elif (len(a) < len(b)):
        return a
    elif (len(b) < len(a)):
        return b
    elif (a < b):
        return a
    else:
        return b


main()
