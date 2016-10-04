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
    def preparejobs(self,extrabash=''):
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

## -- Concrete implementation: Blind job, the user provides everything
class blindjob(workenv):
    """Concrete implementation of a blind job. The user provides a bashscript
    name which corresponds with an actual bashscript in the working folder.
    The expected inputs are formed by:
        * 1 unic bashscript which contains inside %i pattern which is going
        to be substitute per the jobId
        * a list of files following the notation 'filename_i.suff'
        where 'i' stands for the jobID and 'suff' the suffix of the file
    
    Therefore the job splitting is based in the auxiliary files filename_i.suff
    """
    def __init__(self,bashscriptname,specificfile=None,**kw):
        """Concrete implementation of an blind job. 
        
        Parameters
        ----------
        nameofthejob: str
            generic name to this job and the name of an actual bashscript
            which must exist in the working dir 
        specificfile: str
            name of a file which should be used for each job, the file name should 
            contain a number which is associated to the job number: filename_i.suffix
                So the name to be passed should be filename.suffix
        """
        import glob
        from jobssender import getrealpaths,getremotepaths,getevt

        super(blindjob,self).__init__(bashscriptname,**kw)
        try:
            self.bashscript=getrealpaths(bashscriptname+'.sh')[0]
        except IndexError:
            raise RuntimeError('Bash script file not found %s' % bashscriptname)
        
        self.specificfiles = []
        if specificfile:
            self.specificfiles= sorted(glob.glob(specificfile.split('.')[0]+'_*'))
            if len(self.specificfiles) == 0:
                raise RuntimeError('Specific files not found %s' % specificfile)
        
        if kw.has_key('njobs'):
            self.njobs = int(kw['njobs'])
        else:
            self.njobs= 1

    def __setneedenv__(self):
        """..method:: __setneedenv__() 

        Relevant environment in an ATLAS job:
        """
        self.typealias = 'Blind'
        # just dummy
        self.relevantvar = [ ('PWD','echo') ] 

    def preparejobs(self,extra_asetup=''):
        """..method:: preparejobs() -> listofjobs
        
        main function which builds the folder structure
        and the needed files of the job, in order to be
        sent to the cluster
        A folder is created following the notation:
          * JOB_self.jobname_jobdsc.index
          
        """
        import os
        from jobssender import jobdescription

        cwd=os.getcwd()

        jdlist = []
        for i in xrange(self.njobs):
            # create a folder
            foldername = "%sJob_%s_%i" % (self.typealias,self.jobname,i)
            os.mkdir(foldername)
            os.chdir(foldername)
            # create the local bashscript
            self.createbashscript(i=i)
            # Registring the jobs in jobdescription class instances
            jdlist.append( 
                    jobdescription(path=foldername,script=self.jobname,index=i)
                    )
            jdlist[-1].state   = 'configured'
            jdlist[-1].status  = 'ok'
            jdlist[-1].workenv = self
            #self.setjobstate(jdlist[-1],'configuring') ---> Should I define one?
            os.chdir(cwd)

        return jdlist

    def createbashscript(self,**kw):
        """..method:: creatdbashscript()

        the bash script is copied in the local path      
        """
        import shutil
        import os
        import stat
        
        localcopy=os.path.join(os.getcwd(),os.path.basename(self.bashscript))
        if localcopy != self.bashscript:
            shutil.copyfile(self.bashscript,localcopy)
        # And re-point: WHY??
        #self.bashscript=localcopy

        with open(localcopy,"rw") as f:
            lines = f.readlines()
        f.close()
        newlines = map(lambda l: l.replace("%i",str(kw["i"])), lines)

        with open(localcopy,"w") as f1:
            f1.writelines(newlines)
        f1.close()
        # make it executable
        st = os.stat(localcopy)
        os.chmod(localcopy, st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH )

    # DEPRECATED!!
    #def getlistofjobs(self):
    #    """..method:: getlistofjobs() -> [ listofjobs ]
    #    return the list of prepared jobs, if any, None otherwise

    #    :return: List of jobs prepared
    #    :rtype:  list(jobdescription)        
    #    """
    #    return self.joblist

    @staticmethod
    def checkfinishedjob(jobdsc,logfilename):
        """..method:: checkfinishedjob(jobdsc) -> status
        
        using the datamember 'successjobcode' perform a check
        to the job (jobdsc) to see if it is found the expected
        outputs or success codes
        """
        return 'fail' 

    def sethowtocheckstatus(self):
        """TO BE DEPRECATED!!!
        ..method:: sethowtocheckstatus()
        
        empty
        """
        self.succesjobcode=['','']

# Concrete workenv class for blind jobs
workenv.register(blindjob)

## -- Concrete implementation: Athena job
class athenajob(workenv):
    """Concrete implementation of an athena work environment. 
    An athena job could be called in two different modes:
      1. as jobOption-based [jO]
      2. as transformation job [tf]
    In both cases, an athena job should contain:
      * a bashscript name, which defines the cluster jobs, being
      bash script to deliver to the cluster
      * a list of input files
      * and depending of the mode (jO-based or tf):
        - [jO]: a jobOption python script feeding the athena exec
        - [tf]: a python script which contains in a single line (as
        it is) the string to be deliver to the Reco_tf.py exec. In that
        line, the input files related commands must be removed; but
        the output file related commands must be included (i.e. 
        --outputAODFile fileName.root) 
    
    See __init__ method to instatiate the class

    TO BE IMPLEMENTED: Any extra configuration variable to be used
    in the jobOption (via -c), can be introduced with the kw in the
    construction.
    """
    def __init__(self,bashscriptname,joboptionfile,
            inputfiles,athenamode = 'jo',**kw):
        """Instantiation

        Parameters
        ----------
        bashscriptname: str
            name of the bash script argument to the cluster sender command.
            Note that must be without suffix (.sh)
        joboptionfile: str
            path to the python script (jobOption or tf_parameters, depending
            the athena mode)
        inputfiles: str
            comma separated root inputfiles, wildcards are allowed
        athenamode: str, {'jo', 'tf'}
            athena mode, either jobOption-based or transformation job 
            (note default is jobOption mode)

        input_type: str, optional, { 'ESD', 'RAW', 'HITS', 'RDO', 'AOD' }
            only valid with athenamode=='tf'
        output_type: str, optional, 
            only valid with athenamode=='tf'
        evtmax: int, optional
            number of events to be processed
        njobs: int, optional
            number of jobs to be sent
        """
        from jobssender import getrealpaths,getremotepaths,getevt

        super(athenajob,self).__init__(bashscriptname,**kw)
        try:
            self.joboption=getrealpaths(joboptionfile)[0]
        except IndexError:
            raise RuntimeError('jobOption file not found %s' % joboptionfile)
        
        # check if it is a transformation job
        self.isTFJ = (athenamode == 'tf')
        self.useJOFile()
        if athenamode == 'tf':
            # To be extracted from the jobOption
            # ---- input file type
            i_if = self.tf_parameters.find("--input")
            if i_if == -1:
                raise RuntimeError('The jobOption must include the \'--inputTYPEFile\' option')
            self.tf_input_type = self.tf_parameters[i_if:].split()[0].replace("--input","").replace("File","")
            if self.tf_input_type not in [ 'ESD', 'RAW', 'HITS', 'RDO', 'AOD' ]:
                    raise AttributeError("Invalid input type found ='"+self.tf_input_type+"', "\
                            " see help(athenajob.__init__) to get the list of valid input types")
            # ---- output file and tpe
            i_of = self.tf_parameters.find("--output")
            if i_of == -1:
                raise RuntimeError('The jobOption must include the \'--outputTYPEFile\' option')
            self.tf_output_type = self.tf_parameters[i_of:].split()[0].replace("--output","").replace("File","")
            self.outputfile = self.tf_parameters[i_of:].split()[1]

            # --- remove the parameters related input file and outputfile
            removethis = []
            for _idnx in  [i_if, i_of ]:
                removethis.append( ' '.join(self.tf_parameters[_idnx:].split()[:2]) )

            # XXX: re-initialize tf_paramters
            for _rm in removethis:
                self.tf_parameters = self.tf_parameters.replace(_rm,"")
            # -- just to be sure the user do not include some unwanted commands/options
            self.tf_parameters = self.tf_parameters.replace("Reco_tf.py","")

        # Allowing EOS remote files
        if inputfiles.find('root://') == -1:
            self.remotefiles=False
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

    def useJOFile(self):
        """..method:: useJOFile()

        the JobOption is copied in the local path if is a athena job or
        extracted the content if is a transformation job
        """
        if self.isTFJ:
            # if Reco_tf, just extract the content of the file
            with open(self.joboption) as f:
                _params = f.readline()
                self.tf_parameters = _params.replace("\n","")
                f.close()
            return
        # Otherwise, copy it in the local path
        import shutil
        import os
        
        localcopy=os.path.join(os.getcwd(),os.path.basename(self.joboption))
        if localcopy != self.joboption:
            shutil.copyfile(self.joboption,localcopy)
        # And re-point
        self.joboption=localcopy
    
    def jobOption_modification(self):
        """Be sure that the FilesInput and SkipEvents are used
        accordingly in a jo-based
        """
        lines = []
        with open(self.joboption) as f:
            lines = f.readlines()
        # secure and lock the FilesINput and skipEvents provided
        # by the user
        prelines = [ "athenaCommonFlags.FilesInput.set_Value_and_Lock(FilesInput)\n" ,\
                "athenaCommonFlags.SkipEvents.set_Value_and_Lock(SkipEvents)\n",
                "athenaCommonFlags.EvtMax.set_Value_and_Lock(EvtMax)\n"]
        try:
            impline = filter(lambda (i,l): 
                    l.find("from AthenaCommon.AthenaCommonFlags import athenaCommonFlags") == 0, enumerate(lines))[0][0]
        except IndexError:
            print "\033[1;m31WARNING\0331;m Weird jobOption, which does not content the athenaCommonFlags."\
                    " The input files, and skip events options are ignored, be sure that your jobOption"\
                    " contains the proper input files for the job"
            return

        for k in xrange(len(prelines)):
            lines.insert(impline+(k+1),prelines[k])

        with open(self.joboption,"w") as f:
            f.writelines(lines)


    def preparejobs(self,extra_asetup=''):
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
        
        # if is an athena job, be sure that the FilesInput and SkipEvents
        # orders are received and locked, i.e. modify accordingly the JO
        if not self.isTFJ:
            self.jobOption_modification()

        # setting up the folder structure to send the jobs
        # including the bashscripts
        return self.settingfolders(usersetupfolder,athenaversion,compiler,extra_asetup)


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
                self.extra_asetup=''

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
        bashfile += 'source $AtlasSetup/scripts/asetup.sh %s,%s,here %s\n' % (ph.version,ph.gcc,ph.extra_asetup)
        bashfile += 'cd -\n'
        # Create a guard against malformed Workers (those which uses the same $HOME)
        bashfile += 'tmpdir=`mktemp -d`\ncd $tmpdir;\n\n'
        if self.isTFJ:
            # Transformation job
            # convert the list of files into a space separated string (' '.join(self.inputfiles)
            bashfile += 'Reco_tf.py --fileValidation False --maxEvents {0}'\
                    ' --skipEvents {1} --ignoreErrors \'True\' {2} --input{3}File {4} '\
                    '--output{5}File {6}'.format(ph.nevents,ph.skipevts,self.tf_parameters,
                    self.tf_input_type,' '.join(self.inputfiles),self.tf_output_type,self.outputfile)
        else:
            # athena.py jobOption.py job
            bashfile += 'cp %s .\n' % self.joboption
            bashfile +='athena.py -c "SkipEvents=%i; EvtMax=%i; FilesInput=%s;" ' % \
                    (ph.skipevts,ph.nevents,str(self.inputfiles))
            # Introduce a new key with any thing you want to introduce in -c : kw['Name']='value'
            bashfile += self.joboption+" \n"
        bashfile +="\ncp *.root %s/\n" % os.getcwd()
        # remove the tmpdir
        bashfile +="rm -rf $tmpdir\n"
        f=open(self.scriptname,"w")
        f.write(bashfile)
        f.close()
        os.chmod(self.scriptname,0755)

    def settingfolders(self,usersetupfolder,athenaversion,gcc,extra_asetup=''):
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
                    gcc=gcc,skipevts=skipevts,nevents=nevents,extra_asetup=extra_asetup)
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
    def checkfinishedjob(jobdsc,logfilename):
        """..method:: checkfinishedjob(jobdsc) -> status
        
        using the datamember 'successjobcode' perform a check
        to the job (jobdsc) to see if it is found the expected
        outputs or success codes

        FIXME: Static class do not have make use of the self?
        """
        #if self.isTFJ:
        #    succesjobcode=['PyJobTransforms.main','trf exit code 0']
        #else:
        #    succesjobcode=['Py:Athena','INFO leaving with code 0: "successful run"']
        succesjobcode_tf=['PyJobTransforms.main','trf exit code 0']
        succesjobcode_jo=['Py:Athena','INFO leaving with code 0: "successful run"']
        import os
        # Athena jobs outputs inside folder defined as:
        #folderout = os.path.join(jobdsc.path,'LSFJOB_'+str(jobdsc.ID))
        # outfile
        #logout = os.path.join(folderout,"STDOUT")
        # -- defined as logfilename
        logout = os.path.join(jobdsc.path,logfilename)
        if not os.path.isfile(logout):
            if DEBUG:
                print "Not found the logout file '%s'" % logout
            return 'fail'

        f = open(logout)
        lines = f.readlines()
        f.close()
        # usually is in the end of the file
        for i in reversed(lines):
            if i.find(succesjobcode_jo[-1]) != -1:
                return 'ok'
            if i.find(succesjobcode_tf[-1]) != -1:
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
