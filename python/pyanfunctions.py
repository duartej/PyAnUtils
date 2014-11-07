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
