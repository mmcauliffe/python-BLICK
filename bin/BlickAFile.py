#!/usr/bin/env python

import argparse
from blick import BlickLoader

parser = argparse.ArgumentParser(description='Add phonotactic probability to a file of phone strings.')
parser.add_argument('filename', type=open,
                   help='name of file of phone strings')
parser.add_argument('-d','--debug', action='store_true',
                    default=False,
                   help='whether or not debug mode should be activated')
parser.add_argument('-c','--constraints', action='store_true',
                    default=False,
                   help='whether or not debug mode should be activated')
parser.add_argument('-g','--grammar', type=str, choices = set(['HayesWhite','NoStress','default']), default='default',
                   help='type of grammar to be used')

args = parser.parse_args()
argdict = vars(args)
#print argdict
b = BlickLoader(debug=argdict['debug'],grammarType=argdict['grammar'])
b.assessFile(argdict['filename'].name,includeConstraints=argdict['constraints'])
