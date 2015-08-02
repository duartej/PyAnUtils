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
    ntuple obtainer (RPVMCInfoTree/RPVMCTruthHist/...)
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
        
        self._rootfiles = rootfiles
        
        self._tree = ROOT.TChain(chainname)
        print "TChain '%s' created" % chainname
        print "Adding %i root files to the tree" % len(self.rootfiles)
        for i in sorted(self._rootfiles):
            self._tree.AddFile(i)
        
        self._plotsactivated = False
        self._nentries   = self.tree.GetEntries()
        self._wise_values = {}
        # The self._vars attribute is created in the concrete implementations


    def activate_variables(self,varname,alias=None):
        """The varname variable is activated and will be filled in the entry loop
        of the tree. If there is no varname, it is going to be used all of them 
        (content of the _vars datamember). If varname is a tuple of str, a
        TH2F is going to be created, while if is a str or a list of str, a TH1F
        foe each variable is created
    
        Parameters
        -----------
        varname: str | tuple(str,str) | list(str)
            the name of the variable(s) to activate
        histos:  ROOT.TH1F | ROOT.TH2F | list(ROOT.TH1F)
            the associated histogram to the variables. It must match the content 
            of the varname parameter

        Raises
        ------
        """
        if not alias:
            aliasname = varname
        else:
            aliasname = alias

        try:
            self._wise_value[aliasname] = getattr(self._tree,varname)
        except AttributeError:
            raise AttributeError("Not found variable '%s' in the Tree" % varname)


    def activate_all_variables(self):
        """
        """
        for tbranch in self._tree.GetListOfBranches():
            self.activate_variable(tbranch.GetName())

    def deactivate_variable(self,varname):
        """
        """
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

    def book_histos(self,hc,histoVarMap):
        """
        Parameters
        ----------
        hc: PyAnUtils.HistoContainer
            the container of histograms already initialized and ready to
            be filled
        histoVarMap: dict( (str,str) )
            the link between the histogram names and the variable names.
            Every histogram name (key of the dict) is pointing to the 
            variable (or list of variables) which should be filled every
            call to the 'fill' method

        Note
        ----
        The name of the histograms should match the name of the 
        activated variables because this is the way they are going
        to be filled
        """
        # Perform some consistency checks
        for hname, variables in histoVarMap.iteritems():
            hc.checkhisto(hname)
            # Checking variables exist
            if type(variables) is str:
                if variables not in self._wise_values.keys():
                    raise AttributeError("Not variable named '%s' has been"\
                            " activated" % variables)
            elif type(variables) is tuple:
                for var in variables:
                    if var not in self._wise_values.keys():
                        raise AttributeError("Not variable named '%s' has been"\
                                " activated" % var)
            else:
                raise RuntimeError("Not valid type for '%s'. Only str or tuple(str)"\
                        " are accepted" % variables)

            self._histos[variables] = getattr(hc,hname)
    
    def getentries(self):
        """
        """
        return self._nentries

    def getentry(self,i):
        """
        """
        _dummy = self._tree.GetEntry(i)

    def fill(self,i):
        """
        """
        self.getentry(i)
        for variables,histo in self._histos.iteritems():
            if type(variables) is str:
                histo.Fill( self._wise_values[variables] )
            elif type(variables) is tuple:
                x,y = variables[0],variables[1]
                if len(variables) == 3:
                    z = variables[2]
                    histos.Fill(x,y,z)
                else:
                    histos.Fill(x,y)



class xaod(storedtree):
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
        import ROOT
        import PyCintex
        PyCintex.Cintex.Enable()
        # Not use this, just look cyypy, and the other stuff..
        from AthenaROOTAccess import transientTree  

        super(xaod,self).__init__(rootfiles,'CollectionTree')
