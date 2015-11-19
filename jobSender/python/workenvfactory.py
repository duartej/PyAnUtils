#!/usr/bin/env python
""":mod:`workenvfactory` -- workenv abstract and concrete classes
=========================================================================

.. module:: workenvfactory
   :platform: Unix
   :synopsis: Module which contains the workenv abstract class and its
              concrete workenv classes.
              The workenv class defines the "work environment" of a job
              which is going to be sent to a cluster. It defines what
              kind of job is, what scripts needs and what requirements
              has. The base class defines the interface, which interacts
              with the client (a clusterspec instance). Each concrete 
              class needs to implement its own details. 
.. moduleauthor:: Jordi Duarte-Campderros <jorge.duarte.campderros@cern.ch>
"""

from abc import ABCMeta
from abc import abstractmethod

DEBUG=True
JOBEVT=500

class workenv(object):
    """ ..class:: workenv
    
    Class defining the "work environment" of a job which is 
    going to be sent to any cluster. It is a base class, which
    is a placeholder of the methods needed to build a concrete 
    implementation of it. 

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
        """..class:: workenv()
        
        Abstract class to deal with a specific kind of job. 
        The following methods have to be implemented in the 
        concrete classes:
          * __setneedenv__
          * preparejobs
          * createbashscript     
          * sethowtocheckjobs 
          * sendjobs    
          * checkjobs 
        """
        # List of enviroment variables that should be defined in the shell
        # relevants to the job [ (environment_var,command_who_set_this_env), 
        # .. ]
        self.relevantvar = None
        # Name of the job type (Athena, ...) similar or probably the same 
        # as the base class
        self.typealias   = None
        # Name of the job
        self.jobname     = bashscriptname.split('.sh')[0]
        # Name of the script to be used to send jobs including the suffix 
        self.scriptname  = bashscriptname+'.sh'

        # set the relevant variables used to check the kind
        # of job is
        self.__setneedenv__()
        # Controling that the concrete method set the 'relevantvar'
        # datamember
        notfoundmess = "the __setneedenv__ class implemented in the class"
        notfoundmess+=" '%s' must inititalize the" % self.__class__.__name__
        notfoundmess+=" datamembers '%s'" 
        if not self.relevantvar:
            raise NotImplementedError(notfoundmess % ('relevantvar'))
        if not self.typealias:
            raise NotImplementedError(notfoundmess % ('typealias'))
        # Check if the enviroment is ok
        isenvset= self.checkenvironment()
        
        # Just error, send it and exit
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

        method to set the datamember 'relevantvar' and the 'typealias'
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

## -- Concrete implementation: Athena job
class athenajob(workenv):
    """..class:: athenajob

    Concrete implementation of an athena work environment. 
    An athena job should contain an jobOption python script which
    feeds the athena.py executable. This jobs needs a list of 
    input files and the probably a list of output files. 
    TO BE IMPLEMENTED: Any extra configuration variable to be used
    in the jobOption (via -c), can be introduced with the kw in the
    construction.
    """
    def __init__(self,bashscriptname,joboptionfile,inputfiles,**kw):
        """..class:: athenajob(nameofthejob[,])

        Concrete implementation of an athena job. 

        :param nameofthejob: generic name to this job. It is used to 
                             populate other data members (script name,...)
        :type  nameofthejob: str
        """
        from jobssender import getrealpaths,getremotepaths,getevt

        super(athenajob,self).__init__(bashscriptname,**kw)
        try:
            self.joboption=getrealpaths(joboptionfile)[0]
        except IndexError:
            raise RuntimeError('jobOption file not found %s' % joboptionfile)
        
        # JobOptions file
        self.makecopyJO()
        
        # Allowing EOS remote files
        if inputfiles.find('root://') == -1:
            self.inputfiles=getrealpaths(inputfiles)
        else:
            self.remotefiles=True
            self.inputfiles,self.evtmax = getremotepaths(inputfiles)

        if len(self.inputfiles) == 0:
            raise RuntimeError('Not found the Athena inputfiles: %s' \
                    % inputfiles)
        
        if kw.has_key('evtmax') and int(kw['evtmax']) != -1:
            self.evtmax = int(kw['evtmax'])
        else:
            if not self.remotefiles:
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
        # followed by the number of events to be processed
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
        """..method:: makecopyJO()

        the JobOption is copied in the local path      
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
        # Obtaining some Athena related-info (asetup,release,...)
        usersetupfolder = self.getuserasetupfolder()
        athenaversion = os.getenv('AtlasVersion')
        compiler      = self.getcompiler()

        # setting up the folder structure to send the jobs
        # including the bashscripts
        return self.settingfolders(usersetupfolder,athenaversion,compiler)


    def getuserasetupfolder(self):
        """..method:: getuserasetupfolder() -> fullnameuser
        get the asetup folder (where the asetup was launch)
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
        import datetime,time

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

        ts = time.time()
        timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        bashfile = '#!/bin/bash\n\n'
        bashfile += '# File created by the %s class [%s]\n\n' % (self.__class__.__name__,timestamp)
        bashfile += 'cd '+ph.setupfolder+'\n'
        bashfile += 'source $AtlasSetup/scripts/asetup.sh %s,%s,here\n' % (ph.version,ph.gcc)
        bashfile += 'cd -\n'
        bashfile += 'cp %s .\n' % self.joboption
        bashfile +='athena.py -c "SkipEvents=%i; EvtMax=%i; FilesInput=%s;" ' % \
                (ph.skipevts,ph.nevents,str(self.inputfiles))
        # Introduce a new key with any thing you want to introduce in -c : kw['Name']='value'
        bashfile += self.joboption+" \n"
        bashfile +="\ncp *.root %s/\n" % os.getcwd()
        f=open(self.scriptname,"w")
        f.write(bashfile)
        f.close()
        os.chmod(self.scriptname,0755)

    def settingfolders(self,usersetupfolder,athenaversion,gcc):
        """..method:: settingfolders()
        create the folder structure to launch the jobs: for each job
        a folder is created following the notation:
          * AthenaJob_self.jobname_jobdsc.index
          
        """
        import os
        from jobssender import jobdescription

        cwd=os.getcwd()

        jdlist = []
        i=0
        for (skipevts,nevents) in self.skipandperform:
            # create a folder
            foldername = "%sJob_%s_%i" % (self.typealias,self.jobname,i)
            os.mkdir(foldername)
            os.chdir(foldername)
            # create the local bashscript
            self.createbashscript(setupfolder=usersetupfolder,\
                    version=athenaversion,\
                    gcc=gcc,skipevts=skipevts,nevents=nevents)
            # Registring the jobs in jobdescription class instances
            jdlist.append( 
                    jobdescription(path=foldername,script=self.jobname,index=i)
                    )
            jdlist[-1].state   = 'configured'
            jdlist[-1].status  = 'ok'
            jdlist[-1].workenv = self
            #self.setjobstate(jdlist[-1],'configuring') ---> Should I define one?
            os.chdir(cwd)
            i+=1

        return jdlist

    # DEPRECATED!!
    #def getlistofjobs(self):
    #    """..method:: getlistofjobs() -> [ listofjobs ]
    #    return the list of prepared jobs, if any, None otherwise

    #    :return: List of jobs prepared
    #    :rtype:  list(jobdescription)        
    #    """
    #    return self.joblist

    @staticmethod
    def checkfinishedjob(jobdsc):
        """..method:: checkfinishedjob(jobdsc) -> status
        
        using the datamember 'successjobcode' perform a check
        to the job (jobdsc) to see if it is found the expected
        outputs or success codes
        """
        succesjobcode=['Py:Athena','INFO leaving with code 0: "successful run"']
        import os
        # Athena jobs outputs inside folder defined as:
        folderout = os.path.join(jobdsc.path,'LSFJOB_'+str(jobdsc.ID))
        # outfile
        logout = os.path.join(folderout,"STDOUT")
        if not os.path.isfile(logout):
            if DEBUG:
                print "Not found the logout file '%s'" % logout
            return 'fail'

        f = open(logout)
        lines = f.readlines()
        f.close()
        for i in lines:
            if i.find(succesjobcode[-1]) != -1:
                return 'ok'
        return 'fail' 

    def sethowtocheckstatus(self):
        """TO BE DEPRECATED!!!
        ..method:: sethowtocheckstatus()
        
        An Athena job has succesfully finished if there is the line
        'Py:Athena            INFO leaving with code 0: "successful run"'
        """
        self.succesjobcode=['Py:Athena','INFO leaving with code 0: "successful run"']



# Concrete workenv class for athena jobs
workenv.register(athenajob)
