#!/usr/bin/env python
""":mod:`plotstyles` -- ROOT plot styles
=====================================

.. module:: plotstyles
   :platform: Unix
      :synopsis: define ROOT plot styles .
	  .. moduleauthor:: Jordi Duarte-Campderros <jorge.duarte.campderros@cern.ch>
"""

def squaredStyle(): 
	""".. function:: squaredStyle() -> ROOT.gStyle
	
	Return a ROOT.gStyle based in the Latinos' CMS group
	"""
	import ROOT
	
	ROOT.GloStyle = ROOT.gStyle
	
	squaredStyle = ROOT.TStyle("squaredStyle", "squaredStyle")
	ROOT.gStyle = squaredStyle
	
        #----------------------------------------------------------------------------
	# Font Legend?
	#----------------------------------------------------------------------------
        squaredStyle.SetTextFont(52)
        squaredStyle.SetTextSize(0.025)
	
	#----------------------------------------------------------------------------
	# Canvas
	#----------------------------------------------------------------------------
	squaredStyle.SetCanvasBorderMode(  0)
	squaredStyle.SetCanvasBorderSize( 10)
	squaredStyle.SetCanvasColor     (  0)
	squaredStyle.SetCanvasDefH      (600)
	squaredStyle.SetCanvasDefW      (550)
	squaredStyle.SetCanvasDefX      ( 10)
	squaredStyle.SetCanvasDefY      ( 10)
	
	#----------------------------------------------------------------------------
	# Pad
	#----------------------------------------------------------------------------
	squaredStyle.SetPadBorderMode  (   0)
	squaredStyle.SetPadBorderSize  (  10)
	squaredStyle.SetPadColor       (   0)
	squaredStyle.SetPadBottomMargin(0.16)
	squaredStyle.SetPadTopMargin   (0.08)
	squaredStyle.SetPadLeftMargin  (0.16)
	squaredStyle.SetPadRightMargin (0.16)
	
	#----------------------------------------------------------------------------
	# Frame
	#----------------------------------------------------------------------------
	squaredStyle.SetFrameFillStyle ( 0)
	squaredStyle.SetFrameFillColor ( 0)
	squaredStyle.SetFrameLineColor ( 1)
	squaredStyle.SetFrameLineStyle ( 0)
	squaredStyle.SetFrameLineWidth ( 2)
	squaredStyle.SetFrameBorderMode( 0)
	squaredStyle.SetFrameBorderSize(10)
    
	#----------------------------------------------------------------------------
	# Hist
	#----------------------------------------------------------------------------
	squaredStyle.SetHistFillColor(0)
	squaredStyle.SetHistFillStyle(1)
	squaredStyle.SetHistLineColor(1)
	squaredStyle.SetHistLineStyle(0)
	squaredStyle.SetHistLineWidth(1)
	
	#----------------------------------------------------------------------------
	# Axis
	#----------------------------------------------------------------------------
	squaredStyle.SetLabelFont  (   42, "xyz")
	#squaredStyle.SetLabelOffset(0.015, "xyz")
	squaredStyle.SetLabelSize  (0.050, "xyz")
	squaredStyle.SetNdivisions (  505, "xyz")
	squaredStyle.SetTitleFont  (   42, "xyz")
	squaredStyle.SetTitleSize  (0.050, "xyz")
	
	#  squaredStyle.SetNdivisions ( -503, "y")
	squaredStyle.SetTitleOffset(  1.4,   "x")
	squaredStyle.SetTitleOffset(  1.4,   "y")
        squaredStyle.SetTitleOffset(  1.4,   "z")
	squaredStyle.SetPadTickX   (           1)  # Tick marks on the opposite side of the frame
	squaredStyle.SetPadTickY   (           1)  # Tick marks on the opposite side of the frame
	
	#----------------------------------------------------------------------------
	# Title
	#----------------------------------------------------------------------------
	squaredStyle.SetTitleBorderSize(    0)
	squaredStyle.SetTitleFillColor (   10)
	squaredStyle.SetTitleAlign     (   23)
	squaredStyle.SetTitleFontSize  (0.045)
	squaredStyle.SetTitleX         (0.560)
        squaredStyle.SetTitleOffset    (  1.0)
	squaredStyle.SetTitleY         (0.99)
	squaredStyle.SetTitleFont(42, "")
	
	squaredStyle.SetPalette(1)
	#----------------------------------------------------------------------------
	# Stat
	#----------------------------------------------------------------------------
	#squaredStyle.SetOptStat       (1110)
	#squaredStyle.SetStatBorderSize(   0)
	#squaredStyle.SetStatColor     (  10)
	#squaredStyle.SetStatFont      (  42)
	#squaredStyle.SetStatX         (0.94)
	#squaredStyle.SetStatY         (0.91)
	return squaredStyle


def atlasStyle():
	""".. function:: AtlasStyle() -> ROOT.gStyle
	
	Return a ROOT.gStyle based in ATLAS Style
	(check for last versions in svn:)
	which is based on style from BaBar
	"""	
	import ROOT
	ROOT.GloStyle = ROOT.gStyle

	atlasStyle= ROOT.TStyle("ATLAS","Atlas style")
	ROOT.gStyle = atlasStyle

    # use plain black on white colors
	icol=0
	atlasStyle.SetFrameBorderMode(icol)
	atlasStyle.SetCanvasBorderMode(icol)
	atlasStyle.SetPadBorderMode(icol)
	atlasStyle.SetPadColor(icol)
	atlasStyle.SetCanvasColor(icol)
	atlasStyle.SetStatColor(icol)
	#atlasStyle.SetFillColor(icol)
	
	# set the paper & margin sizes
	atlasStyle.SetPaperSize(20,26)
	atlasStyle.SetPadTopMargin(0.05)
	atlasStyle.SetPadRightMargin(0.05)
	atlasStyle.SetPadBottomMargin(0.16)
	atlasStyle.SetPadLeftMargin(0.12)
	
	# use large fonts
	#font=72
	#font=42
        font=52
	#tsize=0.05
	tsize=0.025
	atlasStyle.SetTextFont(font)
	
	atlasStyle.SetTextSize(tsize)
	atlasStyle.SetLabelFont(font,"x")
	atlasStyle.SetTitleFont(font,"x")
	atlasStyle.SetLabelFont(font,"y")
	atlasStyle.SetTitleFont(font,"y")
	atlasStyle.SetLabelFont(font,"z")
	atlasStyle.SetTitleFont(font,"z")
	
	atlasStyle.SetLabelSize(tsize,"x")
	atlasStyle.SetTitleSize(tsize,"x")
	atlasStyle.SetLabelSize(tsize,"y")
	atlasStyle.SetTitleSize(tsize,"y")
	atlasStyle.SetLabelSize(tsize,"z")
	atlasStyle.SetTitleSize(tsize,"z")
	
	#use bold lines and markers
	atlasStyle.SetMarkerStyle(20)
	atlasStyle.SetMarkerSize(1.2)
	#atlasStyle.SetHistLineWidth(2.)
	atlasStyle.SetLineStyleString(2,"[12 12]") # postscript dashes
	
	#get rid of X error bars and y error bar caps
	#atlasStyle.SetErrorX(0.001)
	# get rid of error bar caps
	atlasStyle.SetEndErrorSize(0.);
	
	#do not display any of the standard histogram decorations
	atlasStyle.SetOptTitle(0)
	#atlasStyle.SetOptStat(1111)
	atlasStyle.SetOptStat(0)
	#atlasStyle.SetOptFit(1111)
	atlasStyle.SetOptFit(0)
	
	# put tick marks on top and RHS of plots
	atlasStyle.SetPadTickX(1)
	atlasStyle.SetPadTickY(1)
	
	atlasStyle.SetPalette(1)
	#ROOT.gROOT.SetStyle("Plain")
	#ROOT.gROOT.SetStyle("ATLAS")
	#ROOT.gROOT.ForceStyle()
	
	#gStyle.SetPadTickX(1)
	#gStyle.SetPadTickY(1)
	return atlasStyle

def njStyle():
	""".. function:: njStyle() -> ROOT.gStyle
	
	Return a ROOT.gStyle based in Castello-Mor and
	Duarte-Campderros mixed styles.
	"""	
	import ROOT
	ROOT.GloStyle = ROOT.gStyle
	#jl TStyle
	njStyle = ROOT.TStyle('jlStyle', "N-J Style");

	#set the background color to white
	njStyle.SetFillColor(10);
	njStyle.SetFrameFillColor(10);
	njStyle.SetCanvasColor(10);
	njStyle.SetPadColor(10);
	njStyle.SetTitleFillColor(0);
	njStyle.SetStatColor(10);

	#dont put a colored frame around the plots
	njStyle.SetFrameBorderMode(0);
	njStyle.SetCanvasBorderMode(0);
	njStyle.SetPadBorderMode(0);
	njStyle.SetLegendBorderSize(0);

	#use the primary color palette
	njStyle.SetPalette(1);
	
	#set the default line color for a histogram to be black
	njStyle.SetHistLineColor(ROOT.kBlack);
	
	#set the default line color for a fit function to be red
	njStyle.SetFuncColor(ROOT.kRed);
	
	#make the axis labels black
	njStyle.SetLabelColor(ROOT.kBlack,"xyz");
	
	#set the default title color to be black
	njStyle.SetTitleColor(ROOT.kBlack);
	 
	#set the margins
	njStyle.SetPadBottomMargin(0.18);
	njStyle.SetPadTopMargin(0.08);
	njStyle.SetPadRightMargin(0.08);
	njStyle.SetPadLeftMargin(0.17);

	#set axis label and title text sizes
	njStyle.SetLabelFont(42,"xyz");
	njStyle.SetLabelSize(0.05,"xyz");
	njStyle.SetLabelOffset(0.015,"xyz");
	njStyle.SetTitleFont(42,"xyz");
	njStyle.SetTitleSize(0.05,"xyz");
	njStyle.SetTitleOffset(1.2,"yz");
	njStyle.SetTitleOffset(1.5,"x");
	njStyle.SetStatFont(42);
	njStyle.SetStatFontSize(0.09);
	njStyle.SetTitleBorderSize(0);
	njStyle.SetStatBorderSize(0);
	njStyle.SetTextFont(52);
	
	#set line widths
	njStyle.SetFrameLineWidth(2);
	njStyle.SetFuncWidth(2);
	njStyle.SetHistLineWidth(2);
	
	#set the number of divisions to show
	njStyle.SetNdivisions(506, "xy");
	
	#turn off xy grids
	njStyle.SetPadGridX(0);
	njStyle.SetPadGridY(0);
	
	#set the tick mark style
	njStyle.SetPadTickX(1);
	njStyle.SetPadTickY(1);
	
	#turn off stats
	njStyle.SetOptStat(0);
	njStyle.SetOptFit(0);
	
	#marker settings
	njStyle.SetMarkerStyle(20);
	njStyle.SetMarkerSize(0.7);
	njStyle.SetLineWidth(2); 

	#done
	#njStyle.cd();
	#ROOT.gROOT.ForceStyle();
	#ROOT.gStyle.ls();
	return njStyle

def setpalette(name="rainbow", ncontours=999):
	""".. function::setpalette()
	
	Set a color palette from a given RGB list
	stops, red, green and blue should all be lists 
	of the same length 
	see set_decent_colors for an example"""
	from ROOT import TColor,gStyle
	from array import array
	
	if name == "gray" or name == "grayscale":
		stops = [0.00, 0.34, 0.61, 0.84, 1.00]
		red   = [1.00, 0.84, 0.61, 0.34, 0.00]
		green = [1.00, 0.84, 0.61, 0.34, 0.00]
		blue  = [1.00, 0.84, 0.61, 0.34, 0.00]
	elif name == 'darkbody':
		stops = [0.00, 0.25, 0.50, 0.75, 1.00]
		red   = [0.00, 0.50, 1.00, 1.00, 1.00]
		green = [0.00, 0.00, 0.55, 1.00, 1.00]
		blue  = [0.00, 0.00, 0.00, 0.00, 1.00]
	elif name == 'inv_darkbody':
		stops = [0.00, 0.25, 0.50, 0.75, 1.00] 
		red   = [1.00, 1.00, 1.00, 0.50, 0.00]
		green = [1.00, 1.00, 0.55, 0.00, 0.00]
		blue  = [1.00, 0.00, 0.00, 0.00, 0.00]
	elif name == 'deepsea':
		stops = [0.00, 0.34, 0.61, 0.84, 1.00]  
		red   = [0.00, 0.09, 0.18, 0.09, 0.00]
		green = [0.01, 0.02, 0.39, 0.68, 0.97] 
		blue  = [0.17, 0.39, 0.62, 0.79, 0.97] 
	else:
		# default palette, looks cool
		stops = [0.00, 0.34, 0.61, 0.84, 1.00]
		red   = [0.00, 0.00, 0.87, 1.00, 0.51]
		green = [0.00, 0.81, 1.00, 0.20, 0.00]
		blue  = [0.51, 1.00, 0.12, 0.00, 0.00]

		
	s = array('d', stops)
	r = array('d', red)
	g = array('d', green)
	b = array('d', blue)
	
	npoints = len(s)
	TColor.CreateGradientColorTable(npoints, s, r, g, b, ncontours)
	gStyle.SetNumberContours(ncontours)
