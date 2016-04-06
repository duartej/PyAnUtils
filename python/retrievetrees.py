#!/usr/bin/env python
""":module:`retrievetrees` -- Helper class to deal with n-tuple style ROOT Files
================================================================================

.. module:: retrievetrees    
      :platform: Unix
      :synopsis: Classes defined to get the content of ROOT files which are
                 n-tuple types.

       .. scriptauthor:: Jordi Duarte-Campderros <jorge.duarte.campderros@cern.ch>
"""
from abc import ABCMeta
from abc import abstractmethod

class storedtree(object):
    """Abstract class to implement the retrieval of a tree-type (n-tuple) root file.
    The concrete classes should implement the relative methods dependents of the
    ntuple obtainer (RPVMCInfoTree/RPVMCTruthHist/...). The class is intented to
    deal with the main plots 
    Virtual methods:
     * gettreechain
     * getmctruthinfo
     * setuptree
    """
    __metaclass__ = ABCMeta

    def __init__(self,rootfiles,chainname):
        """Abstract class to implement the retrieval of a tree-type (n-tuple) root file.
        The concrete classes should implement the relative methods dependents of the
        ntuple obtainer (RPVMCInfoTree/RPVMCTruthHist/...)
        Virtual methods:
         * gettreechain
         * getmctruthinfo
         * setuptree
        """
        import ROOT
        import os

        # should be a list
        if type(rootfiles) is not list:
            self._rootfiles = [rootfiles]
        else:
            self._rootfiles = rootfiles

        self._tree = ROOT.TChain(chainname)
        print "TChain '%s' created" % chainname
        print "Adding %i root files to the tree" % len(self._rootfiles)
        for i in sorted(self._rootfiles):
            # is there a file?
            if not os.path.exists(i):
                raise IOError("ROOT file '{0}' does not exists!".format(i))
            self._tree.AddFile(i)
        
        self._plotsactivated = False
        self._nentries   = self._tree.GetEntries()
        self._wise_values= {}
        self._aliases    = {}
        self._currententry = -1
        self._aux_associated = {}
        # The self._vars attribute is created in the concrete implementations
    
    #def __iter__(self):
    #    """Easyly iterates the tree, by calling the GetEntry methods
    #    """
    #    return self

    def activate_variable(self,varname,methodtouse=None,**kwd):
        """The varname variable is encapsulated to be includede in this
        instance and an attribute with the name `varname` (or `alias` if
        was used) is settled. If this method is called with the argument
        `methodtouse` the implicit assumption is that `varname` is
        representing a class in the original TTree of the file, therefore
        the `methodtouse` must be a valid method of the `varname` class 
        (as a string, and without the call '()', see `Examples`). In
        this case, the encapsulation of the method is also performed and
        can be accessed through the attribute built from 'varname_methodtouse'
        Note that the method call is changing in order to use the index of 
        the i-element on the case of a vector variable.

    
        Parameters
        -----------
        varname: str
            the name of the variable. It is a ROOT.TBranch (or inheriting class)
            on the input root file
        methodtosue: str [Default: None]
            a valid method of the class which `varname` is an instance
        alias: str, optional
            the name to be used as attribute instead of `varname`
        isvector: bool, optional
            whether or not `varname` is a std::vector in the input tree
        methodshort: str, optional
            a short name to be used as attribute instead of `methodtouse`
        nocallmethod: bool, optional
            whether the method `methodtouse` should not be called or yes, i.e.

        Examples
        --------
        The root file contains a TTree called "CollectionTree" and a 
        TBranchElement called 'InDetHighD0Particles':
        ...
        <ROOT.TBranchElement object ("InDetHighD0TrackParticles") at 0x4a2b290>
        ...
        which is a std::vector of instances of the class "xAOD::TrackParticles".
        This class has a method "xAOD::TrackParticles::d0()", 
        "xAOD::TrackParticles::z0()". The following lines shows the 
        instantiation of the class and the encapsulation of those methods:

        >>> a = xaodtree('filename.root')
        >>> a.activate_variable('InDetHighD0TrackParticles','d0')
        >>> a.activate_variable('InDetHighD0TrackParticles','z0')

        To obtain the d0 of the i-track in the j-event:
        >>> a.getentry(j)
        >>> a.InDetHighD0TrackParticles_d0(i)
        
        Raises
        ------

        Notes on implementation
        -----------------------
        The main data-member is the '_wise_values' dictionary. Each
        key of the dictionary is filled with the name of the Tree-branch
        variable, and the values are 2-tuples composed by the actual
        accessor and a dictionary with the methods associtated to that
        variable and the values are the actual accessors of those methods:

        _wise_values = { 'branchvariablename': (ROOT.ClassOfbranchvariablename, 
                                   { 'method1': method1functor(int index), ...} ) }
        """
        from PyAnUtils.pyanfunctions import ExtraOpt
        opt = ExtraOpt( [('alias',None), ('isvector',True), \
                ('methodshort',None), ('nocallmethod',False)] )
        opt.setkwd(kwd)
        
        if not opt.alias:
            aliasname = varname
        else:
            aliasname = opt.alias
            # Not needed below line... to be deprecated this data-member
            self._aliases[aliasname] = opt.alias

        methodimpl = methodtouse
        if opt.methodshort:
            methodname = opt.methodshort
        else:
            methodname = methodtouse

        if opt.isvector:
            if opt.nocallmethod:
                extractfunc = lambda k: getattr(self._wise_values[aliasname][0][k],methodimpl)
            else:
                extractfunc = lambda k: getattr(self._wise_values[aliasname][0][k],methodimpl)()
        else:
            extractfunc = lambda k=None: getattr(self._wise_values[aliasname][0],methodimpl)
        
        # First initialization
        if not self._wise_values.has_key(aliasname):
            # Note that an exception will be raised by ROOT if the attribute 
            # doesn't exist in the TTree
            self._wise_values[aliasname] = (getattr(self._tree,varname),{})
            # Also create an accessor
            setattr(self,aliasname,self._wise_values[aliasname][0])
            # Be careful, only if is a vector make sense
            try:
                setattr(self,aliasname+'_size',self._wise_values[aliasname][0].size())
            except AttributeError:
                pass

        # Just initialize the variable
        if not methodtouse:
            return

        self._wise_values[aliasname][1][methodname] = extractfunc
        # how to obtain the variable from the tree: methodtouse, check it if
        # is works
        if self._currententry == -1:
            self._tree.GetEntry(0)
        # Check if the attribute exits, othewise raised exception by ROOT
        _dummy = self._wise_values[aliasname][1][methodname](0)
        # Just making  an accessor: nameOfVariable_method
        setattr(self,aliasname+'_'+methodname,self._wise_values[aliasname][1][methodname])
        

    def activate_all_variables(self):
        """
        """
        for tbranch in self._tree.GetListOfBranches():
            self.activate_variable(tbranch.GetName())

    def deactivate_variable(self,varname):
        """
        """
        # Put a print here!!!! WARNING
        if varname in self._wise_values.keys():
            raise AttributeError("Trying to de-activate a previously activated"\
                    " variable: '%s'" % varname)
        self._tree.SetBranchStatus(varname+'*',0)

    def deactivate_all_unused_variables(self):
        """
        """
        # get the actual branch names, not an alias if were used
        nameoftheusedbranches = map(lambda x: x.GetName(), self._wise.values.values())
        deactivated = []
        for tbranch in self._tree.GetListOfBranches():
            if tbranch.GetName() not in nameoftheusedbranches:
                self.deactivate_variable(tbranch.GetName())
                deactivated.append(tbranch.GetName())
        # Print deactivated info if we want...a

    #def book_histo(self,histo,*variablenames):
    #    """Associate an histogram (ROOT.THXF) to a list of 
    #    variables. Each histogream is going to be filled when
    #    the method fill_all_histos is called. Note that more
    #    complicated syntax is allowed with the optional parameter 
    #    `method`. 

    #    Parameters
    #    ----------
    #    histo: ROOT.THXF
    #        the histogram (X=1,2,3)
    #    variablenames: (str[,str,..])
    #        the link between the histogram and the variables of this
    #        ntuple. The variable should be of the type varname_method 
    #        (see method `activate_variable`)

    #    """
    #    # First check the existence of the variables
    #    listofgetters = []
    #    for varname in variablenames:
    #        if not hasattr(self,varname):
    #            raise AttributeError("Variable '%s' not activated" % varname)
    #        listofgetters.append(getattr(self,varname))

    #    self._histos.append( (histo,listofgetters) )


    #def book_histos(self,hc,histoVarMap):
    #    """
    #    Parameters
    #    ----------
    #    hc: PyAnUtils.HistoContainer
    #        the container of histograms already initialized and ready to
    #        be filled
    #    histoVarMap: dict( (str,str) )
    #        the link between the histogram names and the variable names.
    #        Every histogram name (key of the dict) is pointing to the 
    #        variable (or list of variables) which should be filled every
    #        call to the 'fill' method

    #    Note
    #    ----
    #    The name of the histograms should match the name of the 
    #    activated variables because this is the way they are going
    #    to be filled
    #    """
    #    # Perform some consistency checks
    #    for hname, variables in histoVarMap.iteritems():
    #        hc.checkhisto(hname)
    #        # Checking variables exist
    #        if type(variables) is str:
    #            if variables not in self._wise_values.keys():
    #                raise AttributeError("Not variable named '%s' has been"\
    #                        " activated" % variables)
    #        elif type(variables) is tuple:
    #            for var in variables:
    #                if var not in self._wise_values.keys():
    #                    raise AttributeError("Not variable named '%s' has been"\
    #                            " activated" % var)
    #        else:
    #            raise RuntimeError("Not valid type for '%s'. Only str or tuple(str)"\
    #                    " are accepted" % variables)

    #        self._histos[variables] = getattr(hc,hname)
    
    def getentries(self):
        """
        """
        return self._nentries

    def getentry(self,i):
        """
        """
        if self._currententry == i:
            return
        _dummy = self._tree.GetEntry(i)
        # working in xAOD trees, setting the aux variables each event
        for varname in self._aux_associated.keys():
            #setattr(self,varname,getattr(self._tree,varname))
            #self._aux_associated[varname] = getattr(self._tree,varname+'Aux.')
           getattr(self,varname).setStore(self._aux_associated[varname])
        self._currententry = i

    #def fill_all_histos(self):
    #    """
    #    """
    #    pass

    #def fill(self,i):
    #    """
    #    """
    #    self.getentry(i)
    #    for histo,m in self._histos.iteritems():
    #        x = m()
    #        if len(m) >= 3:
    #            x = variables[0],variables[1]
    #            if len(variables) == 3:
    #                z = variables[2]
    #                histos.Fill(x,y,z)
    #            else:
    #                histos.Fill(x,y)


class plaintree(storedtree):
    """.. class plaintree(rootfiles,treename)
    concrete storedeff class for plain TTree, i.e. containing STL containers
    or other plain types of C
    """
    def __init__(self,rootfiles,treename):
        """.. class plaintree(rootfiles,treename)
        concrete storedeff class for plain TTree, i.e. containing STL containers
        or other plain types of C

        TO BE DEPRECATED: ROOT do not need that anymore. You can access directly
        """
        import ROOT

        super(plaintree,self).__init__(rootfiles,treename)
        
        # create direct access to the variables (as attributes of the class)
        self.getentry(0)
        self.activate_all_variables()

class xaodtree(storedtree):
    """.. class rpvmcinfo(rootfiles)
    concrete storedeff class for efficiencies evaluated using the 
    RPVMCInfoTree ATLAS package 
    Git repo:
      https://duartej@bitbucket.org/duartej/rpvmctruthhist.git
    """
    #def __init__(self,rootfiles):
    #    """.. class rpvmcinfo(rootfiles)
    #    concrete storedeff class for efficiencies evaluated using the 
    #    RPVMCInfoTree ATLAS package 
    #    """
    #    import ROOT
    #    import cppyy
    #    #import PyCintex
    #    #PyCintex.Cintex.Enable()
    #    # Not use this, just look cyypy, and the other stuff..
    #    from AthenaROOTAccess import transientTree

    #    super(xaodtree,self).__init__(rootfiles,'CollectionTree')

    #    # re-do the tree, to associate properly auxliar data and so on
    #    # FIXME:: VERY PROVISIONAL FIXME::
    #    self._file = ROOT.TFile.Open(rootfiles)
    #    del self._tree
    #    self._tree = transientTree.makeTree(self._file)

    #    # Initialize the tree, just to be able to set memory addresses
    #    self.getentry(0)
    
    # second version
    def __init__(self,rootfiles):
        """.. class rpvmcinfo(rootfiles)
        concrete storedeff class for efficiencies evaluated using the 
        RPVMCInfoTree ATLAS package 
        """
        import ROOT
        import cppyy
        # let's assume we are inside ATLAS-- FIXME: CHECK IT

        super(xaodtree,self).__init__(rootfiles,'CollectionTree')
        
        # let's associate properly auxliar data and so on
        # Initialize the tree, just to be able to set memory addresses
        self.getentry(0)

        # Obtain all the variables of the tree, and their associated
        branch_names = map(lambda x: x.GetName(), self._tree.GetListOfBranches())
        tocreate_attr = []
        for bname in filter(lambda y: y.find('Aux') == -1,branch_names):
            try:
                # try to match then name or only the instance name A_B_C --> C
                bname_aux = filter(lambda x: x == bname+'Aux.',branch_names)[0]
                self._aux_associated[bname] = getattr(self._tree,bname_aux)
            except IndexError:
                pass
            tocreate_attr.append( (bname,getattr(self._tree,bname)) )
        # -- note that if no aux is associated is because we are not using 
        #    properly the name info: CONTAINERTYPE<CLASSCONTAINED>_INSTANCENAME_
        if len(self._aux_associated) == 0:
            tocreate_attr = []
            # get a splitted list TYPECLASS,INSTANCE
            instances_names = map(lambda x: x.GetName().split('_'), self._tree.GetListOfBranches())
            for bname in filter(lambda y: y[-1].find('Aux') == -1,instances_names):
                try:
                    # try to match then name or only the instance name A_B_C --> C
                    bname_aux = filter(lambda x: x[-1] == bname[-1]+'Aux.',instances_names)[0]
                    self._aux_associated[bname[-1]] = getattr(self._tree,'_'.join(bname_aux))
                except IndexError:
                    pass
                tocreate_attr.append( (bname[-1],getattr(self._tree,'_'.join(bname))) )
        # create the attribute to the class
        for (atname,obj) in tocreate_attr:
            setattr(self,atname,obj)
        #    properly the instances names: TYPE_CLASS_INSTANCE 
        # do the association (points to the aux var)
        for varname,auxvar in self._aux_associated.iteritems():
            getattr(self,varname).setStore(auxvar)

