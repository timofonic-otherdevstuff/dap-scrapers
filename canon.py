"""convert country names to M49 codes."""

import dataset
import fileinput
import dedupe

db = dataset.connect('sqlite:///canon.db')
region = db['region']

def getpair(text):
    chars = '\t|,'
    for char in chars:
        if char in text:
            return [x.strip() for x in text.split(char)]
    raise RuntimeError, "getpair: found none of %r in %r."%(chars, text)

def getcode(name):
    if len(name)==3 and region.find_one(code=name.upper()):
       return name.upper()
    name = dedupe.apply_one(name)
    newname = region.find_one(name=name)
    if not newname:
        raise RuntimeError, "Name %r not found."%name
    return newname
    
def updatedb(m49=False):
    for i, line in enumerate(fileinput.input()):
        left, right = getpair(line.decode('utf-8'))
        left = dedupe.apply_one(left)  # convert to a key
        if not m49:
            try:
                right = getcode(right)  # convert to One True Name
            except RuntimeError,e:
                print e,line.strip()
                continue
        region.upsert({'name':left, 'code':right}, ['name','code'])

updatedb()