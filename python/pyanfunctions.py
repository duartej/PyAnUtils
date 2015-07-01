#!/usr/bin/env
""":mod:`pyanfunctions` -- Useful functions
=====================================

.. module:: pyanfunctions
   :platform: Unix
      :synopsis: Module gathering a bunch of useful analysis-related functions
	  .. moduleauthor:: Jordi Duarte-Campderros <jorge.duarte.campderros@cern.ch>
"""
TEXTSIZE=0.05

class ExtraOpt:
    """Auxiliary class to deal with optional dictionary in function,
    classes, ... (the kargs of somefunction(arg1,**kargs) ). 

    The class must be instanced with a list of 2-tuple 
    ('optarg',defaultval). The arguments will be set as attributes
    of the class, accessibles for any client. After instanciated 
    can be called as well to update his values using the 'setkwd'
    method

    ExtraOpt( validkwdtuple )

    Parameters
    ----------
    validkwdtuple: list(tuple(str,anything))
        The list of 2-tuples of the valid keywords and its default
        values. The list should be like 
            ['value1',val1),('value2',val2), ...]
        where val_i could be any type.

    Example
    -------
    The usual way to use this class is inside of a function/class which
    uses optional arguments, supposse the function 'f' accepts several
    optional arguments 'opt1' (a float) and 'opt2' (a bool). Then we
    can use this class to set the default arguments and to initialize
    the ones created by the user:

    >>> def f(somearg,**kwd):
            # Define the valid optional argumenst and their defaults
            opt = ExtraOpt( [('opt1',2.3),('opt2',False)] )
            opt.setkwd(kwd)
            ...
            # Do whatever the function should do
            ...
            # Change behaviour depending the value of the optional
            if opt.opt1 == somevalue:
                blabla

    When someone calls the function f and wants to introduce some of the
    optionals, the class deals with it

    >>> f(somearg,opt1=34)

    But if the optional doesn't exist,

    >>> f(somearg,optdoesntexist='testing')
    RuntimeError: not valid 'optdoesntexist' when calling 'f'                
    """
    def __init__(self,validkwd):
        """.. class:: extraopt(validkwdtuple)

        Auxiliary class to deal with optional dictionary in function,
        classes, ... (the kargs of somefunction(arg1,**kargs) ).

        The class must be instanced with a list of 2-tuple 
        ('optarg',defaultval). The arguments will be set as attributes
        of the class, accessibles for any client. After instanciated 
        can be called as well to update his values using the 'setkwd'
        method
        """
        self.validkwd = validkwd
        for name,initval in self.validkwd:
            setattr(self,name,initval)
    def setkwd(self,kwddict):
        """.. method::setkwd(kwddict) 

        Set the attributes of this instances with the values
        found in the kwddict dict. The keys of the dict are
        the attributes to be modified
        """
        for key,val in kwddict.iteritems():
            if key not in map(lambda (x,y): x,self.validkwd):
                raise RuntimeError("not valid '%s' when calling '%s'" %
                (key,self.__class__))
            setattr(self,key,val)

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

def getcoord(where,xwidth,ywidth,ystart=-1): 
    """..function::getcoord(where) --> (x1,y1,x2,y2) 
    Obtain the coordinates to place an rectangular
    object (TPave,TLegend, ...) placed in 'where'

    :param where: placement LEFT RIGHT or CENTER
    :type where: str
    :param xwidth: width in the x-direction
    :type xwidth: float
    :param ywidth: width in the y-direction
    :type ywidth: float
    :param ystart: y higher position [fixed at 1.02 per default]
    :type ystar: float

    :return: the four vertices of the rectangle (x1,y1,x2,y2)
    :rtype: tuple(float)
    """ 
    if where == "LEFT": 
        x1 = 0.22  
    elif where == "RIGHT": 
        x1 = 0.56#0.60   
    elif where == "CENTER": 
        x1 = (1.0-xwidth-2.0*0.22)/2.0+0.22 
    else: 
        message = "\033[31mgetcoord ERROR\033[m Not defined coordinates at '%s'" % where 
        raise RuntimeError(message) 
    
    x2 = x1+xwidth 
    if ystart == -1: 
        y2 = 1.02 
    else: 
        y2 = ystart-0.005 
    y1 = y2-ywidth 
    
    return (x1,y1,x2,y2) 

def drawlegend(legend,where,ystart,**kwd):
    """..function:: drawlegend(legend,where,ystart)
    Draw a TLegend in the position defined by where (see getcoor
    function) and with the y-position starting at ystart
    
    Parameters
    ----------
    legend: ROOT.TLegend
        the legend to draw
    where: str
        placement LEFT, RIGHT or CENTER
    ystart: float
        where to place the upper y coordinate
    textlength: str, optional
        the maximum length of the text, giving
        the x-width of the legend's box [Default: 0.12]
    """
    textlength=0.12
    if kwd.has_key("textlength"):
        textlength = float(kwd['textlength'])
    # Extract the maximum available lenght
    maxsize=0.0
    for i in legend.GetListOfPrimitives():
    	maxsize = max(len(i.GetLabel()),maxsize)
    # - Maximum 3 Columns, distribute the entries
    nrows = legend.GetNRows()
    #if nrows >= 5:
    #	legend.SetNColumns(3)
    #	textlength=0.22 # (Just to fill all the xwidth available 0.66)
    #	where = "LEFT"
    y1width = TEXTSIZE*legend.GetNRows()
    xwidth  = textlength*legend.GetNColumns()
    x1,y1,x2,y2 = getcoord(where,xwidth,y1width,ystart)
    legend.SetX1NDC(x1)
    legend.SetY1NDC(y1)
    legend.SetX2NDC(x2)
    legend.SetY2NDC(y2)
    legend.Draw()


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
