#!/usr/bin/env python
# Copyright (c) 2009-2010 Simon van Heeringen <s.vanheeringen@ncmls.ru.nl>
#
# This module is free software. You can redistribute it and/or modify it under 
# the terms of the MIT License, see the file COPYING included with this 
# distribution.

import sys
from gimmemotifs.motif import *

motifs = pwmfile_to_motifs(sys.argv[1])
for motif in motifs:
	motif.to_img(motif.id, format="PNG")
