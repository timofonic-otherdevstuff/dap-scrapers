"""convert country names to M49 codes."""

import dataset
import fileinput
import dedupe
import logging
import sys

db = dataset.connect('sqlite:///canon.db')
region = db['region']

log = logging.getLogger("canon")
log.addHandler(logging.StreamHandler())
log.level = logging.WARN

def getpair(text):
    """cheap and dirty CSV parsing"""
    chars = '\t|,'
    for char in chars:
        if char in text:
            return [x.strip() for x in text.split(char)]
    raise RuntimeError, "getpair: found none of %r in %r."%(chars, text)

def canonicalise(name):
    """see if there's a matching row in the DB already, give answer"""
    if len(name)==3 and region.find_one(code=name.upper()):
       return name.upper()
    name = dedupe.apply_one(name)
    newname = region.find_one(name=name)
    if not newname:
        log.warn("Name %r not found."%name)
        return None
    return newname
    
def updatedb(m49=False):
    """update db with data from a file in a CSV-like format"""
    for i, line in enumerate(fileinput.input()):
        left, right = getpair(line.decode('utf-8'))
        left = dedupe.apply_one(left)  # convert to a key
        if not m49:
            right = canonicalise(right)  # convert to One True Name
        if right is not None:
            region.upsert({'name':left, 'code':right}, ['name','code'])

#updatedb()

def _ignore():
    if len(sys.argv) > 1:
        m49 = "m49" in sys.argv[1]
        print "parsing ", sys.argv[1:]
        updatedb()
    else:
        for i in open("who-nasty.out").read().split('\n'):
            try:
                canonicalise(i)
            except Exception, e:
                print e
