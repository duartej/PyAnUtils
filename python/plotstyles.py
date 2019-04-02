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
    
    squaredStyle.SetPalette(53)
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
    which is based on style from BaBar
    It is actually a wrapper to the AtlasStyle 
    macro (should be located in the system FIXE HOW)
    """ 
    import ROOT
    import AtlasStyle
    
    AtlasStyle.ROOT.SetAtlasStyle()

    atlasStyle= ROOT.gStyle

    atlasStyle.SetCanvasDefH      (600)
    atlasStyle.SetCanvasDefW      (700)
    #atlasStyle.SetCanvasDefX      ( 10)
    #atlasStyle.SetCanvasDefY      ( 10)
    
    atlasStyle.SetPalette(53)
    
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

    njStyle.SetTextSize(0.025)
    #set the background color to white
    njStyle.SetFillColor(10);
    njStyle.SetFrameFillColor(10);
    njStyle.SetCanvasColor(10);
    njStyle.SetPadColor(10);
    njStyle.SetTitleFillColor(0);
    njStyle.SetStatColor(10);
    
    #----------------------------------------------------------------------------
    # Canvas
    #----------------------------------------------------------------------------
    njStyle.SetCanvasBorderMode(  0)
    njStyle.SetCanvasBorderSize( 10)
    njStyle.SetCanvasColor     (  0)
    njStyle.SetCanvasDefH      (450)
    njStyle.SetCanvasDefW      (600)
    njStyle.SetCanvasDefX      ( 10)
    njStyle.SetCanvasDefY      ( 10)
    
    #----------------------------------------------------------------------------
    # Pad
    #----------------------------------------------------------------------------
    njStyle.SetPadBorderMode  (   0)
    njStyle.SetPadBorderSize  (   8)
    njStyle.SetPadColor       (   0)
    njStyle.SetPadBottomMargin(0.15)
    njStyle.SetPadTopMargin   (0.08)
    njStyle.SetPadLeftMargin  (0.10)
    njStyle.SetPadRightMargin (0.10)
    

    #use the primary color palette
    njStyle.SetPalette(53);
    
    #set the default line color for a histogram to be black
    njStyle.SetHistLineColor(ROOT.kBlack);
    
    #set the default line color for a fit function to be red
    njStyle.SetFuncColor(ROOT.kRed);
    
    #make the axis labels black
    njStyle.SetLabelColor(ROOT.kBlack,"xyz");
    
    #set the default title color to be black
    njStyle.SetTitleColor(ROOT.kBlack);
     
    #set the margins
    #njStyle.SetPadBottomMargin(0.15);
    #njStyle.SetPadTopMargin(0.08);
    #njStyle.SetPadRightMargin(0.10);
    #njStyle.SetPadLeftMargin(0.15);

    #set axis label and title text sizes
    njStyle.SetLabelFont(52,"x");
    njStyle.SetLabelFont(52,"y");
    njStyle.SetLabelFont(52,"z");
    njStyle.SetLabelSize(0.05,"x");
    njStyle.SetLabelSize(0.05,"y");
    njStyle.SetLabelSize(0.05,"z");
    njStyle.SetLabelOffset(0.015,"x");
    njStyle.SetLabelOffset(0.015,"y");
    njStyle.SetLabelOffset(0.015,"z");
    njStyle.SetTitleFont(52,"x");
    njStyle.SetTitleFont(52,"y");
    njStyle.SetTitleFont(52,"z");
    njStyle.SetTitleSize(0.04,"x");
    njStyle.SetTitleSize(0.04,"y");
    njStyle.SetTitleSize(0.04,"z");
    njStyle.SetTitleXOffset(1.6);
    njStyle.SetTitleYOffset(1.2);
    njStyle.SetTitleOffset(1.1,"z");
    njStyle.SetStatFont(52);
    njStyle.SetStatFontSize(0.08);
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
    njStyle.SetMarkerSize(0.6);
    njStyle.SetLineWidth(2); 

    #done
    #njStyle.cd();
    #ROOT.gROOT.ForceStyle();
    #ROOT.gStyle.ls();
    return njStyle

def get_sifca_style(squared=False,stat_off=False):
    """Return a ROOT.gStyle to be used for the SIFCA group
    """
    import ROOT
    
    ROOT.GloStyle = ROOT.gStyle
    
    sifcaStyle = ROOT.TStyle("sifcaStyle", "sifcaStyle")
    ROOT.gStyle = sifcaStyle
    
    #----------------------------------------------------------------------------
    # Legend
    #----------------------------------------------------------------------------
    sifcaStyle.SetTextFont(132)
    sifcaStyle.SetTextSize(0.045)
    sifcaStyle.SetLegendBorderSize(0)
    sifcaStyle.SetLegendFillColor(0)

    
    #----------------------------------------------------------------------------
    # Canvas
    #----------------------------------------------------------------------------
    sifcaStyle.SetCanvasBorderMode(  0)
    sifcaStyle.SetCanvasBorderSize( 10)
    sifcaStyle.SetCanvasColor     (  0)
    sifcaStyle.SetCanvasDefH(550)
    sifcaStyle.SetCanvasDefW(700)
    #sifcaStyle.SetCanvasDefX      ( 10)
    #sifcaStyle.SetCanvasDefY      ( 10)
    #
    ##----------------------------------------------------------------------------
    ## Pad
    ##----------------------------------------------------------------------------
    sifcaStyle.SetPadBorderMode  (   0)
    sifcaStyle.SetPadBorderSize  (  10)
    sifcaStyle.SetPadColor       (   0)
    sifcaStyle.SetPadBottomMargin(0.14)
    sifcaStyle.SetPadTopMargin   (0.08)
    sifcaStyle.SetPadLeftMargin  (0.14)
    sifcaStyle.SetPadRightMargin (0.08)
    if squared:
        sifcaStyle.SetCanvasDefH(700)
        sifcaStyle.SetCanvasDefW(724)
        sifcaStyle.SetPadRightMargin (0.18)
    
    #----------------------------------------------------------------------------
    # Frame
    #----------------------------------------------------------------------------
    sifcaStyle.SetFrameFillStyle ( 0)
    sifcaStyle.SetFrameFillColor ( 0)
    sifcaStyle.SetFrameLineColor ( 1)
    sifcaStyle.SetFrameLineStyle ( 0)
    sifcaStyle.SetFrameLineWidth ( 2)
    sifcaStyle.SetFrameBorderMode( 0)
    sifcaStyle.SetFrameBorderSize(10)
    
    #----------------------------------------------------------------------------
    # Hist
    #----------------------------------------------------------------------------
    sifcaStyle.SetHistFillColor(0)
    sifcaStyle.SetHistFillStyle(1)
    sifcaStyle.SetHistLineColor(1)
    sifcaStyle.SetHistLineStyle(0)
    sifcaStyle.SetHistLineWidth(2)
    
    #----------------------------------------------------------------------------
    # Func
    #----------------------------------------------------------------------------
    sifcaStyle.SetFuncWidth(2)
    sifcaStyle.SetFuncColor(ROOT.kRred+1)
    
    #----------------------------------------------------------------------------
    # Title
    #----------------------------------------------------------------------------
    sifcaStyle.SetTitleBorderSize(    0)
    sifcaStyle.SetTitleFillColor (    0)
    if squared:
        sifcaStyle.SetTitleX         (0.56)
    else:
        sifcaStyle.SetTitleX         (0.5)
    sifcaStyle.SetTitleAlign     (   23)
    sifcaStyle.SetTitleFont(132)
    sifcaStyle.SetTitleSize(0.045)
    
    sifcaStyle.SetPalette(57)
    #----------------------------------------------------------------------------
    # Stat
    #----------------------------------------------------------------------------
    sifcaStyle.SetStatBorderSize(0)
    sifcaStyle.SetStatColor(0)
    if stat_off:
        sifcaStyle.SetOptStat       (0)
    
    #----------------------------------------------------------------------------
    # Axis
    #----------------------------------------------------------------------------
    #sifcaStyle.SetPadTickX   (           1)  # Tick marks on the opposite side of the frame
    #sifcaStyle.SetPadTickY   (           1)  # Tick marks on the opposite side of the frame
    sifcaStyle.SetTitleFont(132, "x")
    sifcaStyle.SetTitleFont(132, "y")
    sifcaStyle.SetTitleFont(132, "z")
    sifcaStyle.SetTitleSize(0.045,"x")
    sifcaStyle.SetTitleSize(0.045,"y")
    sifcaStyle.SetTitleSize(0.045,"z")

    sifcaStyle.SetTitleOffset(1.4,"x")
    sifcaStyle.SetTitleOffset(1.2,"y")
    sifcaStyle.SetTitleOffset(1.2,"z")
    if squared:
        sifcaStyle.SetTitleOffset(1.4,"x")
        sifcaStyle.SetTitleOffset(1.6,"y")
        sifcaStyle.SetTitleOffset(1.4,"z")

    sifcaStyle.SetLabelFont(132, "x")
    sifcaStyle.SetLabelFont(132, "y")
    sifcaStyle.SetLabelFont(132, "z")
    sifcaStyle.SetLabelSize(0.045,"x")
    sifcaStyle.SetLabelSize(0.045,"y")
    sifcaStyle.SetLabelSize(0.045,"z")

    # ---------------------------------------
    # Extra
    # ---------------------------------------    
    sifcaStyle.SetNumberContours(99)
    sifcaStyle.SetMarkerStyle(20)
    sifcaStyle.SetMarkerSize(0.7)
    
    return sifcaStyle

def setpalette(name="rainbow", ncontours=99):
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
    elif name == 'forest':
        stops = [0.00, 0.25, 0.50, 0.75, 1.00]  
        red   = [0.93, 0.70, 0.40, 0.17, 0.00]
        green = [0.97, 0.89, 0.76, 0.64, 0.43] 
        blue  = [0.98, 0.89, 0.64, 0.37, 0.17] 
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
