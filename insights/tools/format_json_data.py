#!/usr/bin/env python

import json
import sys

if __name__ == '__main__':
    for line in sys.stdin:
        obj = json.loads(line)
        print "Target: {0}\nPath: {1}\nCreatedDate: {2}\nContent:".format(obj["target"], obj['path'], obj['createddate'])
        for contentline in obj['content'].splitlines():
            print "\t{0}".format(contentline.encode('utf-8'))
        print
