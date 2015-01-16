#!/usr/bin/env python
""":mod:`jobsender` -- Send jobs to cluster utilities
======================================================

.. module:: jobsender
   :platform: Unix
   :synopsis: Module gathering utilities to deal with sending 
              jobs to a cluster. The utilities of this module
              are used by the script 'sendjobs', the interface
              the factor to this module
.. moduleauthor:: Jordi Duarte-Campderros <jorge.duarte.campderros@cern.ch>
               """
DEBUG=False
JOBEVT=500

from abc import ABCMeta
from abc import abstractmethod
        
def getrealpaths(inputfiles):
    """..function:: getrealpaths(inputfiles) -> realpaths
    
    Given the names of a files (as regular expressions), 
    the function return the complete path of all the files
    matching the regular expresion

    :param inputfiles: a str or list of str with regular expressions
                       to match files
    :type inputfiles: str or list(str)

    :return: the real paths or an empty list if no match
    :rtype: list(str)

    """
    if not inputfiles:
        return None

    import glob
    import os
    __preinputfiles__ = []
    if type(inputfiles) is str:
        __preinputfiles__ = glob.glob(inputfiles)
    if type(inputfiles) is list:
        for i in inputfiles:
            __preinputfiles__.append([j for j in glob.glob(i)])
    
    return map(lambda x: os.path.realpath(x),set(__preinputfiles__))


def getevt(filelist,**kw):
    """ ..function:: getevt(filelist[,treename]) -> totalevts
    
    Getting the number of events contained in a list
    of files

    :param filelist: the files to look into
    :type filelist: list(str)
    :param treename: the name of the tree where to check 
                     [CollectionTree default]
    :type treename: str

    ;return: number of events contained in the treename Tree 
    :rtype: int
    """
    try:
        import cppyy
    except ImportError:
        pass
    import ROOT

    if kw.has_key("treename"):
        treename=kw["treename"]
    else:
        treename="CollectionTree"

    if DEBUG:
        print "Loading the root files to obtain the N_{evts} "\
                "[Tree:%s]: " % treename
    t = ROOT.TChain(treename)
    for f in filelist:
        t.AddFile(f)
    return t.GetEntries()    


class jobspec(object):
    """ ..class:: jobspec
    
    Class to deal with an specific job to the (cern) cluster.
    It is a base class, which is a placeholder of the methods
    needed to build a concrete implementation of it
    
    Virtual Methods:
     * __setneedenv__          
     * preparejobs
     * createbashscript     
     * sethowtocheckjobs 
     * sendjobs    
     * checkjobs 
     """
    __metaclass__ = ABCMeta

    def __init__(self,bashscriptname,**kw):
        """..class:: jobspec()
        
        Abstract class to deal with a specific kind of job. 
        The following methods have to be implemented in the 
        concrete classes:
          * __setneedenv__
        """
        self.relevantvar = None
        self.typealias   = None
        self.scriptname  = bashscriptname
        # set the relevant variables used to check the kind
        # of job is
        self.__setneedenv__()
        # Controling that the concrete method set the 'relevantvar'
        # datamember
        notfoundmess = "the __setneedenv__ class implemented in the class"
        notfoundmess+=" '%s' must inititalize the datamember" % self.__class__.__name__
        notfoundmess+=" '%s'"
        if not self.relevantvar:
            raise NotImplementedError(notfoundmess % ('relevantvar'))
        if not self.typealias:
            raise NotImplementedError(notfoundmess % ('typealias'))
        # Check if the enviroment is ok
        isenvset= self.checkenvironment()

        if type(isenvset) is tuple:
            message = "The environment is not ready for sending an %s" % self.typealias
            message += " job. The environment variable '%s' is not set." % isenvset[1]
            message += " Do it with the '%s' command." % isenvset[2]
            raise RuntimeError(message)
           
    def checkenvironment(self):
        """..method:: checkenvironment() -> bool

        function to check if the environment is ready (the relevant 
        variables, libraries, etc..) are loaded in order to be able to 
        send this kind of jobs. 
        
        The function uses the 'relevantvar' datamember set in the 
        __setneedenv__ abstract method
        """
        import os
        for _var,_com in self.relevantvar:
            if not os.getenv(_var):
                return False,_com,_var
        return True
    
    @abstractmethod
    def __setneedenv__(self):
        """...method:: __setneedenv__() 

        method to set the datamember 'relevantvar' and the typealias
        which depends of each job. The 'relevantvar' is a list of 
        tuples representing each step (if more than one) in the 
        setup process, where first element is the environment var 
        and the second element the command needed to export that var
        """
        raise NotImplementedError("Class %s doesn't implement "\
                "__setneedenv__()" % (self.__class__.__name__))

    @abstractmethod
    def preparejobs(self):
        """..method:: preparejobs()
        
        function to modify input scripts, make the cluster steer
        file (usually a bash script), build a folder hierarchy, etc.. in
        order to send a job. Depend on the type of job
        """
        raise NotImplementedError("Class %s doesn't implement "\
                "preparejobs()" % (self.__class__.__name__))
     
    @abstractmethod
    def createbashscript(self,**kw):
         """..method:: createbashscript 
         
         function which creates the specific bashscript(s). Depend on the 
         type of job
         """
         raise NotImplementedError("Class %s doesn't implement "\
                 "createbashscript()" % (self.__class__.__name__))

    @abstractmethod
    def sethowtocheckjobs(self):
         """...method:: sethowtocheckjobs()
         
         function to implement how to check if a job has
         succesfully finalized (looking at some key works in the output log
         and/or checking that the expected output files are there). Depend
         on the type of job
         """
         raise NotImplementedError("Class %s doesn't implement "\
                 "sethowtocheckjobs()" % (self.__class__.__name__))

class clusterspec(object):
    """ ..class:: jobspec
    
    Class to deal with an specific cluster (cern/tau/...) cluster.
    This base class serves as placeholder for the concrete implementation
    of a cluster commands, environments,...
    
    Virtual Methods:
     * sendjobs    
     * checkjobs 
     """
    __metaclass__ = ABCMeta
    
    def __init__(self,**kew):
        """
        """
        pass
    
    @abstractmethod
    def sendjobs(self):
         """...method:: sendjobs()
         
         function to send the jobs to the cluster. Depend on the type of cluster 
         """
         raise NotImplementedError("Class %s doesn't implement "\
                 "sendjobs()" % (self.__class__.__name__))
     
    @abstractmethod
    def checkjobs(self):
         """..method:: checkjobs()
         
         function to check the status of a job (running/finalized/
         aborted-failed,...). Depend on the type of cluster
         """
         raise NotImplementedError("Class %s doesn't implement "\
                 "checkjobs()" % (self.__class__.__name__))


class jobsender(jobspec,clusterspec):
    """ ..class:: jobsender
    
    Class to prepare a (athena/generic) job to the (cern) cluster
    This class has some pure virtual methods lister below, so it
    is an abstract class to be by a concrete implementation
    of the cluster (cern/tau/...) and/or the type of job 
    (Athena/Geant4/generic...)
    
    Virtual Methods:
     * checkenvironment          
     * preparejobs
     * createbashscript     
     * sethowtocheckjobs 
     * sendjobs    
     * checkjobs 
     """
    __metaclass__ = ABCMeta

    def __init__(self,bashscript,inputfiles=None,**kw):
        """ ..method:: jobsender(basescript[,inputfiles,maxevts,njobs) ->
                                                            jobsender instance

        Initialize common datamembers:
         * bashscript [str]      : bash script name to be send to the cluster
         * inputfiles [list(str)]: list of the input files names 
         * outputfiles[list(str)]: list of the output files names (if any)
         * njobs      [int]      : number of jobs 
         * maxevts    [int]      : number of events to be processes
         * jobslist   [lit(int)] : list of the sended jobs (or taks) ID

        :param basescript: the base script from build the jobs
        :type basescript: str
        :param inputfiles: str or list of files (can be regex expressions)
        :type inputfiles: str/list(str)
        :param maxevts: number of events to process
        :type maxevts: int
        :param njobs: number of jobs
        :type njobs: int
        """
        self.bashscript = bashscript
        self.inputfiles = getrealpath(inputfiles)
        self.outputfiles= None
        self.njobs      = None
        self.maxevts    = None
        self.jobslist   = None

        if kw.has_key('maxevts'):
            self.maxevts = int(kw['maxevts'])
        if kw.has_key("njobs"):
            self.njobs = int(kw['njobs'])

        if not self.inputfiles:
            return self
        
        # consistency
        if len(self.inputfiles) == 0:
            message = "Didn't found any root file in the entered"
            message +=" location: %s" % str(inputfiles)
            raise RuntimeError(message)

        if not self.maxevts:
            self.maxevts = self.getevt(self.inputfiles)

        if not self.njobs:
            self.njobs = self.maxevts/JOBEVT

        # Get the evtperjob
        evtperjob = self.__evts2proc__/self.__njobs__
        # First event:0 last: n-1
        remainevts = (self.__evts2proc__ % self.__njobs__)-1
        
        #Build the list of events
        for i in xrange(self.__njobs__-1):
            #self.__evtperjob__.append( (i*evtperjob,(i+1)*evtperjob-1) )
            self.__evtperjob__.append( (i*evtperjob,evtperjob) )
        # And the remaining
        self.__evtperjob__.append( ((self.__njobs__-1)*evtperjob,remainevts) ) 

    @staticmethod
    def getevt(filelist,**kw):
        """ ..method:: jobsender.getevt(filelist[,treename]) -> totalevts
        
        Getting the number of events contained in a list
        of files

        :param filelist: the files to look into
        :type filelist: list(str)
        :param treename: the name of the tree where to check 
                         [CollectionTree default]
        :type treename: str

        ;return: number of events contained in the treename Tree 
        :rtype: int
        """
        try:
            import cppyy
        except ImportError:
            pass
        import ROOT

        if kw.has_key("treename"):
            treename=kw["treename"]
        else:
            treename="CollectionTree"

        if DEBUG:
            print "Loading the root files to obtain the N_{evts} "\
                    "[Tree:%s]: " % treename
        t = ROOT.TChain(treename)
        for f in filelist:
            t.AddFile(f)
        return t.GetEntries()    

# jobsender is a mix-in class of jobspec and clusterspec
jobspec.register(jobsender)
clusterspec.register(jobsender)

## -- Concrete implementation: Athena job
class athenajob(jobspec):
    """..class:: athenajob

    Concrete implementation of an athena job. 
    An athena job should contain an jobOption python script which
    feeds the athena.py executable. This jobs needs a list of 
    input files and the probably a list of output files
    """
    def __init__(self,bashscriptname,joboptionfile,inputfiles,**kw):
        """..class:: athenajob
        
        Concrete implementation of an athena job. 
        """
        super(athenajob,self).__init__(bashscriptname,**kw)
        try:
            self.joboption=getrealpaths(joboptionfile)[0]
        except IndexError:
            raise RuntimeError('jobOption file not found %s' % joboptionfile)
        self.inputfiles=getrealpaths(inputfiles)
        if len(self.inputfiles) == 0:
            raise RuntimeError('Not found the Athena inputfiles: %s' \
                    % inputfiles)
        self.makecopyJO()
        
        if kw.has_key('evtmax'):
            self.evtmax = kw['evtmax']
        else:
            self.evtmax = getevt(self.inputfiles,treename='CollectionTree')

        if kw.has_key('njobs'):
            self.evtmax = kw['njobs']
        else:
            self.njobs= self.evtmax/JOBEVT

        # Get the evtperjob
        evtsperjob = self.evtmax/self.njobs
        # First event:0 last: n-1
        remainevts = (self.evtmax % self.njobs)-1
        
        self.skipandperform = []
        # Build a list of tuples containing the events to be skipped
        # followd by the number of events to be processed
        for i in xrange(self.njobs-1):
            self.skipandperform.append( (i*evtsperjob,evtsperjob) )
        # And the remaining
        self.skipandperform.append( ((self.njobs-1)*evtsperjob,remainevts) )


    def __setneedenv__(self):
        """..method:: __setneedenv__() 

        Relevant environment in an ATLAS job:
        """
        self.typealias = 'Athena'
        self.relevantvar =  [ ("AtlasSetup","setupATLAS"), ("CMTCONFIG","asetup") ] 

    def makecopyJO(self):
        """
        """
        import shutil
        import os
        
        localcopy=os.path.join(os.getcwd(),os.path.basename(self.joboption))
        shutil.copyfile(self.joboption,localcopy)
        # And re-point
        self.joboption=localcopy

    def preparejobs(self):
        """..method:: preparejobs() -> listofjobs
        
        main function which builds the folder structure
        and the needed files of the job, in order to be
        sent to the cluster
        """
        import os
        # Obtained some previous info 
        usersetupfolder = self.getuserasetupfolder()
        athenaversion = os.getenv('AtlasVersion')
        compiler      = self.getcompiler()

        # setting up the folder structure to send the jobs
        # including the bashscripts
        self.settingfolders(usersetupfolder,athenaversion,compiler)


    def getuserasetupfolder(self):
        """..method:: getuserasetupfolder() -> fullnameuser

        """
        import os

        ldfolders = os.getenv('LD_LIBRARY_PATH')
        user = os.getenv('USER')
        basedir = None
        for i in ldfolders.split(':'):
            if i.find(user) != -1 and i.find('InstallArea'):
                basedir=i[:i.find('InstallArea')-1]
        # check that the folder exists
        if not basedir or not os.path.isdir(basedir):
            message = 'Check the method (getuserasetupfolder) to'
            message += 'extract the user base directory. The algorithm'
            message += 'didn\'t find the path'
            raise RuntimeError(message)

        return basedir

    def getcompiler(self):
        """..method:: getcompiler() -> compilername
        
        Get the compiler version X.Y.Z, returning gccXY
        """
        import platform
        return platform.python_compiler().lower().replace(' ','').replace('.','')[:-1]

    def createbashscript(self,**kw):
        """..method:: createbashscript 
         
        function which creates the specific bashscript(s). Depend on the 
        type of job
        """
        import os

        class placeholder(object):
            def __init__(self):
                self.setupfolder=None
                self.version=None
                self.gcc =None
        
        ph = placeholder()
        for var,value in kw.iteritems():
            setattr(ph,var,value)
        
        bashfile = '#!/bin/bash\n\n'
        bashfile += '# File created by %s class\n\n' % self.__class__.__name__
        bashfile += 'cd '+ph.setupfolder+'\n'
        bashfile += 'source $AtlasSetup/scripts/asetup.sh %s,%s,here\n' % (ph.version,ph.gcc)
        bashfile += 'cd -\n'
        bashfile += 'cp %s .\n' % self.joboption
        bashfile +='athena.py -c "SkipEvents=%i; EvtMax=%i; FilesInput=%s;" ' % \
                (ph.skipevts,ph.nevents,str(self.inputfiles))
        bashfile += self.joboption+" \n"
        bashfile +="\ncp *.root %s/\n" % os.getcwd()
        f=open(self.scriptname,"w")
        f.write(bashfile)
        f.close()
        os.chmod(self.scriptname,0755)

    def settingfolders(self,usersetupfolder,athenaversion,gcc):
        """..method:: settingfolders()
        """
        import os

        cwd=os.getcwd()

        i=0
        for (skipevts,nevents) in self.skipandperform:
            # create a folder
            foldername = "%sJob_%s_%i" % (self.typealias,self.scriptname,i)
            os.mkdir(foldername)
            os.chdir(foldername)
            # create the local bashscript
            self.createbashscript(setupfolder=usersetupfolder,version=athenaversion,\
                    gcc=gcc,skipevts=skipevts,nevents=nevents)
            os.chdir(cwd)
            i+=1


    def sethowtocheckjobs(self):
        """..method:: sethowtocheckjobs()
        
        An Athena job has succesfully finished if there is the line
        'Py:Athena            INFO leaving with code 0: "successful run"'
        """
        self.succesjobcode=['Py:Athena','INFO leaving with code 0: "successful run"']



# Concrete jobspec class for athena jobs
jobspec.register(athenajob)

