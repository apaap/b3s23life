#C synthesise-constellation-v2.0.py
# by Goldtiger997, original version here
#   http://www.conwaylife.com/forums/viewtopic.php?p=68370#p68370
# v2.0 update by Arie Paap, changelog:
#   - Use sjk component format for glider collisions

import os
import re
import golly as g

g.setrule("B3/S23")

# File containing glider collisions data.
compFile = "3Gcols.sjk"

def main():
    apgcode = canonise()
    
    compFormat = re.compile('^([a-z0-9_]*)>([ 0-9\/-]+)>{}$'.format(apgcode))
    cols = []
    with open(compFile) as cF:
        for line in cF:
            m = compFormat.search(line)
            if m: cols.append(m.groups())
    if cols:
        # g.note(str(cols[:20]))
        cols = [reconstruct(col[1]) for col in cols]
        # g.note(str(cols[:20]))
        g.new("solutions")
        g.show("{} collisions found".format(len(cols)))
        g.setname(apgcode)
        offset = 0
        for col in cols:
            g.putcells(col, offset, 0)
            offset += 50
        g.fit()
    else:
        g.note("No glider collisions found for that constellation. Better luck next time")

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
    # Step back to separate gliders (same as Shinjuku uses for realising syntheses 
    t += stepback
    # Process glider sets
    for i, field in enumerate(gstr.split("/")):
        salvo = []
        for (time, lane) in zip(*[iter(field.split())] * 2):
            time, lane = - int(time) - t - 4, int(lane)
            dist, time = time // 4, time % 4
            g.show('t {}, l {}, d {}'.format(time, lane, dist))
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
    
    p = bijoscar(4)
    
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
