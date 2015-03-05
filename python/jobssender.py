#!/usr/bin/env python
""":mod:`jobsender` -- Send jobs to cluster utilities
======================================================

.. module:: jobsender
   :platform: Unix
   :synopsis: Module gathering utilities to deal with sending 
        jobs to a cluster. The utilities of this module are 
        used by the script 'clustermanager', the interface to
        this module.
.. moduleauthor:: Jordi Duarte-Campderros <jorge.duarte.campderros@cern.ch>
"""
DEBUG=True
JOBEVT=500

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

def getremotepaths(remoteinputfiles):
    """..function:: getremotepaths(remoteinputfiles) -> nevents
    
    Given the names of a files in a remote filesystem (EOS), 
    the function return the complete path of all the files
    matching the regular expresion. This function list the available
    files inside a folder using the eos command. 

    :param inputfiles: a str or list of str with regular expressions
                       to match files
    :type inputfiles: str or list(str)

    :return: the real paths or an empty list if no match
    :rtype: list(str)

    """
    if not remoteinputfiles:
        return None

    from subprocess import Popen,PIPE
    import os
    import glob
    # Substitute root://remoteserver//path_blabla -> /path_blablaa
    protocol = remoteinputfiles.split('//')[0]
    remoteserver = remoteinputfiles.split('//')[1]
    inputfiles = remoteinputfiles.replace(protocol+'//'+remoteserver+'//','')
    parentfolder= os.path.dirname(inputfiles)
    mountpoint = inputfiles.split('/')[0]
    if mountpoint.find('/') != -1:
        # SANITY CHECK
        raise RuntimeError('Probably problem with the input files. If you'\
                ' are using a EOS sample, the format is:\n'\
                '     root://eosserver//whateverpath\n'\
                'NOTE the double slash!! (//)')

    # Note that eos is an alias (don't like too much this... but)
    # Anyway it's needed the shell
    # FIXME:: NOTE THAT IS DEPENDENT OF THE EOS CLIENT VERSION!!
    eos = '/afs/cern.ch/project/eos/installation/0.3.84-aquamarine/bin/eos.select'
    command = eos+' ls '+parentfolder
    p = Popen(command,stdout=PIPE,stderr=PIPE,shell=True).communicate()

    if len(p[1]) != 0:
        raise RuntimeError('Problem with the EOS path, didn\'t find any file in'\
                ' "%s"' % parentfolder)
    # fetch the files from the string p[0] (note that the last element is empty)
    remotefiles = map(lambda x: protocol+'//'+remoteserver+'//'+parentfolder+'/'+x,
            p[0].split('\n')[:-1])
    nevents = getevt(remotefiles,treename='CollectionTree')

    return remotefiles,nevents

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

def bookeepingjobs(jobinstance,clusterinstance):
    """.. function::bookeepingjobs(listjobs) 
    stores  the list of the jobdescription instances found in 'listjobs' and 
    which can be accessed using the accesingjobsinfo functions. 
    The function is useful to snapshot the status of the jobs
    amongst other information
    """
    import shelve
    d = shelve.open(".presentjobs",writeback=True)
    #d['joblist'] = listjobs
    d['jobspecinstance'] = jobinstance
    d['clusterspecinstance'] = clusterinstance

    d.close()

def accessingjobsinfo(filename='.presentjobs'):
    """.. function::accessingjobsinfo(filename) 
    retrieve a shelve object containing jobdescription objects
    """
    import shelve
    d = shelve.open(filename)
    #joblist = d['joblist'] 
    jobspecinstance = d['jobspecinstance']
    clusterinstance = d['clusterspecinstance'] 

    d.close()
    
    return jobspecinstance,clusterinstance
    


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
    
    TODO:  jobspec and clusterspec related instances??
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
         * index: index of the job (regarding jobspec class)
        """
        # I would need to check that the instance is build only
        # throught the buildfromcluster or buildfromjob methods
        # FIXME
        self.path   = None
        self.script = None
        self.ID     = None
        self.status = None
        self.state  = None
        self.index  = None
        for _var,_value in kw.iteritems():
            setattr(self,_var,_value)

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


#from clusterfactory import clusterspec
#from workenvfactory import workenv
#
#class jobsender(clusterspec,workenv):
#    """ ..class:: jobsender
#    
#    """
#    __metaclass__ = ABCMeta
#
#    def __init__(self,bashscript,inputfiles=None,**kw):
#        """ ..method:: jobsender(basescript[,inputfiles,maxevts,njobs) ->
#                                                            jobsender instance
#
#        Initialize common datamembers:
#         * bashscript [str]      : bash script name to be send to the cluster
#         * inputfiles [list(str)]: list of the input files names 
#         * outputfiles[list(str)]: list of the output files names (if any)
#         * njobs      [int]      : number of jobs 
#         * maxevts    [int]      : number of events to be processes
#         * jobslist   [lit(int)] : list of the sended jobs (or taks) ID
#
#        :param basescript: the base script from build the jobs
#        :type basescript: str
#        :param inputfiles: str or list of files (can be regex expressions)
#        :type inputfiles: str/list(str)
#        :param maxevts: number of events to process
#        :type maxevts: int
#        :param njobs: number of jobs
#        :type njobs: int
#        """
#        self.bashscript = bashscript
#        self.inputfiles = getrealpath(inputfiles)
#        self.outputfiles= None
#        self.njobs      = None
#        self.maxevts    = None
#        self.jobslist   = None
#
#        if kw.has_key('maxevts'):
#            self.maxevts = int(kw['maxevts'])
#        if kw.has_key("njobs"):
#            self.njobs = int(kw['njobs'])
#
#        if not self.inputfiles:
#            return self
#        
#        # consistency
#        if len(self.inputfiles) == 0:
#            message = "Didn't found any root file in the entered"
#            message +=" location: %s" % str(inputfiles)
#            raise RuntimeError(message)
#
#        if not self.maxevts:
#            self.maxevts = self.getevt(self.inputfiles)
#
#        if not self.njobs:
#            self.njobs = self.maxevts/JOBEVT
#
#        # Get the evtperjob
#        evtperjob = self.__evts2proc__/self.__njobs__
#        # First event:0 last: n-1
#        remainevts = (self.__evts2proc__ % self.__njobs__)-1
#        
#        #Build the list of events
#        for i in xrange(self.__njobs__-1):
#            #self.__evtperjob__.append( (i*evtperjob,(i+1)*evtperjob-1) )
#            self.__evtperjob__.append( (i*evtperjob,evtperjob) )
#        # And the remaining
#        self.__evtperjob__.append( ((self.__njobs__-1)*evtperjob,remainevts) ) 
#
#    @staticmethod
#    def getevt(filelist,**kw):
#        """ ..method:: jobsender.getevt(filelist[,treename]) -> totalevts
#        
#        Getting the number of events contained in a list
#        of files
#
#        :param filelist: the files to look into
#        :type filelist: list(str)
#        :param treename: the name of the tree where to check 
#                         [CollectionTree default]
#        :type treename: str
#
#        ;return: number of events contained in the treename Tree 
#        :rtype: int
#        """
#        try:
#            import cppyy
#        except ImportError:
#            pass
#        import ROOT
#
#        if kw.has_key("treename"):
#            treename=kw["treename"]
#        else:
#            treename="CollectionTree"
#
#        if DEBUG:
#            print "Loading the root files to obtain the N_{evts} "\
#                    "[Tree:%s]: " % treename
#        t = ROOT.TChain(treename)
#        for f in filelist:
#            t.AddFile(f)
#        return t.GetEntries()    
#
## jobsender is a mix-in class of jobspec and clusterspec
#workenv.register(jobsender)
#clusterspec.register(jobsender)
#
#### -FIXME:: PROVISIONAL---
