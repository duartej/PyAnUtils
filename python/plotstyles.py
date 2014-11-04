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
    squaredStyle.SetPadBottomMargin(0.20)
    squaredStyle.SetPadTopMargin   (0.08)
    squaredStyle.SetPadLeftMargin  (0.18)
    squaredStyle.SetPadRightMargin (0.05)
    
    
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
    squaredStyle.SetLabelOffset(0.015, "xyz")
    squaredStyle.SetLabelSize  (0.050, "xyz")
    squaredStyle.SetNdivisions (  505, "xyz")
    squaredStyle.SetTitleFont  (   42, "xyz")
    squaredStyle.SetTitleSize  (0.050, "xyz")
    
    #  squaredStyle.SetNdivisions ( -503, "y")
    
    squaredStyle.SetTitleOffset(  1.4,   "x")
    squaredStyle.SetTitleOffset(  1.2,   "y")
    squaredStyle.SetPadTickX   (           1)  # Tick marks on the opposite side of the frame
    squaredStyle.SetPadTickY   (           1)  # Tick marks on the opposite side of the frame
    
	#----------------------------------------------------------------------------
    # Title
    #----------------------------------------------------------------------------
    squaredStyle.SetTitleBorderSize(    0)
    squaredStyle.SetTitleFillColor (   10)
    squaredStyle.SetTitleAlign     (   12)
    squaredStyle.SetTitleFontSize  (0.045)
    squaredStyle.SetTitleX         (0.560)
    squaredStyle.SetTitleY         (0.860)
    
    squaredStyle.SetTitleFont(42, "")
    
    
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
    font=42
    tsize=0.05
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
    
    #ROOT.gROOT.SetStyle("Plain")
    #ROOT.gROOT.SetStyle("ATLAS")
    #ROOT.gROOT.ForceStyle()
    
    #gStyle.SetPadTickX(1)
    #gStyle.SetPadTickY(1)
	return atlasStyle

