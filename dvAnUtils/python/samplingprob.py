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
        """ TWO CONSTRUCTORS with readws=***
        and the other
        """
        from PyAnUtils.pyanfunctions import ExtraOpt
        
        # Extra options
        extraopt = ExtraOpt( [('readws',None),('modeltype',None),
            ('modelname',None)] )
        extraopt.setkwd(kwd)
            
            
        # Initialize dictionary of models, which must be
        # associated to an observable. Also, the hashed
        # name of the pdf used is stored
        self.__models   = {}
        self.__pdftypes = {}

        # Constructor from a Workspace
        if extraopt.readws: 
            out = extraopt.readws
            if type(obs) != str:
                raise RuntimeError("Initialization with the 'readws' keyword"\
                        " requires the first argument to be the name of the"\
                        " observable (str)")
            if not out[2].has_key(obs):
                raise AttributeError("Observable '%s' not found in the "\
                        "Workspace" % obs)
            self.__observable = obs
            self.__setattr__(self.__observable,out[2][obs])
            self.__setattr__
            # Set up the models, need info from the user
            # --- The modeltype (bkg,signal,..)
            if not extraopt.modeltype:
                raise RuntimeError("Initialization with the 'readws' keyword"\
                        " requires another keyword 'modeltype' to be set")
            # --- the actual internal name 
            if not extraopt.modelname:
                raise RuntimeError("Initialization with the 'readws' keyword"\
                        " requires another keyword 'modelname' to be set")
            # --- Set up the models
            self.__setupmodelsfromws(out,extraopt.modeltype,extraopt.modelname)
        # Regular constructor
        else:
            # Initialize observable put the name as attribute
            self.__observable = obs.GetName()
            self.__setattr__(obs.GetName(),obs)
            
    def __str__(self):
        """
        """
        ms = 'ObservableSamplingProb instance at %s\n' % hex(id(self))
        ms +=' |\n'
        ms +='  \-- Associated observable: {0:s}\n'.format(self.__observable)
        ms +=' |\n'
        ms +='  \-- Models:\n'
        typeandtitle = map(lambda (y,x): (y,x[0].GetName(),x[0].getTitle()),
                self.__models.iteritems())
        for (_t,_i,_h) in typeandtitle:
            ms += "  |----- [{0}]: {1},{2}\n".format(_t,_i,_h)
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

    def __setupmodelsfromws(self,out,modeltypesIn,modelnamesIn):
        """ TO BE DOCUMENTED !! FIXME
        """
        # -- Could be a list
        if type(modeltypesIn) == list or type(modelnamesIn) == list:
            if type(modelnamesIn) != list:
                raise NameError("Coherence requires to 'modelnames' keyword"\
                        " being a string, as 'modeltypes' is")
            if type(modeltypesIn) != list:
                raise NameError("'Coherence requires to 'modeltypes' keyword"\
                        " being a string, as 'modelnames' is")
            modeltypeslist = modeltypesIn
            modelnameslist = modelnamesIn
            # Check the same len!!! FIXME
        else:
            modeltypeslist = [modeltypesIn]
            modelnameslist = [modelnameIn] 
        # Setting
        for modeltype,modelname in zip(modeltypeslist,modelnameslist):
            try:
                # Note that the regular constructor puts a ntuple
                # containing the observables, so mimicking that
                self.__models[modeltype] = (out[3][modelname],None)
            except KeyError:
                # Who is not there?
                nothere = None
                if self.__models.has_key(modeltype):
                    nothere = modeltype
                else:
                    # should be here
                    nothere = modelname
                raise AttributeError("Not found the model '%s'" % nothere)
            # Don't have this info, so
            self.__pdftypes[modeltype] = '__UNDEF__'


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
        from pdfmodels import * #negative_binomial_pdf,negative_binomial_sum_pdf
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
        import multiprocessing
        from ROOT import RooFit,RooLinkedList,RooAbsReal,RooDataSet,RooDataHist,RooMinuit
        from ROOT.RooFit import Range,NumCPU,Optimize,ProjectedObservables,SplitRange,DataError,Extended
        
        nCPUs = multiprocessing.cpu_count()

        # Just picking the first one
        if not modeltype:
            modeltype = self.__models.keys()[0]
        ## Create the unbinned likelihood or the chi2 depending the type of the data
        #if isinstance(data,RooDataSet):
        #    _fitToFunction = self.__models[modeltype][0].fitTo
        ##    minim_function = self.__models[modeltype][0].createNNL(data)
        #elif isinstance(data,RooDataHist):
        #    _fitToFunction = self.__models[modeltype][0].chi2FitTo
        ##    minim_function = self.__models[modeltype][0].createChi2(data)
        #else:
        #    raise RuntimeError("[fitTo ERROR]: Unexpected class instance for data:"\
        #            " '{0}'".format(type(data)))
        # Create Minuit interface
        #m = RooMinuit(minim_function)
    
        # we expect a couple of calls to converge.. if not print warning and go on
        failFit = True
        nloop  = 0
        while failFit and nloop < 3:
            print
            print '\033[1;34mfitTo INFO\033[1;m: Fitting Attemp [#{0}]:'.format(nloop) 
            print ' - MODEL: {0} [{1}] '.format(self.__pdftypes[modeltype],modeltype)
            print ' - DATA:  {0}       '.format(data.GetName())
            print 
            fit_result = self.__models[modeltype][0].fitTo(data,RooFit.Save())#RooFit.NumCPU(nCPUs))
            #fit_result = _fitToFunction(data,RooFit.Save())#RooFit.NumCPU(nCPUs))
            # check status and quality of covariance matrix: 
            # covQuality codes 3=Full,accuratte cov matrix, 2=FULL, but forced to POSITIVE DEFINED...
            # Check the status of the
            if fit_result.status() == 0 and fit_result.covQual() == 3:
                failFit = False
            nloop += 1
        if nloop == 3:
            print '\033[1;33mfitTo WARNING\033[1;m: Fit DID NOT CONVERGE! Please do it manually:' 
            print ' - MODEL: {0} [{1}] '.format(self.__pdftypes[modeltype],modeltype)
            print ' - DATA:  {0}       '.format(data.GetName())

        vardict = {}
        avai_variables = parameter_names_from_model(self.__models[modeltype][0])
        largest_length = max(map(lambda x: len(x),avai_variables))
        print
        print "\033[1;34mfitTo INFO\033[1;m: Fit Results"
        print "--------------------------------------------"
        for varname in avai_variables:
            if varname == self.__observable:
                continue
            var = self.get_variable_from_model(modeltype,varname)
            vardict[varname] = var
            str_format = " + {0:"+str(largest_length)+"}={1:.3f} +/- {2:.3f}" 
            print str_format.format(varname,var.getVal(),var.getError())
        print
        
        return vardict
    
    def plot(self,pre_plotname,data,modeltype=None,**kwd):
        """Plot the data and the model and saves the image in pdf

        Parameters
        ----------
        plotname: str
            the name to be used in the image (the suffix will be 
            overwritten by optional plot_suffix)
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
            ('layoutlabel',''),('components',''), ('bins',''),
            ('plot_suffix','pdf')] )
        aux.setkwd(kwd)
    
        ROOT.gROOT.SetBatch(1)

        # format the suffix name
        try:
            plotname = pre_plotname.split('.')[:-1][0]+".{0}".format(aux.plot_suffix)
        except IndexError:
            plotname = pre_plotname+".{0}".format(aux.plot_suffix)
    
        frame = self.__getattribute__(self.__observable).frame()
        frame.SetXTitle(aux.xtitle)
        frame.SetYTitle(aux.ytitle)
        frame.SetTitle(aux.title)
        # Just if the data has to be rebinnined
        if aux.bins:
            data.plotOn(frame,ROOT.RooFit.Binning(int(aux.bins)))
        else:
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
        #plotname_nosuffix = plotname.split('.')[0]
        #plotname_suffix   = plotname.split('.')[-1]
        c.SetLogy(0)
        c.SaveAs(plotname)
        #c.SaveAs(aux.sample+"_"+self.__observable+".pdf")
        c.SetLogy(1)
        c.SaveAs(plotname.split('.')[0]+"_log."+plotname.split(".")[-1])
        #c.SaveAs(aux.sample+"_"+self.__observable+"_log.pdf")

    def getobservable(self):
        """TO BE DCOUMENTED FIXME
        """
        return self.__getattribute__(self.__observable)

    def get_variable_from_model(self,modeltype,obsname):
        """Gets a copy of the RooRealVar object present in a model.
        This method just calls to the `get_variable_from_model` 
        function

        Parameters
        ----------
        modeltype: str
            The type of the model 
        obsname: str
            The name of the variable

        Returns
        -------
        currentvar: ROOT.RooRealVar
            A copy of the variable object, if doesn't exist
            then 'None' is returned

        See Also
        --------
        get_variable_from_model: the function where is performed the work
        """
        return get_variable_from_model(self.getmodel(modeltype),obsname)


    def getobservablename(self):
        """TO BE DCOUMENTED FIXME
        """
        return self.__observable

    def get_pdfmodel_name(self,modeltype=None):
        """Given the 'modeltype' model, the function returns
        the name of the `pdfmodels` model used

        Parameters
        ----------
        modeltype: str|None
            The `modeltype`

        Returns
        -------
        str: the name of the `pdfmodels` class
        """
        # Just picking the first one
        if not modeltype:
            modeltype = self.__pdftypes.keys()[0]
        elif not self.__pdftypes.has_key(modeltype):
            raise AttributeError("No model type '%s' available" % modeltype)
        return self.__pdftypes[modeltype]

    def getmodel(self,modeltype=None):
        """
        """
        # Just picking the first one
        if not modeltype:
            modeltype = self.__models.keys()[0]
        elif not self.__models.has_key(modeltype):
            raise AttributeError("No model type '%s' available" % modeltype)

        return self.__models[modeltype][0]
        


class evidence:
    """
    """
    def __init__(self,obsinst,):
        """
        obsinstances = ( obs, model sign, model bkg) 
        """
        self.__observable = obsinst.getobservable()
        self.__modelDV = obs.getmodel(modeltype)
        self.__modelBkg= obsinstances[2]


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

def array_converter(roodataobject,obs_name):
    """Converts the RooAbsReal object (RooDataSet|RooDataHist|RooAbsPdf)
    into an (numpy, if available) array

    FIXME:: 1D case only!!??

    Parameters
    ----------
    roodataobject: ROOT.RooDataSet|ROOT.RooDataHist|ROOT.RooAbsPdf
        The RooAbsVar object to be converted
    obs_name: str
        The name of the observable to create the histogram against for

    Returns
    -------
    harray: numpy.array|array.array
        The array containing the elements in each bin of the histogram
    """
    try:
        from numpy import array
    except ImportError:
        from array import array as array

    # Create the histogram with respect the observable
    histo = roodataobject.createHistogram(obs_name)
    # Normalize
    histo.Scale(1.0/histo.Integral())
    _provlist = []
    for i in xrange(1,histo.GetNbinsX()+1):
        _provlist.append(histo.GetBinContent(i))

    # the output array
    try:
        harray = array([ x for x in _provlist ],dtype='d')
    except TypeError:
        harray = array('d',[ x for x in _provlist ])
    return harray


def get_variable_from_model(model,varname):
    """Gets a copy of the RooRealVar object present in a model

    Parameters
    ----------
    model: ROOT.RooAbsPdf
        The model object where the variable lives in.
    varname: str
        The name of the variable

    Returns
    -------
    currentvar: ROOT.RooRealVar
        A copy of the variable object, if doesn't exist
        then 'None' is returned
    """
    variables = model.getVariables()
    itvar = variables.iterator()
    for i in xrange(len(variables)):
        currentvar = itvar.Next()
        if currentvar.GetName() == varname:
            return currentvar
    return None

def parameter_names_from_model(model):
    """Gets a list of the parameters presents in a model

    Parameters
    ----------
    model: ROOT.RooAbsPdf
        The model object where the variable lives in.

    Returns
    -------
    variables: list(str)
        A list of the names of the parameters presents in the
        model
    """
    variables = model.getVariables()
    itvar = variables.iterator()
    names = []
    for i in xrange(len(variables)):
        currentvar = itvar.Next()
        names.append(currentvar.GetName())
    return names

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
    datahists = builddict('RooDataHist')
    data.update(datahists)
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


