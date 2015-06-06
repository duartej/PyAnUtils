#!/usr/bin/env python
""":mod:`trigeffclass` -- Trigger efficiencies
==============================================

.. module:: trigeffclass
   :platform: Unix
   :synopsis: define efficiency class based in trigger path groups.
      The module also incorporate helper functions to deal with the class
.. moduleauthor:: Jordi Duarte-Campderros <jorge.duarte.campderros@cern.ch>
"""
from abc import ABCMeta
from abc import abstractmethod

# DEPRECATED
#def geteffname(trname,varname):
#    """.. function::  geteffname(trname,varname)
#    given a trigger name and a variable name, it returns
#    an standarized efficiency name
#
#    :param trname: the trigger path name
#    :type  trname: str
#    :param varname: the variable name
#    :type  varname: str
#    
#    :return: a standar efficiency name
#    :rtype:  str
#    """
#    name = 'eff'+varname+'_'+trname
#    return name
# Pseudo ROOT colors
kBlack=1
kRed=632
kGreen=416
kAzure=860
kCyan=432
kOrange=800

COLORS = [ kBlack, kRed+2, kAzure+3,kCyan-2,kGreen-2, kOrange-2, \
		 kRed-3, kAzure-3, kCyan+4, kGreen+4, kOrange+7 ]
TEXTSIZE = 0.03

DEFAULTBINNING = { 'eta': (100,-5,5), 'phi': (100,-3.1415,3.1415),
    'betagamma': (100,0,20),
    'nTrk4mm':   (41,0,40),
    'genpfromdv_pdgId':   (1000,-2300,2300),
    'genpfromdv_eta': (100,-5,5), 'genpfromdv_phi': (100,-3.1415,3.1415),
    'genpfromdv_pt':  (100,0,200),
    'genpfromdv_vx':  (200,-300,300), 'genpfromdv_vy': (200,-300,300), 'genpfromdv_vz': (200,-1500,1500),
    'dv_X':  (200,-300,300), 'dv_Y': (200,-300,300), 'dv_Z': (200,-1500,1500),
    'vx_LSP':  (200,-0.8,0.8), 'vy_LSP': (200,-0.8,0.8), 'vz_LSP': (200,-200,200),
    'nTrk':  (101,0,100), 
    'Dtdv': (50,0,300),
    'Drdv': (50,0,300),
    'Dzdv': (50,0,300),
    'tdv': (50,0,300),
    'zdv': (50,0,300),
    'rdv': (50,0,300),
    }

DEFAULTXTITLE = { 'Dtdv': 'XY_{DV} [mm]' ,
                'Dzdv': 'z_{DV} [mm]',
                'Drdv': 'radial distance [mm]',
                'tdv': 'transverse r_{DV} [mm]', 'zdv': 'longitudinal r_{DV} [mm]', 'rdv': 'r_{DV} [mm]',
                'eta': '#eta_{DV}', 'phi': '#phi_{DV}', 'betagamma': '#beta#gamma_{DV}',
                'dv_X': 'DV v_{x} [mm]', 'dv_Y': 'DV v_{y} [mm]', 'dv_Z': 'DV v_{z} [mm]',
                'vx_LSP': 'PV v_{x} [mm]', 'vy_LSP': 'PV v_{y} [mm]', 'vz_LSP': 'PV v_{z} [mm]',
                'nTrk': 'DV N_{trk}', 
                'nTrk4mm': 'status-1 N_{trk}^{4mm}',
                'pdgId_g': 'pdgID_{<4mm}',
                'eta_g': '#eta^{<4mm}', 'phi_g': '#phi^{<4mm}', 'pt_g': 'p_{t}^{<4mm} [GeV]',
                'vx_g':  'prod v_{x}^{<4mm} [mm]', 
                'vy_g': 'prod v_{y}^{<4mm} [mm]', 
                'vz_g': 'prod v_{z}^{<4mm} [mm]', 
                'genpfromdv_pdgId': 'pdgID_{<4mm}',
                'genpfromdv_eta': '#eta^{<4mm}', 
                'genpfromdv_phi': '#phi^{<4mm}', 
                'genpfromdv_pt':  'p_{t}^{<4mm} [GeV]',
                'genpfromdv_vx':  'prod v_{x}^{<4mm} [mm]', 
                'genpfromdv_vy': 'prod v_{y}^{<4mm} [mm]', 
                'genpfromdv_vz': 'prod v_{z}^{<4mm} [mm]', 
                }

def parsegrouptriggers(linestr):
    """.. function:: parsegrouptriggers(linestr) -> [ 'OR_TR1_TR2_...', 'OR_TRX_...']

    The linestr contains the triggers which want to be OR. They are grouped 
    between semi-colons ":"  and each trigger in the group should be separated by 
    a comma ","
    The function returns a list with the trigger grouped in a strings
    """
    trgroup = {}
    
    groups = linestr.split(":")
    for g in groups:
        trnames = g.split(",")
        _pre = 'OR'
        trlist = []
        for tr in trnames:
            _pre+= ('_'+tr)
            trlist.append(tr)
        trgroup[_pre] = trlist
    #FIXME:: Check the syntax
    return trgroup


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
        if kw.has_key('extravareff'):
            self.extravareff=kw['extravareff']
        else:
            self.extravareff=False
        
        self.grouptriggersOR = {}
        if kw.has_key('triggersOR') and kw['triggersOR']:
            # Just doing the OR of these selected triggers
            self.grouptriggersOR = parsegrouptriggers(kw['triggersOR'])
        else:
            self.grouptriggersOR["OR"] = None


        self.__var__= [ 'Dtdv', 'Dzdv', 'Drdv',   # SV with respect Primary vertex
                        'tdv', 'zdv', 'rdv'       # SV absolute position
                        ]             

        self.__extravars__ = [ 'eta','phi','betagamma',         # Kinematics of the DVs
                'nTrk4mm']#,                       # Number of status-1 genparticles 
                                                 # decayed from the DVs (in a 4mm radius)
                #'pdgId_g',                       # Gen particles inside the 4mm radius
                #'eta_g','phi_g','pt_g',          # Kinematics of these particles
                #'vx_g','vy_g','vz_g',
                #]
        # bins, xmin,xmax 
        self.__defaults__ = DEFAULTBINNING

        self.__xtitle__ = DEFAULTXTITLE
        
        self.__title__ = { 'Dtdv': 'Distance between PV and the DV in the XY plane' ,
                'Dzdv': 'Distance between PV and the DV in the Z-axis',
                'Drdv': 'Distance between PV and the DV',
                'tdv': 'Distance of the DV in the XY plane', 
                'zdv': 'Distance of the DV in the Z-axis',
                'rdv': 'Distance of the DV',
                'eta': 'pseudo-rapidity of LSP',
                'phi': 'azimuthal angle of LSP',
                'betagamma': '#beta#gamma of LSP',
                'nTrk4mm': 'number of tracks (undecayed status-1) around < 4mm of DV',
                }
        # Efficiencies       
        self.__effs__ = {}
        # If there is no list of triggers, there will be set later...
        if trnameslist: 
            self.__trgnames__ = trnameslist
            # Each variable is associated with a dictionary of the trigger chains availables 
            # { 'var1': { 'trpath1': TEfficiency, 'trpath2': TEfficiency, ....}, ... } 
            for i in self.__var__:
                _xbins= self.__defaults__[i][0]
                _xmin = self.__defaults__[i][1]
                _xmax = self.__defaults__[i][2]
                self.__effs__[i] = dict(map(lambda x:
                    (x,ROOT.TEfficiency(self.geteffname(x,i),'',_xbins,_xmin,_xmax)),
                            trnameslist))
                ## -- And the ORs keys
                for orkey in self.grouptriggersOR.keys():
                    self.__effs__[i][orkey] = ROOT.TEfficiency('eff'+i+'_'+orkey,'',_xbins,_xmin,_xmax)
            # Could be put in the previous for
            if self.extravareff:
                for i in self.__extravars__:
                    _bins = self.__defaults__[i][0]
                    _xmin = self.__defaults__[i][1]
                    _xmax = self.__defaults__[i][2]
                    self.__effs__[i] = dict(map(lambda x:
                        (x,ROOT.TEfficiency(self.geteffname(x,i),'',_bins,_xmin,_xmax)),
                        trnameslist))
                    ## -- And the ORs keys
                    for orkey in self.grouptriggersOR.keys():
                        self.__effs__[i][orkey] = ROOT.TEfficiency('eff'+i+'_'+orkey,'',_bins,_xmin,_xmax)
        else:
            self.__trgnames__ = []

        self.plotsuffix = '.png'

    def getgroupoftriggers(self,deftr):
        """.. method:: getgroupoftriggers(deftr) -> { 'OR_TR1_TR2...': [tr1,tr2,...] ,  ..}

        Return a dict with the group of OR which were defined at creation time
        (see parsegrouptriggers function).
        If the key OR is found means that all the triggers should be used, then the
        argument deftr is getting this info
        """
        if self.grouptriggersOR.has_key("OR"):
            return { 'OR': deftr }

        return self.grouptriggersOR


        
    def gettrgnames(self):
        """.. method:: gettrgnames() -> trgnames
        The list of the trgnames of this group oef efficiencies
        """
        return self.__trgnames__
    
    @staticmethod
    def geteffname(trname,varname):
        """.. function:: geteffname(trname,varname) -> effname
        given a trigger name and a variable name, it returns
        an standarized efficiency name

        :param trname: the trigger path name
        :type  trname: str
        :param varname: the variable name
        :type  varname: str
        
        :return: canonical efficiency name
        :rtype:  str
        """
        name = 'eff%s_%s' % (varname,trname)
        return name
    
    @staticmethod
    def gettriggernamefrom(fullname):
        """.. method::  gettriggernamefrom(fullname) -> triggername
        from a canonical efficiency name extracts the
        trigger path name

        :param trname: the canonical trigger efficiency name
        :type  trname: str
        
        :return: the trigger path name
        :rtype:  str
        """
        return fullname.split('eff'+effsv.getvarnamefrom(fullname)+'_')[-1]

    @staticmethod
    def getvarnamefrom(fullname):
        """.. method:: getvarnamefrom(fullname) -> varname
        from a canonical efficiency name extracts the
        variable name

        :param fullname: the canonical trigger efficiency name
        :type  fullname: str
        
        :return: the variable name
        :rtype:  str
        """
        return fullname.split('eff')[-1].split('_')[0]


    def fill(self,trname,varname,decission,varvalue):
        """.. method:: fill(trname,varname,decision,varvalue) 
        Fill the efficiency object defined by the 'trname' and the 
        variable 'varname' using the values 'decision' and 'varvalues'
        """
        # Just filling variables pre-defined
        if varname not in self.__effs__.keys():
            return
        self.__effs__[varname][trname].Fill(decission,varvalue)
    
    def setplotsuffix(self,suffix):
        """.. method:: setplotsuffix(suffix) 
        set the plot output format, which is .png per default
        """
        self.plotsuffix = suffix
        if suffix.find('.') == -1:
            self.plotsuffix = '.'+suffix

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
        lstyle.cd()
        ROOT.gROOT.SetBatch()
        
        _xmin=self.__defaults__[varname][1]
        _xmax=self.__defaults__[varname][2]
        c = ROOT.TCanvas()
        h = c.DrawFrame(_xmin,0.0,_xmax,1.0)
        h.SetXTitle(self.__xtitle__[varname])
        h.SetYTitle('#varepsilon_{MC}')
        h.SetTitle('[%s] %s' % (trname,self.__title__[varname]))
        h.Draw()
        self.__effs__[varname][trname].Draw("PSAME")
        c.SaveAs('eff_'+trname+'_'+varname+self.plotsuffix)

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
        lstyle.cd()
        ROOT.gROOT.SetBatch()
        
        _xmin=self.__defaults__[varname][1]
        _xmax=self.__defaults__[varname][2]
        c = ROOT.TCanvas()
        h = c.DrawFrame(_xmin,0,_xmax,1.0)
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
            # XXX - PROVISIONAL PATCH: To be deleted
            # converting trigger names to displaced vertex triggers
            if trname.find('OR') == 0:
                legentryname = 'OR'
            elif trname.find('_L') != -1:
                # Note format HLT_JETPART_LEVEL1PART
                legentryname = 'HLT_DV_'+trname.split('_')[-1]
            else:
                legentryname = trname
            legend.AddEntry(self.__effs__[varname][trname],legentryname,'PL')
            self.__effs__[varname][trname].Draw("PSAME")
            _j += 1
        drawlegend(legend,'RIGHT',0.40)
        c.SaveAs('eff_GroupedTriggers'+'_'+varname+self.plotsuffix)


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


class storedeff(object):
    """ ..class:: storedeff
    abstract class to implement the retrieval of a MC-info and trigger root file.
    The concrete classes should implement the relative methods dependents of the
    ntuple obtainer (RPVMCInfoTree/RPVMCTruthHist/...)
    Virtual methods:
     * gettreechain
     * getmctruthinfo
     * setuptree
    """
    __metaclass__ = ABCMeta

    def __init__(self,rootfiles,chainname):
        """ ..class:: storedeff
        abstract class to implement the retrieval of a MC-info and trigger root file.
        The concrete classes should implement the relative methods dependents of the
        ntuple obtainer (RPVMCInfoTree/RPVMCTruthHist/...)
        Virtual methods:
         * gettreechain
         * getmctruthinfo
         * setuptree
        """
        import ROOT
        import os
        
        self.rootfiles = rootfiles
        
        self.tree = ROOT.TChain(chainname)
        print "TChain '%s' created" % chainname
        print "Adding %i root files to the tree" % len(self.rootfiles)
        for i in sorted(self.rootfiles):
            self.tree.AddFile(i)
        
        self.plotsactivated = False
        self.nentries   = self.tree.GetEntries()
        # Setting up how-many DV are:
        self.tree.GetEntry(0)
        self.llpindices = xrange(len(self.tree.dv_X))
    
    def activate_plots(self,varname=None,**kw):
        """.. method:: activate_plots(varname=None[,bins=bins,xmin=xmin,xmax=xmax]) 
        The varname plot is activated and will be filled in the entry loop
        of the tree. If there is no varname, it is going to be used all of them 
        (content of the __vars__ datamember). If varname is a tuple of str, a
        TH2F is going to be created, while if is a str or a list of str, a TH1F
        foe each variable is created

        :param varname: the name of the variable(s) to activate
        :type  varname: str/tuple(str,str)/list(str)
        :param bins: number of bins
        :type  bins: int
        :param xmin: the lower x-range
        :type  xmin: float
        :param xmax: the higher x-range
        :type  xmax: float
        ...
        """
        import ROOT

        try:
            _d = self._hist2d
        except AttributeError:
            self._hist2d = {}
        try:
            _dd = self._hist1d
        except AttributeError:
            self._hist1d = {}
        
        varnamelist = []
        
        if not varname:
            varnamelist = self.__vars__
        elif type(varname) is str:
            varnamelist = [varname]
        elif type(varname) is tuple:
            self._hist2d[varname[0]+':'+varname[1]] = ROOT.TH2F(varname[0]+'_'+varname[1],
                    varname[0]+' vs. '+varname[1],DEFAULTBINNING[varname[0]][0],
                    DEFAULTBINNING[varname[0]][1],DEFAULTBINNING[varname[0]][2],
                    DEFAULTBINNING[varname[1]][0],
                    DEFAULTBINNING[varname[1]][1],DEFAULTBINNING[varname[1]][2])

        for var in varnamelist:
            self._hist1d[var] = ROOT.TH1F(var,var,DEFAULTBINNING[var][0],
                    DEFAULTBINNING[var][1],DEFAULTBINNING[var][2])

        self.plotsactivated=True

    def plots(self,plotsuffix='.png'):
        """.. method:: plots()
        draw the activated plots
        """
        if not self.plotsactivated:
            return

        import ROOT
        from PyAnUtils.plotstyles import atlasStyle,setpalette

        lstyle = atlasStyle()
        lstyle.cd()
        ROOT.gROOT.SetBatch()
        setpalette('darkbody')
        
        for name,th1 in self._hist1d.iteritems():
            c = ROOT.TCanvas()
            xtitle = DEFAULTXTITLE[name]
            th1.SetXTitle(xtitle)
            width = th1.GetBinWidth(1)
            if len(xtitle.split('[')) == 1:
                unit = ''
            else:
                unit  = "["+xtitle.split('[')[-1].replace(']','').strip()+"]"
            th1.SetYTitle('Events/(%.1f %s)' % (width,unit) )
            th1.Draw()
            c.SaveAs('extraplot_'+name+plotsuffix)
        
        for names,th2 in self._hist2d.iteritems():
            c = ROOT.TCanvas()
            name1 = names.split(':')[0]
            name2 = names.split(':')[1]
            xtitle = DEFAULTXTITLE[name1]
            ytitle = DEFAULTXTITLE[name2]
            th2.SetXTitle(xtitle)
            th2.SetYTitle(ytitle)
            th2.Draw("COLZ")
            c.SaveAs('extraplot_'+name1+'_'+name2+plotsuffix)
    

    @abstractmethod
    def gettriggersnames(self):
        raise NotImplementedError("Class %s doesn't implement "\
                "gettriggersname()" % (self.__class__.__name__))

    @abstractmethod
    def setuptree(self,triggerbr):
        raise NotImplementedError("Class %s doesn't implement "\
                "setuptree()" % (self.__class__.__name__))

    @abstractmethod
    def getmctruthinfo(self):
        raise NotImplementedError("Class %s doesn't implement "\
                "getmctruthinfo()" % (self.__class__.__name__))
    
    def get(self,variable):
        """
        """
        return getattr(self.tree,variable)

    def getentry(self,i):
        """
        """
        _d = self.tree.GetEntry(i)
        if self.plotsactivated:
            for name,thf1 in self._hist1d.iteritems():
                for k in self.llpindices:
                    thf1.Fill(getattr(self.tree,name)[k])

            for name,thf2 in self._hist2d.iteritems():
                var1 = name.split(':')[0]
                var2 = name.split(':')[1]
                for k in self.llpindices:
                    thf2.Fill(getattr(self.tree,var1)[k],getattr(self.tree,var2)[k])


    def getentries(self):
        """
        """
        return self.nentries

    def filleff(self,trgdecdict,effsvinst,ignorematching=False,**kw):
        """..function:: filleff(trgdecdic,effsvinst[,ignoremathcing=True]) 

        The function fills the efficiencies with respect the variables 
        obtained with the 'getmctruthinfo' method. The datamember 
        '%TRNAME_isJetRoiMatched' takes into account if any RoI was matched
        with any MC-Truth particle coming from the DV. The datamember is a
        vector of ints, where each index corresponds to one DV (MC-Truth).
        Therefore, efficiencies are calculated as follows:
          * Check if any MC-particle coming from the DV has matched with
          the trigger RoI (isJetRoiMatched[i] outcome for the i-DV)  or not.
          The efficiency is evaluated as an AND (OR) if 'ignorematching'
          argumetn is set to False (True) of the matching checked and the trigger
          decision
    
        :param trgdecdic: dictionary with the trigger names and trigger 
                          decision per event
        :type  trgdecdic: dict(str: bool}
        :param effsvinst: efficiency class instances
        :type  effsvinst: class effsv
        :param ignorematching: argument to control if the matching betweem RoI's 
                               trigger objects and the MC-Truth info hould be
                               performed
        :type  ignorematching: bool                           
        """
        if kw.has_key('extra'):
            extra = True
        else:
            extra = False
        # Just getting the group of triggers
        triggersOR = effsvinst.getgroupoftriggers(trgdecdict.keys())

        sv = self.getmctruthinfo(extra)
        # Getting the OR of all  the triggers
        for orkey,grouptrlist in triggersOR.iteritems():
            trigdecOR = False
            for (tragname,trgdec) in \
                    filter(lambda (trname,wh): trname in grouptrlist,trgdecdict.iteritems()):
                trigdecOR = (trigdecOR or trgdec)
            # And adding it to the trgdecdict
            #trgdecdict["OR"] = trigdecOR
            trgdecdict[orkey] = trigdecOR
        # Filling the efficiencies
        matchvar = "%s_isJetRoiMatched"
        presentvar = "%s_isJetRoiPresent"
        # obtaining the trigger decision in the event.
        for trgname,trgdec in trgdecdict.iteritems():
            i=0
            # Obtaining the MC-info related with the i-DV
            for svinfodict in sv:
                try:
                    ispresent = bool(getattr(self.tree,presentvar%trgname)[0])
                except AttributeError:
                    # The OR case!!
                    ispresent=True
                    pass
                if ispresent:
                    try:
                        # Now checking if the i-DV was matched with any TE
                        # in order to consider not to bias the variable of the
                        # DV MCTruth. The problem with using non-matching objects
                        # relies in the fact you're not sure what MC object is the
                        # responsible of the trigger decision, so you are biasing your 
                        # efficiency
                        try:
                            ismatched = bool(getattr(self.tree,matchvar%trgname)[i])
                        except AttributeError:
                            # Backward compatibility
                            ismatched = True
                        ismatched = (ismatched or ignorematching)
                        if not ismatched:
                            continue
                    except AttributeError:
                        # Just controlling the OR-cases
                        ismatched =1
                else:
                    # Is not present is going to be considered as a fail decision
                    ismatched=False
                # Filling all the variables
                for varname,val in svinfodict.iteritems():
                    effsvinst.fill(trgname,varname,(trgdec and ismatched),val)
                i+=1
    
    def roofitTree(self,genericbranches,signalonlybranches,outfile,**kwd):
        """..method:: roofitTree(genericbranches,signalonlybranches,outfile[,
                            reprocess=[True|False],
                            treename=treename,
                            evtbranch=evtbranch]) -> ROOT.TTree 
        
        Convert the branches designated in 'genericbranches' and (if any) in
        'signalonlybranches' from a vector<X> format to a plain ntuple, where
        each row corresponds to a RoI. The contents of the 'signalonlybranches'
        (usually the kinematics of the two LSP) will be copied redundantly in 
        each entry. A new int branch called 'event' is also added containing 
        the number of the event the RoI belongs to. A new branch is created as
        well: a int branch 'signal', which is set to 1 when is a signal row or
        0 when is background. The resulting tree is suitable to perform a 
        RooFit analysis.

        That tree is copied in a file called outfile; but if the file already 
        exist the tree got from this tree is going to be returned, if the 
        'reprocess' option flag is set to True, event if the file exist the
        algorithm is performed and the output file is recreated.
        """
        import os
        import sys
        from array import array
        from math import sqrt
        from ROOT import TTree,TFile
        
        # extra class to deal with the options
        # FIXME:: Probably to be promoted to a generic
        #         and independent class
        class extraopt:
            def __init__(self,kwddict):
                self.validkwd = [ ("reprocess",False),
                        ("treename",'roofitRPVMCInfoTree'),("evtbranch",None) ]
                for name,initval in self.validkwd:
                    setattr(self,name,initval)
                for key,val in kwddict.iteritems():
                    if key not in validkwd:
                        raise RuntimeError("not valid '%s' when calling 'roofitTree'" %
                        key)
                    setattr(self,key,val)

        eo = extraopt(kwd)
        # Note that contains
        #   eo.treename, eo.reprocess, oe.evtbranch
        # Do nothing if already exist the file,
        # and the TTree inside there, so return it
        if os.path.isfile(outfile):
            _f = TFile(outfile)
            if _f.isZombie():
                raise IOError("No such root file: '%s'" % outfile) 
            # Check the tree is in there
            if oe.treename not in _f.GetListOfKeys():
                print "[WARNING] The root file '%s' has been found but"\
                        " does not contains the TTree '%s'. The"\
                        " tree is going to be processed" % (outfile,oe.treename)
            else:
                # OJO!! Esta bien esto?, No deberia tener el tree suelto y
                # cerrar el fichero?
                return _f.Get(oe.treename)

        # lazyness: shortenen the variable names:
        branches =genericbranches
        dvbranches=signalonlybranches

        variables = {}
        # Get the types of the roi branches and the dv 
        for bname in branches+dvbranches:
            try:
                _bname = bname
                if bname in dvbranches:
                    _bname = bname.split('_')[0]
                vtype = self.tree.GetBranch(_bname).GetClassName()
            except ReferenceError:
                raise ReferenceError("roofitTree: The branch '%s' doesn't"\
                        " exist in the Tree" % bname)
            # Obtain the equivalent non-vector
            equivtype = vtype.lower().replace('vector<','').replace('>','')
            # Get the initial of the type to be put in the branch
            inittype  = equivtype.upper()[0]
            # Update the variables dict with all this info
            variables[bname] = [array(inittype.lower(),[-1]),inittype]
            # Add the 'event' entry to keep track of the vector per event
            event = array('i',[-1])
            # Add the 'isSignal' entry to describe signal (1) or background (0)
            # RoIs
            isSignal = array('i',[-1])
        # New branch: event number
        eventname = 'event'
        if eventname in branches:
            eventname+='__roofitTree'
        # Setup the new tree
        tree = TTree(eo.treename,eo.treename)
        tree.Branch(eventname,event,eventname+'/I')
        # New branch: designating signal or background
        tree.Branch("isSignal",isSignal,"isSignal/I")
        # Set-up the other variables of the new tree
        dummy = map(lambda (name,(var,_type)): tree.Branch(name,var,name+'/'+_type),
                sorted(variables.iteritems(),key=lambda (name,(var,_type)): _type,reverse=True))

        # Set only the variables to read from the old tree
        self.tree.SetBranchStatus("*",0)
        dum=map(lambda bname: self.tree.SetBranchStatus(bname,1),branches)
        dum=map(lambda bname: self.tree.SetBranchStatus(bname,1),\
                set(map(lambda x: x.split('_')[0], dvbranches)))
    
        # Prepare the DV-related quantities
        dvbranchespost = []
        for bname in dvbranches:
            try:
                name,k = bname.split('_')
            except ValueError:
                raise ValueError("roofitTree: Unexpected format: '%s'. "\
                    "Expecting 'name_i', being i-the index" % bname)
            dvbranchespost.append((name,k))

        dvsample = False
        if len(dvbranches) > 0:
            dvsample = True
        # Fill the tree
        # --- Progress bar :)
        point = float(self.tree.GetEntries())/100.0
        for i,iEvent in enumerate(self.tree):
            sys.stdout.write("\r\033[1;34mINFO\033[1;m Post-processing,"+\
                    " creating RooFit-like tree [ "+"\b"+\
                    str(int(float(i)/point)).rjust(3)+"%]")
            sys.stdout.flush()
            # end-progress bar
            event[0] = i
            # Get number of elements 
            # First for the dv (if any), which is going
            # to be the same for all the event
            for (name,kstr) in dvbranchespost:
                k = int(kstr)
                nametostore = name+'_'+kstr
                try:
                    variables[nametostore][0][0] = getattr(iEvent,name)[k]
                except IndexError:
                    # Meaning that this is not a signal DV sample
                    # -- put dvsample to False
                    dvsample = False
                    # -- remove the content of dvbranchespost so do not
                    #    enter again here
                    dvbranchespost = {}
            # Now the RoI based elements
            # Assuming the same number of elements in the branches list
            nsize = max(map(lambda bname: getattr(iEvent,bname).size(),branches))
            for k in xrange(nsize):
                # Not interested if there is no tracks (Sure?)
                #if iEvent.ntracks[k] < 1:
                #    continue
                # Also getting here the cuts for signal,
                # when dealing with a signal sample
                # If is not a DV samples it only can be bkg
                isSignal[0] = 0
                if dvsample:
                    phiroi = iEvent.jetroi_phi[k]
                    etaroi = iEvent.jetroi_eta[k]
                    dR0 = sqrt((phiroi-iEvent.phi[0])**2.+(etaroi-iEvent.eta[0])**2.) < RCUT
                    dR1 = sqrt((phiroi-iEvent.phi[1])**2.+(etaroi-iEvent.eta[1])**2.) < RCUT
                    isSignal[0] = (dR0 or dR1)
    
                for bname in branches:
                    variables[bname][0][0] = getattr(iEvent,bname)[k]
                # Fill the loop (with constant event number)
                tree.Fill()
        # Create the file and store the ttree before returning it
        print
        _f = TFile(outfile.replace('.root','')+'.root',"UPDATE")
        tree.Write()
        _f.Close()
        
        return tree

class rpvmcinfo(storedeff):
    """.. class rpvmcinfo(rootfiles)
    concrete storedeff class for efficiencies evaluated using the 
    RPVMCInfoTree ATLAS package 
    Git repo:
      https://duartej@bitbucket.org/duartej/rpvmctruthhist.git
    """
    def __init__(self,rootfiles):
        """.. class rpvmcinfo(rootfiles)
        concrete storedeff class for efficiencies evaluated using the 
        RPVMCInfoTree ATLAS package 
        """
        super(rpvmcinfo,self).__init__(rootfiles,'RPVMCInfoTree')

        self.__vars__ = []
        for i in filter(lambda x: x.GetName().find('HLT_') == -1, 
                self.tree.GetListOfBranches()):
            self.__vars__.append(i.GetName())

    def gettriggersnames(self):
        """.. method::
        """
        triggersinntuple = []
        for tbranch in filter(lambda x: x.GetName().find('HLT')==0 and \
                x.GetName().lower().find('jetroi') == -1,self.tree.GetListOfBranches()):
            triggersinntuple.append( tbranch.GetName() )
        return triggersinntuple
    
    def setuptree(self,triggerbr):
        """
        """
        pass

    def getmctruthinfo(self,extra=False):
        """
        """
        from math import sqrt
        # Just for improve readibility
        t = self.tree
        sv = []
        for i in self.llpindices:
            sv.append({})
            # Secondary vertex (displaced) with respect the primary vertex 
            # (it means with respect # the production vertex 
            sv[-1]['Dtdv'] = sqrt((t.dv_X[i]-t.vx_LSP[i])**2.0+(t.dv_Y[i]-t.vy_LSP[i])**2.0)
            sv[-1]['Dzdv'] = t.dv_Z[i]-t.vz_LSP[i]
            sv[-1]['Drdv'] = sqrt(sv[-1]['Dtdv']**2.+sv[-1]['Dzdv']**2.)
            # Secondary vertex absolut info
            sv[-1]['tdv'] = sqrt(t.dv_X[i]**2.0+t.dv_Y[i]**2.0)
            sv[-1]['zdv'] = t.dv_Z[i]
            sv[-1]['rdv'] = sqrt(sv[-1]['tdv']**2.+sv[-1]['zdv']**2.)
            if extra:
                sv[-1]['eta'] = t.eta[i]
                sv[-1]['phi'] = t.phi[i]
                sv[-1]['betagamma'] = t.betagamma[i]
                sv[-1]['nTrk4mm'] = t.nTrk4mm[i]
                sv[-1]['pdgId_g'] = t.genpfromdv_pdgId[i]
                sv[-1]['eta_g']   = t.genpfromdv_eta[i]
                sv[-1]['phi_g']   = t.genpfromdv_phi[i]
                sv[-1]['pt_g']    = t.genpfromdv_pt[i]
                sv[-1]['vx_g']    = t.genpfromdv_vx[i]
                sv[-1]['vy_g']    = t.genpfromdv_vy[i]
                sv[-1]['vz_g']    = t.genpfromdv_vz[i]
        return sv

