#!/usr/bin/env python
""":mod:`trigeffclass` -- Trigger efficiencies
==============================================

.. module:: trigeffclass
   :platform: Unix
   :synopsis: define efficiency class based in trigger path groups.
      The module also incorporate helper functions to deal with the class
.. moduleauthor:: Jordi Duarte-Campderros <jorge.duarte.campderros@cern.ch>
"""

def geteffname(trname,varname):
    """.. function::  geteffname(trname,varname)
    given a trigger name and a variable name, it returns
    an standarized efficiency name

    :param trname: the trigger path name
    :type  trname: str
    :param varname: the variable name
    :type  varname: str
    
    :return: a standar efficiency name
    :rtype:  str
    """
    name = 'eff'+varname+'_'+trname
    return name



class effsv(object):
    """.. class:: effsv
    Encapsulate a trigger efficiency defined by one or more trigger
    chains
    """
    def __init__(self,trnameslist=None,**kw):
        """.. class:: effsv(trnameslist) 
        Trigger efficiency obtained from different ntuples (see 
        ????? method). The efficiency object is stored with respect
        some variables, which allows to plot the efficiency versus
        these variables
        """
        import ROOT

        # Some configurables
        self._xbins = 50
        self._xmin  = 0.0
        self._xmax  = 300.0
        if kw.has_key('xbins'):
            self._xbins_ = kw['xbins']
        if kw.has_key('xmin'):
            self._xmin = kw['xmin']
        if kw.has_key('xmax'):
            self._xmax = kw['xmax']

        self.__var__= [ 'Dtdv', 'Dzdv', 'Drdv',   # SV with respect Primary vertex
                        'tdv', 'zdv', 'rdv'       # SV absolute position
                        ]             

        self.__extravar__ = [ 'eta','phi','betagamma',         # Kinematics of the DVs
                'nTrk4mm',                       # Number of status-1 genparticles 
                                                 # decayed from the DVs (in a 4mm radius)
                ]
        self.__xtitle__ = { 'Dtdv': 'r_{DV} [mm]' ,\
                'Dzdv': 'r_{z} [mm]',\
                'Drdv': 'radial distance [mm]',\
                'tdv': 'transverse r_{DV} [mm]', 'zdv': 'longitudinal r_{DV} [mm]', 'rdv': 'r_{DV} [mm]',\
                'eta': '#eta_{DV}', 'phi': '#phi_{DV}', 'betagamma': '#beta#gamma_{DV}',\
                'nTrk4mm': 'N_{trk}^{4mm}',\
                }
        self.__title__ = { 'Dtdv': 'Distance between PV and the DV in the XY plane' ,
                'Dzdv': 'Distance between PV and the DV in the Z-axis',
                'Drdv': 'Distance between PV and the DV',
                'tdv': 'Distance of the DV in the XY plane', 
                'zdv': 'Distance of the DV in the Z-axis',
                'rdv': 'Distance of the DV',
                }
        # Efficiencies       
        self.__effs__ = {}
        # If there is no list of triggers, there will be set later...
        if trnameslist: 
            self.__trgnames__ = trnameslist
            # Each variable is associated with a dictionary of the trigger chains availables 
            # { 'var1': { 'trpath1': TEfficiency, 'trpath2': TEfficiency, ....}, ... } 
            for i in self.__var__:
                self.__effs__[i] = dict(map(lambda x:
                    (x,ROOT.TEfficiency(geteffname(x,i),'',self._xbins,self._xmin,self._xmax)),
                      trnameslist))
                ## -- And the OR key
                self.__effs__[i]["OR"] = ROOT.TEfficiency('eff'+i+'_OR','',self._xbins,self._xmin,self._xmax)
        else:
            self.__trgnames__ = []

    def gettrgnames(self):
        """.. method:: gettrgnames() -> trgnames
        The list of the trgnames of this group oef efficiencies
        """
        return self.__trgnames__

    def fill(self,trname,varname,decission,varvalue):
        """.. method:: fill(trname,varname,decision,varvalue) 
        Fill the efficiency object defined by the 'trname' and the 
        variable 'varname' using the values 'decision' and 'varvalues'
        """
        self.__effs__[varname][trname].Fill(decission,varvalue)

    def __plot__(self,trname,varname):
        """.. method:: __plot__(trname,varname)
        draw the trigger 'trname' efficiency plot with respect to
        the variable 'varname'
        Note that this function should be called throught 
        the method 'plot'
        """
        import ROOT
        from PyAnUtils.plotstyles import atlasStyle

        lstyle = atlasStyle()
        ROOT.gROOT.SetBatch()
        
        c = ROOT.TCanvas()
        h = c.DrawFrame(self._xmin,0.0,self._xmax,1.0)
        h.SetXTitle(self.__xtitle__[varname])
        h.SetYTitle('#varepsilon_{MC}')
        h.SetTitle('[%s] %s' % (trname,self.__title__[varname]))
        h.Draw()
        self.__effs__[varname][trname].Draw("PSAME")
        c.SaveAs('eff_'+trname+'_'+varname+'.png')

    def __plotsamecanvas__(self,triglist,varname):
        """.. __plotsamecanvas__(triglist,varname)
        draw the list of trigger efficiency plots in 'triglist'
        with respect the 'varname' variable, in the same plot.
        Note that this function should be called throught 
        the method 'plot'
        """
        import ROOT
        from PyAnUtils.plotstyles import atlasStyle
        from PyAnUtils.pyanfunctions import drawlegend
        
        lstyle = atlasStyle()
        ROOT.gROOT.SetBatch()
        
        c = ROOT.TCanvas()
        h = c.DrawFrame(self._xmin,0,self._xmax,1.0)
        h.SetXTitle(self.__xtitle__[varname])
        h.SetYTitle('#varepsilon_{MC}')
        #h.SetTitle(trname)
        h.Draw()
        legend = ROOT.TLegend() 
        legend.SetBorderSize(0) 
        legend.SetTextSize(TEXTSIZE) 
        legend.SetFillColor(10) 
        legend.SetTextFont(112)
        _j = 0
        for trname in triglist:
            self.__effs__[varname][trname].SetLineColor(COLORS[_j])
            self.__effs__[varname][trname].SetMarkerStyle(20)
            self.__effs__[varname][trname].SetMarkerSize(0.5)
            self.__effs__[varname][trname].SetMarkerColor(COLORS[_j])
            self.__effs__[varname][trname].SetFillColor(COLORS[_j])
            legend.AddEntry(self.__effs__[varname][trname],trname,'PL')
            self.__effs__[varname][trname].Draw("PSAME")
            _j += 1
        drawlegend(legend,'CENTER',0.90)
        c.SaveAs('eff_GroupedTriggers'+'_'+varname+'.png')


    def plot(self,trname=None,varname=None):
        """.. method::plot([trname[,varname]])
        plot wrapper function. See '__plot__' and 
        '__plotsamecanvas__' methods.
    	"""
    	if trname and varname:
            if type(trname) is list:
                self.__plotsamecanvas__(trname,varname)
            else:
                self.__plot__(trname,varname)
        else:
            for trgname in self.__trgnames__:
                for varname in self.__var__:
                    self.__plot__(trgname,varname)


    def seteffobj(self,trname,varname,effobject):
        """.. method:: seteffof(trname,varname,effobject)
        setter to initialize a TEFficiency object given
        a trigger and a variable

        :param trname: the trigger name
        :type  trname: str
        :param varname: the variable name
        :type  varname: str
        :param effobject: the efficiency object
        :type  effobject: ROOT.TEfficiency
    	"""
    	if trname not in self.__trgnames__:
            self.__trgnames__.append(trname)
        try:
            self.__effs__[varname][trname] = effobject
        except KeyError:
            self.__effs__[varname] = { trname: effobject }

    def saverootfile(self,name):
        """.. method:: saverootfile(name)
        create a ROOT file with the TEfficiency objects stored

        :param name: the name of the root file
        :type  name: str
    	"""
    	import ROOT
    	f = ROOT.TFile.Open(name,'RECREATE')
    	for effd in self.__effs__.values():
    		for effroot in effd.values():
    			effroot.Write()
    	f.Close()

    def showresults(self):
        """.. method:: showresults
        print the results of the trigger chains PER OBJECT (DV)
        """
        effcalc = {}
        varname = self.__effs__.keys()[0]
        for trn,eff in self.__effs__[varname].iteritems():
            passed = float(eff.GetPassedHistogram().GetEntries())
            total  = float(eff.GetTotalHistogram().GetEntries())
            try:
                effcalc[trn] = float(passed)/float(total)
            except ZeroDivisionError:
                effcalc[trn] = 0.0
        maxlen = max(map(lambda x: len(x),self.__effs__[varname].keys()))
        pformat = "%"+str(maxlen)+"s:: %.3f%s"
        for trn,val in sorted(effcalc.iteritems(),key=lambda (x,y): y):
            print pformat % (trn,val*100,'%')
    
