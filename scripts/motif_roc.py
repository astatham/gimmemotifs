#!/usr/bin/python -W ignore
# Copyright (c) 2009-2010 Simon van Heeringen <s.vanheeringen@ncmls.ru.nl>
#
# This module is free software. You can redistribute it and/or modify it under 
# the terms of the MIT License, see the file COPYING included with this 
# distribution.

import pp
import sys
import os
from gimmemotifs.motif import pwmfile_to_motifs
from optparse import  OptionParser
import matplotlib

parser = OptionParser()
parser.add_option("-p", "--pwmfile", dest="pwmfile", help="File with pwms", metavar="FILE")
parser.add_option("-s", "--sample", dest="sample", help="Fasta formatted sample file", metavar="FILE") 
parser.add_option("-b", "--background", dest="background", help="Fasta formatted background file", metavar="FILE") 
parser.add_option("-o", "--output", dest="output", help="Name of output file (Postscript format)", metavar="FILE") 
parser.add_option("-i", "--ids", dest="ids", help="Comma-seperated list of motif ids to plot in ROC (default is all ids)", metavar="IDS") 
parser.add_option("-t", "--tiny", dest="tiny", help="Create tiny figure", default=False, action="store_true") 
parser.add_option("-l", "--nolegend", dest="nolegend", help="Don't show legend", default=False, action="store_true") 

(options, args) = parser.parse_args()

if options.tiny:
	matplotlib.use('Agg')
else:
	matplotlib.use('Agg')

import matplotlib.pyplot as plt
import matplotlib.cm as cm


from gimmemotifs.rocmetrics import * 

if not options.pwmfile or not options.sample or not options.background or not options.output:
	parser.print_help()
	exit()

def get_scores(motif, file):
	from subprocess import Popen, PIPE
	from tempfile import NamedTemporaryFile

	pwm = NamedTemporaryFile()
	pwm.write(motif.to_pwm())
	pwm.flush()
	
	cmd = "pwmscan.py -i %s -p %s -c 0.0" % (file, pwm.name)
	out = Popen(cmd, shell=True, stdout=PIPE).stdout

	vals = []
	for line in out.readlines():
		vals.append(float(line.split("\t")[5]))
	return vals

n_cpu = 8
job_server = pp.Server(n_cpu)

tiny = options.tiny

pwmfile = options.pwmfile
fg_file = options.sample
bg_file = options.background
outputfile = options.output

if options.tiny:
	if not outputfile.endswith(".png"):
		outputfile += ".png"
else:
	if not outputfile.endswith(".png"):
		outputfile += ".png"

motifs = dict([(x.id, x) for x in pwmfile_to_motifs(pwmfile)])

ids = []
if options.ids:
	ids = options.ids.split(",")
else:
	ids = motifs.keys()
	
fg_jobs = {}
bg_jobs = {}

for id in ids:
	if motifs.has_key(id):
		bg_jobs[id] = job_server.submit(get_scores, (motifs[id],bg_file,))
		fg_jobs[id] = job_server.submit(get_scores, (motifs[id],fg_file,))
	else:
		print "Wrong id: %s" % id
		sys.exit()



if options.tiny:
	fig = plt.figure(figsize=(1.1,1))
	rect = fig.patch # a rectangle instance
	ax1 = fig.add_axes([0.2, 0.15, 0.75, 0.8])
	rect = ax1.patch
	ax1.xaxis.set_ticks([0,0.5,1])
	ax1.yaxis.set_ticks([0,0.5,1])
	# plt.figure creates a matplotlib.figure.Figure instance
	for label in ax1.xaxis.get_ticklabels():
		# label is a Text instance
		label.set_fontsize(6)

	for label in ax1.yaxis.get_ticklabels():
		# label is a Text instance
		label.set_fontsize(6)

	for line in ax1.yaxis.get_ticklines():
		# line is a Line2D instance
		#line.set_color('green')
		line.set_markersize(1)
		#line.set_markeredgewidth(1)
	
	for line in ax1.xaxis.get_ticklines():
		line.set_markersize(1)
		#line.set_markeredgewidth(1)
	#plt.xlim(0,1.0)
	#plt.ylim(0,1.0)

else:
	fig = plt.figure()
	rect = fig.patch # a rectangle instance
	if not options.nolegend:
	#	ax1 = fig.add_axes([0.1,0.1,0.8,0.8])
	#else:
		ax1 = fig.add_axes([0.1,0.1,0.5,0.8])
		rect = ax1.patch
	plt.xlim(0,0.2)
	plt.ylim(0,1.0)

colors = [cm.Paired(256 / 11 * i) for i in range(11)]
for i,id in enumerate(ids):
	fg_vals = fg_jobs[id]()	
	bg_vals = bg_jobs[id]()	

	(x, y) = ROC_values(fg_vals, bg_vals) 
	
	plt.plot(x, y, color=colors[(i * 2) % 10 + 1])
	
	#print exp
	#for (xval, yval) in zip(x,y):
	#	print xval, yval

	
	#for i in range(len(x)):
	#	p = y[i] / (y[i] + x[i])
	#	r = y[i]
	#	f = (2 * p * r) / (p + r)
	#	#print p,r,f

plt.axis([0,1,0,1])
if not options.tiny:
	if not options.nolegend:
		plt.legend(ids, loc=(1.03,0.2))
	plt.xlabel("1 - Specificity")
	plt.ylabel("Sensitivity")
	plt.savefig(outputfile, format="png")
else:
	plt.savefig(outputfile, format="png")
