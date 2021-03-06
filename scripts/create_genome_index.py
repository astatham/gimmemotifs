#!/usr/bin/env python
# Copyright (c) 2009-2010 Simon van Heeringen <s.vanheeringen@ncmls.ru.nl>
#
# This module is free software. You can redistribute it and/or modify it under 
# the terms of the MIT License, see the file COPYING included with this 
# distribution.

from gimmemotifs.genome_index import *
from gimmemotifs.config import *
from optparse import OptionParser
import sys

default_index = "/usr/share/gimmemotifs/genome_index/"
try:	
	config = MotifConfig()
	default_index = config.get_index_dir()
except:
	pass

parser = OptionParser()
parser.add_option("-i", "--indexdir", dest="indexdir", help="Index dir (default %s)" % default_index, metavar="DIR", default=default_index)
parser.add_option("-f", "--fastadir", dest="fastadir", help="Directory containing fastafiles", metavar="DIR")
parser.add_option("-n", "--indexname", dest="indexname", help="Name of index", metavar="NAME")
	
(options, args) = parser.parse_args()

if not options.fastadir or not options.indexname:
	parser.print_help()
	sys.exit(1)
	

if not os.path.exists(options.indexdir):
	print "Index_dir %s does not exist!" % (options.indexdir)
	sys.exit(1)

fasta_dir = options.fastadir
index_dir = os.path.join(options.indexdir, options.indexname)

g = GenomeIndex()
g = g.create_index(fasta_dir, index_dir)
