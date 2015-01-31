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
DEBUG=True
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


class jobdescription(object):
    """..class:: jobdescription

    Class to store all the information relative to a job.
    This class is used by both jobspec and clusterspec classes,
    where some datamembers should be filled by one class and
    others by the other class. The class provides the following
    information (in parenthesis it is indicated which class is
    the responsible of filling the datamember):
     * path: the path where the job has been build (jobspec)
     * script: the script to be sended to the cluster (jobspec)
     * ID: job id in the cluster (clusterspec)
     * status: job status in the cluster (clusterspec)
    """
    def __init__(self,**kw):
        """..class:: jobdescription

        Class to store all the information relative to a job.
        This class is used by both jobspec and clusterspec classes,
        where some datamembers should be filled by one class and
        others by the other class. The class provides the following
        information (in parenthesis it is indicated which class is
        the responsible of filling the datamember):
         * path: the path where the job has been build (jobspec)
         * script: the script to be sended to the cluster (jobspec)
         * ID: job id in the cluster (clusterspec)
         * status: job status in the cluster (clusterspec)
        """
        # I would need to check that the instance is build only
        # throught the buildfromcluster or buildfromjob methods
        # FIXME
        self.path   = None
        self.script = None
        self.ID     = None
        self.status = None
        self.index  = None
        for _var,_value in kw.iteritems():
            setattr(self,_var,_value)

    def getnextstatus(self,clusterinst,checkfinishedjob):
        """..method:: getnextstatus() -> nextstatus

        The life of a job follows a clear workflow:
        None -> submitted -> running -> |  (finished) 
                                        |-+ failed    -->  submitted
                                        |-+ successed -->  Done
        """
        if not self.status:
            clusterinst.submit()#submit(self)
            self.status = 'submitted'
        elif self.status == 'submitted' or self.status == 'running':
            self.status=clusterinst.checkstatus(self)
        elif self.status == 'finished':
            self.status = checkfinishedjob(self)
        elif self.status == 'failed':
            self.status = clusterinst.failed()
        elif self.status == 'successed':
            clusterinst.done()
            self.status = 'done'

    @staticmethod
    def buildfromjob(path,script,index):
        """
        """
        return jobdescription(path=path,script=script,index=index)
    
    @staticmethod
    def buildfromcluster(ID,status):
        """
        """
        return jobdescription(ID=ID,status=status)



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
        self.jobdescription = []
        # set the relevant variables used to check the kind
        # of job is
        self.__setneedenv__()
        # Controling that the concrete method set the 'relevantvar'
        # datamember
        notfoundmess = "the __setneedenv__ class implemented in the class"
        notfoundmess+=" '%s' must inititalize the"
        notfoundmess+=" datamember '%s'" % self.__class__.__name__
        if not self.relevantvar:
            raise NotImplementedError(notfoundmess % ('relevantvar'))
        if not self.typealias:
            raise NotImplementedError(notfoundmess % ('typealias'))
        # Check if the enviroment is ok
        isenvset= self.checkenvironment()

        if type(isenvset) is tuple:
            message = "The environment is not ready for sending"
            message +=" an %s job. The environment" % self.typealias
            message += " variable '%s' is not set." % isenvset[1]
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
    def checkfinishedjob(self,jobdsc):
        """..method:: checkfinishedjob(jobdsc) -> status
        
        using the datamember 'successjobcode' perform a check
        to the job (jobdsc) to see if it is found the expected
        outputs or success codes
        """
        raise NotImplementedError("Class %s doesn't implement "\
                "checkfinishedjob()" % (self.__class__.__name__))
    
    @abstractmethod
    def __setneedenv__(self):
        """..method:: __setneedenv__() 

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
    def sethowtocheckstatus(self):
         """...method:: sethowtocheckstatus()
         
         function to implement how to check if a job has
         succesfully finalized (looking at some key works in the output log
         and/or checking that the expected output files are there). Depend
         on the type of job
         """
         raise NotImplementedError("Class %s doesn't implement "\
                 "sethowtocheckstatus()" % (self.__class__.__name__))

class clusterspec(object):
    """ ..class:: jobspec
    
    Class to deal with an specific cluster (cern/tau/...) cluster.
    This base class serves as placeholder for the concrete implementation
    of a cluster commands, environments,...
    
    Virtual Methods:
     * getjobidfromcommand
     * getstatusfromcommandline
     * done
     * failed
     """
    __metaclass__ = ABCMeta
    
    def __init__(self,joblist,**kw):
        """ ..class:: jobspec
        
        Class to deal with an specific cluster (cern/tau/...) cluster.
        This base class serves as placeholder for the concrete implementation
        of a cluster commands, environments,...
        
        Virtual Methods:
         * getjobidfromcommand    
         * getstatusfromcommandline
         * failed
         * done
        """
        self.sendcom     = None
        self.extraopt    = []
        self.statuscom   = None
        self.joblist     = joblist

    def submit(self):
        """..method:: submit()
        wrapper to submit(jobdsc) function, using all the
        jobs in the list
        """
        for jb in self.joblist:
            self.submitjob(jb)
    
    def submitjob(self,jobdsc):
        """...method:: submitjob(jobdsc)
         
        function to send the jobs to the cluster.
        """
        from subprocess import Popen,PIPE
        import os
        cwd = os.getcwd()
        # Going to directory of sending
        os.chdir(jobdsc.path)
        # Building the command to send to the shell
        command = [ self.sendcom ]
        for i in self.extraopt:
            command.append(i)
        command.append(jobdsc.script+'.sh')
        # Send the command
        p = Popen(command,stdout=PIPE,stderr=PIPE).communicate()
        if p[1] != "":
            message = "ERROR from %i:\n" % self.sendcom
            message += p[1]+"\n"
            os.chdir(cwd)
            raise RuntimeError(message)
        ## The job-id is released in the message:
        self.ID = self.getjobidfromcommand(p[0])
        jobdsc.ID = self.ID
        print "INFO:"+str(jobdsc.script)+'_'+str(jobdsc.index)+\
                " submitted with cluster ID:"+str(self.ID)
        # Coming back to the original folder
        os.chdir(cwd)
     
    @abstractmethod
    def getjobidfromcommand(self,p):
        """..method:: getjobidfromcommand()
        
        function to obtain the job-ID from the cluster command
        when it is sended (using sendcom)
        """
        raise NotImplementedError("Class %s doesn't implement "\
                "getjobidfromcommand()" % (self.__class__.__name__))
    
    def checkstatus(self,jobdsc):
        """..method:: checkstatus()
        
        function to check the status of a job (running/finalized/
        aborted-failed,...). 
        """
        from subprocess import Popen,PIPE
        import os
        if jobdsc.status == 'running' or 'submitted':
            command = [ self.statuscom, str(jobdsc.ID) ]
            p = Popen(command,stdout=PIPE,stderr=PIPE).communicate()
            return self.getstatusfromcommandline(p)
        else:
            return jobdsc.status

    @abstractmethod
    def getstatusfromcommandline(self,p):
        """..method:: getstatusfromcommandline() -> status
        
        function to obtain the status of a job. Cluster dependent
        """
        raise NotImplementedError("Class %s doesn't implement "\
                 "getstatusfromcommandline()" % (self.__class__.__name__))
    
    @abstractmethod
    def failed(self):
        """..method:: failed()
         
        function to check the status of a job (running/finalized/
        aborted-failed,...). Depend on the type of cluster
        """
        raise NotImplementedError("Class %s doesn't implement "\
                 "failed()" % (self.__class__.__name__))

    @abstractmethod
    def done(self):
        """..method:: done()
        
        function to check the status of a job (running/finalized/
        aborted-failed,...). Depend on the type of cluster
        """
        raise NotImplementedError("Class %s doesn't implement "\
                 "done()" % (self.__class__.__name__))



# --- Concrete class for the CERN cluster (using the lxplus UI)
class cerncluster(clusterspec):
    """..class:: cerncluster

    Concrete implementation of the clusterspec class dealing with
    the cluster at cern (usign lxplus as UI)
    """
    def __init__(self,joblist=None,**kw):
        """..class:: cerncluster 
        Concrete implementation of the clusterspec class dealing with
        the cluster at cern (usign lxplus as UI)
        """
        super(cerncluster,self).__init__(joblist,**kw)
        self.sendcom   = 'bsub'
        self.statuscom = 'bjobs'
        self.extraopt  += [ '-q','8nh' ]
    
    def getjobidfromcommand(self,p):
        """..method:: getjobidfromcommand()
        
        function to obtain the job-ID from the cluster command
        when it is sended (using sendcom)
        """
        return p.split('<')[-1].split('>')[0]
    
    def getstatusfromcommandline(self,p):
        """..method:: checkstatus()
        
        function to check the status of a job (running/finalized/
        aborted-failed,...).
        """
        # bjobs output
        # JOBID USER STAT QUEUE FROM_HOST EXEC_HOST JOB_NAME SUBMIT_TIME

        isfinished=False
        if p[0].find('not found') != -1 or \
                p[1].find('not found') != -1: 
            return 'finished'
        elif p[0].find('JOBID') == 0:
            jobinfoline = p[0].split('\n')[-1]
            # Third element
            status = jobinfoline.split()[2]
            if status == 'PEND':
                return 'submitted'
            elif status == 'RUN':
                return 'running'
            else:
                message='I have no idea of the status parsed as "%s"' % status
                print message
        else:
            message='I have no idea of the status parsed as "%s"' % p[1]
            raise RuntimeError(message)
    
    def failed(self):
        """..method:: checkstatus()
         
        function to check the status of a job (running/finalized/
        aborted-failed,...). Depend on the type of cluster
        """
        raise NotImplementedError("Class %s doesn't implement "\
                 "checkstatus()" % (self.__class__.__name__))

    def done(self):
        """..method:: checkstatus()
        
        function to check the status of a job (running/finalized/
        aborted-failed,...). Depend on the type of cluster
        """
        raise NotImplementedError("Class %s doesn't implement "\
                 "checkstatus()" % (self.__class__.__name__))

clusterspec.register(cerncluster)



## -- Concrete implementation: Athena job
class athenajob(jobspec):
    """..class:: athenajob

    Concrete implementation of an athena job. 
    An athena job should contain an jobOption python script which
    feeds the athena.py executable. This jobs needs a list of 
    input files and the probably a list of output files. 
    TO BE IMPLEMENTED: Any extra configuration variable to be used
    in the jobOption (via -c), can be introduced with the kw in the
    construction.
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
            self.evtmax = int(kw['evtmax'])
        else:
            self.evtmax = getevt(self.inputfiles,treename='CollectionTree')

        if kw.has_key('njobs'):
            self.njobs = int(kw['njobs'])
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
        if localcopy != self.joboption:
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

            def haveallvars(self):
                if not self.setupfolder or not self.version or not self.gcc:
                    return False
                return True
        
        ph = placeholder()
        for var,value in kw.iteritems():
            setattr(ph,var,value)
        
        if not ph.haveallvars():
            message = "Note that the asetup folder, the Athena version and"
            message += " the version of the gcc compiler are needed to build the"
            message += " bashscript"
            raise RuntimeError(message)
            
        bashfile = '#!/bin/bash\n\n'
        bashfile += '# File created by %s class\n\n' % self.__class__.__name__
        bashfile += 'cd '+ph.setupfolder+'\n'
        bashfile += 'source $AtlasSetup/scripts/asetup.sh %s,%s,here\n' % (ph.version,ph.gcc)
        bashfile += 'cd -\n'
        bashfile += 'cp %s .\n' % self.joboption
        bashfile +='athena.py -c "SkipEvents=%i; EvtMax=%i; FilesInput=%s;" ' % \
                (ph.skipevts,ph.nevents,str(self.inputfiles))
        # Introduce a new key with any thing you want to introduce in -c : kw['Name']='value'
        bashfile += self.joboption+" \n"
        bashfile +="\ncp *.root %s/\n" % os.getcwd()
        f=open(self.scriptname+'.sh',"w")
        f.write(bashfile)
        f.close()
        os.chmod(self.scriptname+'.sh',0755)

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
            self.createbashscript(setupfolder=usersetupfolder,\
                    version=athenaversion,\
                    gcc=gcc,skipevts=skipevts,nevents=nevents)
            # Registring the jobs in jobdescription class instances
            self.jobdescription.append( \
                    jobdescription.buildfromjob(foldername,self.scriptname,i)
                    )
            os.chdir(cwd)
            i+=1

    def getlistofjobs(self):
        """..method:: getlistofjobs() -> [ listofjobs ]
        return the list of prepared jobs, if any, None otherwise

        :return: List of jobs prepared
        :rtype:  list(jobdescription)        
        """
        return self.jobdescription

    @staticmethod
    def checkfinishedjob(jobdsc):
        """..method:: checkfinishedjob(jobdsc) -> status
        
        using the datamember 'successjobcode' perform a check
        to the job (jobdsc) to see if it is found the expected
        outputs or success codes
        """
        succesjobcode=['Py:Athena','INFO leaving with code 0: "successful run"']
        import os
        # Athena jobs outpus inside folder defined as:
        folderout = os.path.join(jobdsc.path,'LSFJOB_'+str(jobdsc.ID))
        # outfile
        logout = os.path.join(folderout,"STDOUT")
        if not os.path.isfile(logout):
            if DEBUG:
                print "Not found the logout file '%s'" % logout
            return 'failed'

        f = open(logout)
        lines = f.readlines()
        f.close()
        for i in lines:
            if i.find(succesjobcode[-1]) != -1:
                return 'successed'
        return 'failed' 

    def sethowtocheckstatus(self):
        """..method:: sethowtocheckstatus()
        
        An Athena job has succesfully finished if there is the line
        'Py:Athena            INFO leaving with code 0: "successful run"'
        """
        self.succesjobcode=['Py:Athena','INFO leaving with code 0: "successful run"']



# Concrete jobspec class for athena jobs
jobspec.register(athenajob)


#if __name__ == '__main__':
#    
#    jsins = jobsender('testBjetSliceAthenaTrigRDO.py',
#            '/afs/cern.ch/user/d/duarte/work/public/datasets/mc14_13TeV.177568.'\
#                    'Pythia_AUET2BCTEQ6L1_RPV_vtx2_LSP100_mujets_filtDL_Rmax300.'\
#                    'recon.RDO.e3355_s1982_s2008_r5787_tid04569111_00/*.pool.root.*',njobs=30)
#    
#    jsins.preparejobs()
#
#    print "Send the jobs using this:"
#    print "for i in `echo */*.sh`; do j=`echo $i|cut -d/ -f1`;"\
#	    "echo $j;cd $j; bsub -q 8nh %s; cd ..;  done;" % jsins.__scriptname__
#	

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

### -FIXME:: PROVISIONAL---
def buildfromathenacern(pathregex):
    """
    """
    import os
    import glob
    jobdscrlist = []
    lsfpaths = pathregex+"/LSFJOB_*"
    jobfolders = glob.glob(lsfpaths)
    for _i in jobfolders:
        i = os.path.abspath(_i)
        try:
            id = int(i.split('_')[-1])
        except ValueError:
            raise RuntimeError('The path should contain LSFJOB_*')
        path=os.path.split(i)[0]
        scriptname=os.path.basename(path).split('_')[0]
        jobdscrlist.append(
                jobdescription(ID=id,status='submitted',\
                        path=path,script=scriptname) )
    return jobdscrlist
