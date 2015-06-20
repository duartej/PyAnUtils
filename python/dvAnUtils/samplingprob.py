#!/usr/bin/env python
""":mod:`samplingprob` -- Sampling probabilities class definitions
===============================================================================

.. module:: samplingprob
   :platform: Unix
      :synopsis: Modules containing the classes related with the sampling
                 probability analysis
    .. moduleauthor:: Jordi Duarte-Campderros <jorge.duarte.campderros@cern.ch>
"""

class ObservableSamplingProb(object):
    """The class is encapsulating the sampling distribution
    associated to an observable. This includes the 
    observable (ROOT.RooRealAbs) and the models asssociated
    to that observables (ROOT.RooAbsPdf)

    Parameters
    ----------
    obs: ROOT.RooRealVar
         Observable

    Attributes
    ----------
    __observable: str
            Name of the observable
    observableName: ROOT.RooRealVar
            Observable which attribute name is built in run-time
            using its name
    __models: dict((str,RooAbsPdf))
            PDF models to be used. The observable could be used in
            a signal region or in a background region, using different
            observables on each case. Therefore, the keys are refering
            to the region (usually 'sig' and 'bkg')
    __pdftypes: dict((str,str))
            The actual PDF function name, available on mod:`pdfmodels`
            associated to each region

    Methods
    -------
    update(wsname,fname,storelist=[])
            Stores the current model (and observable) into
            a ROOT.Workspace, persistified in a root file
        
    """
    def __init__(self,obs,**kwd):
        """
        """
        from PyAnUtils.pyanfunctions import ExtraOpt
        
        # Extra options
        extraopt = ExtraOpt( [('rootfile',None),('ws',None)] )
        extraopt.setkwd(kwd)

        # Initialize observable put the name as attribute
        self.__observable = obs.GetName()
        self.__setattr__(obs.GetName(),obs)

        # Initialize dictionary of models, which must be
        # associated to an observable. Also, the hashed
        # name of the pdf used is stored
        self.__models   = {}
        self.__pdftypes = {}

    def __str__(self):
        """
        """
        ms = 'ObservableSamplingProb instance at %s\n' % hex(id(self))
        ms +=' +-- Associated observable\n'
        ms += ' +---- %s\n' % self.__observable
        ms += '+-- Models\n'
        typeandtitle = map(lambda (y,x): (y,x[0].GetName(),x[0].getTitle()),
                self.__models.iteritems())
        for (_t,_i,_h) in typeandtitle:
            ms += " +---- [%s]: %s,%s\n" % (_t,_i,_h)
        ms += '\n'
        return ms

    def update(self,wsname,fname,storelist=[]):
        """Stores the current model (and observable) into a ROOT.Workspace,
        persistified in a root file
        
        Parameters
        ----------
        wsname: str
             Name to be given to the ROOT.Workspace
        fname:  str
             Name to be given to the ROOT file
        storelist: list(ROOT.RooDataSet,ROOT.RooRealVar,...), optional
             List of RooFit objects to be stored in the same workspace
        """
        import os
        from ROOT import RooWorkspace, TFile

        # Create the ws with the model and data available
        w = RooWorkspace(wsname,'Workspace')
        wsImport = getattr(w,'import')
        # Put the models 
        for rawtuple in self.__models.values():
            model = rawtuple[0]
            anythingelse = rawtuple[1:]
            wsImport(model)
        # Put whatever the user want to store
        for _item in storelist:
            wsImport(_item)

        # Check if the fname already exist
        file_exist = os.path.isfile(fname)
        if file_exist:
            # Create a new auxiliar file, to provisionaly
            # store the ws 
            auxfname = '_auxroot.root'
            w.writeToFile(auxfname)
            # Previously delete the old Workspace, if any
            _rootfile = TFile(fname)
            _rootfile.Delete(wsname+';*')
            _rootfile.Delete("ProcessID*;*")
            _rootfile.Close()
            # Open the auxiliary file
            _aux = TFile(auxfname)
            # and copy the ws to the rootfile
            w = _aux.Get(wsname)
        # and copy the ws to the rootfile
        w.writeToFile(fname,False)

        if file_exist:
            # And closing and removing auxfile
            _aux.Close()
            os.remove(auxfname)

    def availablemodels(self):
        """Available models

        Returns
        -------
        list(str)
          available regions with a model pdf defined
        """
        return self.__models.keys()

    
    def setupmodel(self,modeltype,modelpdfname):
        """Main method to setup the model
        
        Parameters
        ----------
        modeltype: str
            The name of the region where the model is associated
        modelpdfname: str
            The name of the pdf model which must be found it 
            at mod:`pdfmodels` module

        See also
        --------
        pdfmodels: the pool of PDF models
        """
        # from PyAnUtils.dvAnUtils.pdfmodels import\
        #        negative_binomial_pdf,negative_binomial_sum_pdf
        from pdfmodels import negative_binomial_pdf,negative_binomial_sum_pdf
        try:
            model = eval(modelpdfname)
        except NameError:
            raise NameError("There is no available model '%s'" % modelpdfname)
        # Is it there?
        if self.__models.has_key(modeltype):
            print "[WARNING] The model is already set up ignoring..."
            return

        # Instantiate the model using the observable
        self.__models[modeltype] = model(self.__getattribute__(self.__observable))
        self.__pdftypes[modeltype] = modelpdfname

    def fitTo(self,data,modeltype=None):
        """Wrapper to the RooAbsPdf::fitTo

        Parameters
        ----------
        data: ROOT.RooDataSet
        
        modeltype: str, optional
            The region name, note that not using this argument, the
            per default value is the first one found.

        Returns
        -------
        vardict: dict((str,ROOT.RooRealVar))
            The dict with the parameters used in the pdf model (including
            the observable) being the keys the name of those parameters
        """
        # Just picking the first one
        if not modeltype:
            modeltype = self.__models.keys()[0]
        self.__models[modeltype][0].fitTo(data)
        containervar = self.__models[modeltype][0].getVariables()
        vardict = {}
        it = containervar.createIterator()
        print "Fit Results::"
        for i in xrange(containervar.getSize()):
            var = it.Next()
            if var.GetName() == self.__observable:
                continue
            vardict[var.GetName()] = var
            print " + %s=%.3f +/- %.3f" % (var.GetName(),var.getVal(),var.getError())
        
        return vardict
    
    def plot(self,plotname,data,modeltype=None,**kwd):
        """Plot the data and the model and saves the image in pdf

        Parameters
        ----------
        plotname: str
            the name to be used in the image [with extension]
        data: ROOT.RooDataSet
        
        modeltype: str, optional
            The name of the region of the model, not using it will
            use the first one it found

        kwd: dict((str,several types))
            Dictionary of extra options
            sample:
        """
        import ROOT
        from PyAnUtils.plotstyles import njStyle
        
        _style = njStyle()
        _style.cd()

        from PyAnUtils.pyanfunctions import ExtraOpt
        
        aux = ExtraOpt( [ ('sample',''),('xtitle','N_{t}'),
            ('ytitle','Number of Events'),('title',''),
            ('layoutlabel',''),('components','') ] )
        aux.setkwd(kwd)
    
        ROOT.gROOT.SetBatch(1)
    
        frame = self.__getattribute__(self.__observable).frame()
        frame.SetXTitle(aux.xtitle)
        frame.SetYTitle(aux.ytitle)
        frame.SetTitle(aux.title)
        data.plotOn(frame)
        # Model to use -->
        if not modeltype:
            modeltype = self.__models.keys()[0]
        model = self.__models[modeltype][0]
        model.plotOn(frame)
        # -- The components, if any
        components = model.getComponents()
        componentsIter = components.iterator()
        modelName = model.GetName()
        for i in xrange(len(components)):
            comp = componentsIter.Next()
            compName = comp.GetName()
            if compName != modelName:
                model.plotOn(frame,ROOT.RooFit.Components(compName),
                        ROOT.RooFit.LineStyle(ROOT.kDashed))
        # --- The parameters of the fit
        model.paramOn(frame,ROOT.RooFit.Layout(0.55,0.9,0.8),
                ROOT.RooFit.Label(aux.layoutlabel))
        frame.Draw()
        c = ROOT.gROOT.GetListOfCanvases()[0]
        c.SaveAs(aux.sample+"_"+self.__observable+".pdf")
        c.SetLogy()
        c.SaveAs(aux.sample+"_"+self.__observable+"_log.pdf")
        c.SetLogy(0)

class evidence:
    """
    """
    def __init__(self,obsinstances):
        """
        """
        self.__observable = lll
        self.__modelDV = modelDV
        self.__modelBkg= modelBkg


    def __call__(self,observable):
        """
        """
        from math import log10
        self.__observable.setVal(observable)
        samplingprobsum = 0.0
        print self.__modelDV[0]
        for dv,ip in zip(self.__modelDV,self.__modelBkg):
            try:
                samplingprobsum += dv.getVal()/ip.getVal()
            except ZeroDivisionError:
                samplingprobsum += 0.0
        return (-100.0 + 10.0*log10(samplingprobsum))


class DataObsSet(object):
    """.. class:: DataObsSet
    
    Container of ObservableSamplingProb instances which belongs
    to the same data sample. Therefore, all the relevant observables
    of one dataset should be established here

    """
    pass


####################################
## --- Some useful functions  --- ##
####################################

def readfile(filename):
    """Get the ROOT.RooFit objects inside a ROOT file

    Parameters
    ----------
    filename: str
        ROOT input file name

    Returns
    -------
    f: ROOT.TFile
        The ROOT file object, to avoid segmentation faults due to Roofit 
        internal memory management
    obsdict: dict((str,ROOT.RooRealVar))
        The available observables
    modeldict: dict((str,ROOT.RooRealPdf))
        The available PDF models
    databkgdict: dict((str,ROOT.RooDataSet))
        The available datasets
    """
    import ROOT
    f = ROOT.TFile(filename)
    keys = f.GetListOfKeys()

    extract = lambda _type: filter(lambda x: x.GetClassName() == _type,keys)
    builddict = lambda _type: dict(map(lambda x: (x.GetName(),f.Get(x.GetName())),
            extract(_type)))

    # Retrieve all the stuff
    obsdict   = builddict('RooRealVar')
    data      = builddict('RooDataSet')
    modeldict = builddict('RooRealPdf')

    databkgdict = dict(filter(lambda (x,y): x.find('dvbkg') == 0, data.iteritems()))
    datasigdict = dict(filter(lambda (x,y): x.find('dvsig') == 0, data.iteritems()))

    return f,obsdict,modeldict,databkgdict,datasigdict


# METHODS to be used when observing the data
def readworkspace(filename):
    """Get the ROOT.RooWorkspace object inside a ROOT file

    Parameters
    ----------
    filename: str
        ROOT input file name

    Returns
    -------
    f: ROOT.TFile
        The ROOT file object, to avoid segmentation faults due to Roofit 
        internal memory management
    w: ROOT.Workspace
        The workspace
    obsdict: dict((str,ROOT.RooRealVar))
        The available observables
    modeldict: dict((str,ROOT.RooRealPdf))
        The available PDF models
    databkgdict: dict((str,ROOT.RooDataSet))
        The available datasets
    """
    import ROOT
    f = ROOT.TFile(filename)
    w = f.Get("w")

    # Retrieve all the stuff
    # -- Observables
    observables = w.allVars()
    obsIter = observables.iterator()
    obsdict = {}
    for i in xrange(len(observables)):
        currentObs = obsIter.Next()
        obsdict[currentObs.GetName()] = currentObs
    # -- Models
    models = w.allPdfs()
    modelsIter = models.iterator()
    modeldict = {}
    for i in xrange(len(models)):
        currentModel = modelsIter.Next()
        modeldict[currentModel.GetName()] = currentModel
    # -- Data (Note that is a list)
    data = w.allData()
    databkgdict = {}
    datasigdict = {}
    for currentData in data:#xrange(len(data)):
        dname = currentData.GetName()
        if dname.find('dvbkg') == 0:
            databkgdict[dname] = currentData
        elif dname.find('dvsig') == 0:
            datasigdict[dname] = currentData

    return f,w,obsdict,modeldict,databkgdict,datasigdict

def getframe(var,model,data):
    """Function to speed-up the plot management. Just associate 
    the data, model and observable to a frame

    Parameters
    ----------
    var: ROOT.RooRealVar
        The observable to be used as frame
    model: ROOT.RooAbsPdf
    data:  ROOT.RooDataSet

    Returns
    -------
    ROOT.RooPlot
    """
    from PyAnUtils.plotstyles import njStyle
    pstyle = njStyle()
    pstyle.cd()

    frame = var.frame()
    data.plotOn(frame)
    model.plotOn(frame)

    return frame


#####################################################################
## --- Some functions with examples on using the class
#####################################################################

def signalroisample(filename,obs):
    """.. signalroisample(filename)

    given a processed filename with a RooDAt

    """
    from samplingdist import readworkspace,readfile
    #f,w,obsdict,modeldict,databkgdict,datasigdict = readworkspace(filename)
    f,obsdict,modeldict,databkgdict,datasigdict = readfile(filename)
    if not obsdict.has_key(obs):
        raise RuntimeError("Observable '%s' not defined" % obs)
    sd = ObservableSamplingProb(obsdict[obs])
    sd.setupmodel('bkg','negative_binomial_pdf')
    sd.setupmodel('sig','negative_binomial_sum_pdf')

    datasig = datasigdict['dvsig_'+obs]
    databkg = databkgdict['dvbkg_'+obs]
    sd.fitTo(datasig,'sig')
    sd.fitTo(databkg,'bkg')

    samplename = filename.split('_')[1]
    sd.plot(samplename,datasig,'sig',sample=samplename+'_sig')
    sd.plot(samplename,databkg,'bkg',sample=samplename+'_bkg')

    nfile = filename.split('_')[1]+'_bkgsig_'+obs+'_ws.root'
    sd.update('w',nfile,[datasig,databkg])

def bkgroisample(filename,obs):
    """.. signalroisample(filename)

    given a processed filename with a RooDAt

    """
    from samplingdist import readworkspace,readfile
    #f,w,obsdict,modeldict,databkgdict,datasigdict = readworkspace(filename)
    f,obsdict,modeldict,databkgdict,datasigdict = readfile(filename)
    if not obsdict.has_key(obs):
        raise RuntimeError("Observable '%s' not defined" % obs)
    sd = ObservableSamplingProb(obsdict[obs])
    sd.setupmodel('bkg','negative_binomial_pdf')

    databkg = databkgdict['dvbkg_'+obs]
    sd.fitTo(databkg,'bkg')

    samplename = filename.split('_')[1]
    sd.plot(samplename,databkg,'bkg',sample=samplename)

    nfile = filename.split('_')[1]+'_bkg_'+obs+'_ws.root'
    sd.update('w',nfile,[databkg])

#signalroisample("rpvmcplustrigger_muon_177568_sd_processed.root","ntracks")
#signalroisample("rpvmcplustrigger_elec_202882_sd_processed.root","ntracks")
#bkgroisample("rpvmcplustrigger_dijetJF17_129160_sd_processed.root","ntracks")
#bkgroisample("rpvmcplustrigger_dijetJF17_129160_sd_processed.root","ntracksd0lowercut")
#bkgroisample("rpvmcplustrigger_ttbar_110401_sd_processed.root","ntracks")


