#!/usr/bin/env
""":mod:`pyanfunctions` -- Useful functions
=====================================

.. module:: pyanfunctions
   :platform: Unix
      :synopsis: Module gathering a bunch of useful analysis-related functions
	  .. moduleauthor:: Jordi Duarte-Campderros <jorge.duarte.campderros@cern.ch>
"""

def graphtohist(graph,binning=1000):
	""".. function:: graphtohist(graph,binning=1000) -> ROOT.TH1F

	Converts a TGraph into an histogram (ROOT.TH1F), where each 
	bin-entry is averaged with the number of points available
	at x+-dx, being dx=bin size.

	:graph: The graph to be converted
	:graph type: ROOT.TGraph	
	:binning: Number of desired bins
	:binning type: float

	:return: A histogram based in the TGraph
	:rtype: ROOT.TH1F
	"""
	from ROOT import Double,TH1F
	# Extract limits to build the histo
	xmin = graph.GetXaxis().GetBinLowEdge(graph.GetXaxis().GetFirst())
	xmax = graph.GetXaxis().GetBinUpEdge(graph.GetXaxis().GetLast())
	h = TH1F(graph.GetName()+'_histo','',binning,xmin,xmax)
	#xbins = [ h.GetXaxis().GetBinLowEdge(i) for i in xrange(1,h.GetNbinsX()+2) ]
	yval = Double(0.0)
	xval = Double(0.0)
	# dict to count how many entries are pushed in the same bin, in order to
	# make an average later
	hdict = {}
	for i in xrange(graph.GetN()):
		point = graph.GetPoint(i,xval,yval)
		_hbin = h.Fill(xval,yval)
		try:
			hdict[_hbin] +=1 
		except KeyError:
			hdict[_hbin] = 1
	# Let's average the bins with more than one entry
	for b,nentries in hdict.iteritems():
		valaux = h.GetBinContent(b)
		h.SetBinContent(b,valaux/nentries)
	
	return h

def graphtohist2D(graph,binning=1000):
	""".. function:: graphtohist2D(graph,binning=1000) -> ROOT.TH2F

	2-dimensional version of the graphtohist2D function

	:graph: The graph to be converted
	:graph type: ROOT.TGraph2D	
	:binning: Number of desired bins
	:binning type: float

	:return: A histogram based in the TGraph2D
	:rtype: ROOT.TH2F

	FIXME: Possible can be absorved by the graphtohist function
	just minor addition are needed
	"""
	from ROOT import Double,TH2F
	# Extract limits to build the histo
	xmin = graph.GetXmin()
	xmax = graph.GetXmax()
	ymin = graph.GetYmin()
	ymax = graph.GetYmax()
	h = TH2F(graph.GetName()+'_histo','',binning,xmin,xmax,binning,ymin,ymax)
	#xbins = [ h.GetXaxis().GetBinLowEdge(i) for i in xrange(1,h.GetNbinsX()+2) ]
	#ybins = [ h.GetYaxis().GetBinLowEdge(i) for i in xrange(1,h.GetNbinsY()+2) ]
	yval = Double(0.0)
	xval = Double(0.0)
	zval = Double(0.0)
	# dict to count how many entries are pushed in the same bin, in order to
	# make an average later
	hdict = {}
	for i in xrange(graph.GetN()):
		point = graph.GetPoint(i,xval,yval,zval)
		_hbin = h.Fill(xval,yval,zval)
		try:
			hdict[_hbin] +=1 
		except KeyError:
			hdict[_hbin] = 1
	# Let's average the bins with more than one entry
	for b,nentries in hdict.iteritems():
		valaux = h.GetBinContent(b)
		h.SetBinContent(b,valaux/nentries)
	
	return h

def psitest(predicted,observed):
	""".. function:: psitest(predicted,observed) -> value
	Function which evaluate the amount of plausability a hypothesis has (i.e., 
	predicted) when it is found a particular set of observed data (i.e. observed). 
	The unit are decibels, and more close to 0 implies a better	reliability of 
	the hypothesis. On the other hand, getting a psi_B = X db implies that there is
	another hypothesis that it is X db better than B. So, psi function is useful to
	compare two hypothesis with respect the same observed and see which of them 
	has a psi nearest zero.

	:param predicted: the set of values which are predicted. Usually a MC histogram 
	:type predicted: numpy.array
	:param observed: the set of values which are observed; usually the data
	:type observed: numpy.array
	
	:return: the evaluation of the psi function
	:rtype: float
	
	See reference at 'Probability Theory. The logic of Science. T.E Jaynes, 
	pags. 300-305. Cambridge University Press (2003)'
	"""
	from math import log10
	# Preferably use numpy package
	try:
		from numpy import array as array
	except ImportError:
		from array import array as array

	N_total = 0
	for n in observed:
		N_total += n
	# build the frecuency array for observed
	try:
		arrobs = array([ x/N_total for x in observed ],dtype='d')
	except TypeError:
		arrobs = array('d',[ x/N_total for x in observed ])

	# Extracting info from the predicted
	N_total_pre = 0
	for n in predicted:
		N_total_pre += n
	# and build frequency array for predicted
	try:
		arrpre = array( [ x/N_total_pre for x in predicted ], dtype='d' )
	except TypeError:
		arrpre = array( 'd', [ x/N_total_pre for x in predicted ])
	
	#Consistency check: same number of measures (bins)
	if len(arrpre) != len(arrobs):
		message = "\033[31;1mpsitest ERROR\033[m Different number of elements (bins) for predicted and observed"
		raise RuntimeError(message)
	#Evaluating psi (in decibels units)
	psib = 0.0
	for i in xrange(len(arrpre)):
		if not arrpre[i] > 0.0:
			continue
		try:
			psib += arrobs[i]*log10(arrobs[i]/arrpre[i])
		except ValueError:
			continue
		except OverflowError:
			# FIXME--- CHECK WHAT IT MEANS
			continue
	
	return 10.0*N_total*psib
