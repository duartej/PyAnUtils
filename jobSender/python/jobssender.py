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
                       to match files --> A STR ONLY
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

def get_evts_metadata(prefix):
    """Obtain or create a shelve file containing the metadata
    describing the events per file found in a folder which contains
    a list of files

    Parameters
    ----------
    prefix: str, the path to be pre-fixed to the '.events_per_file' 

    Return
    ------
    md: dict( { 'evt_file_dict': { '
        
    """
    import shelve
    import os

    # Open the file if exist, otherwise creates an empty dictionary
    kk = shelve.open(os.path.join(prefix,".events_per_file"))
    if kk.has_key('evt_file_dict'):
        md = kk['evt_file_dict'].copy()
    else:
        md = {}
    kk.close()
    return md

def store_evts_metadata(md,prefix):
    """Store a shelve file containing the metadata describing the 
    events per file found in a folder which contains a list of files
    Note that the file is hardcoded to be '.events_per_file'
    
    Parameters
    ------
    md: { 'file0': events, ...}
    prefix: str, the path to be prefixed to the '.events_per_file'
    """
    import shelve
    import os
    
    kk = shelve.open(os.path.join(prefix,'.events_per_file'))
    kk['evt_file_dict'] = md
    kk.close()        

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
    import os

    # First check if there is exist the file in the folder
    # in order to avoid the loading. Let's assume that file contain 
    # the full path
    prefixpath = os.path.dirname(filelist[0])
    md = get_evts_metadata(prefixpath)
    if len(md) > 0:
        nevts = 0
        print "\033[1;34mINFO\033[1;m Extracting events per file using"\
                " the '.events_per_file'. Note you can remove the file to force a"\
                " recalculation"
        # XXX: Also we can do sum(md.values()), but the files are not checked
        #      then... 
        for f in filelist:
            try: 
                nevts += md[f]
            except KeyError:
                print "\033[1;33mWARNING\033[1;m Metafile '.events_per_file'"\
                        " seems to be malformed, did not find '{0}'. "\
                        "Probably '.events_per_file' should be recreated'".format(f)
        if nevts == 0:
            raise RuntimeError("No event was extracted from '.events_per_file'")
        return nevts
    # NOT FOUND THE METADATA, let's evaluate it, and stores a metadata file
    
    if kw.has_key("treename"):
        treename=kw["treename"]
    else:
        treename="CollectionTree"

    if DEBUG:
        print "Loading the root files to obtain the N_{evts} "\
                "[Tree:%s]: " % treename
    t = ROOT.TChain(treename)
    for f in filelist:
        EntriesBefore=int(t.GetEntries())
        t.AddFile(f)
        md[f] = int(t.GetEntries()-EntriesBefore)
    # store metadata
    store_evts_metadata(md,prefixpath)

    return t.GetEntries()   

def bookeepingjobs(jobinstance):
    """.. function::bookeepingjobs(listjobs) 
    stores  the list of the taskdescription instances found in 'listjobs' and 
    which can be accessed using the accesingjobsinfo functions. 
    The function is useful to snapshot the status of the jobs
    amongst other information
    """
    import shelve
    d = shelve.open(".presentjobs",writeback=True)
    #d['joblist'] = listjobs
    d['jobinstance'] = jobinstance

    d.close()

def accessingjobsinfo(filename='.presentjobs'):
    """.. function::accessingjobsinfo(filename) 
    retrieve a shelve object containing taskdescription objects
    """
    import shelve
    d = shelve.open(filename)
    #joblist = d['joblist'] 
    jobinstance = d['jobinstance']

    d.close()
    
    return jobinstance

class taskdescription(object):
    """Class to store all the information relative to a task 
    of a job. This class is used by the "job" class, which 
    keep a list of the tasks (taskdescription instances). The 
    class provides the following information (in parenthesis 
    it is indicated which class is the responsible of filling
    the datamember):
     * path: the path where the job has been build (workenv)
     * script: the script to be sended to the cluster (workenv)
     * ID: job id in the cluster (clusterspec)
     * status: job status in the cluster (clusterspec)
     * index: index of the job (regarding workenv class)
    """
    def __init__(self,**kw):
        """..class:: taskdescription

        Class to store all the information relative to a job.
        This class is used by the "job" class, which keep a list
        of the tasks (taskdescription instances). The class provides 
        the following information (in parenthesis it is indicated 
        which class is the responsible of filling the datamember):

        Attributes
        ----------
        path: str,
            the path where the job has been build (workenv)
        script: str, 
            the script to be sended to the cluster (workenv)
        parentID: int,
            the job id in the batch system
        ID: int[int], 
            the total ID of the task (parentID[index])
        status: str,
            job status in the cluster (clusterspec)
        index: str,
            index of the job (regarding workenv class)
        """
        # I would need to check that the instance is build only
        # throught the buildfromcluster or buildfromjob methods
        # FIXME
        self.path    = None
        self.script  = None
        self.parentID= None
        self.ID      = None
        self.status  = None
        self.state   = None
        self.index   = None
        for _var,_value in kw.iteritems():
            setattr(self,_var,_value)

    def __str__(self):
        """..method ::__str__(self)
        representation of a taskdescription
        """
        repr = "<taskdescription instance>: Index:%i, ID:%s, state:%s (%s)" % \
                (self.index,self.ID,self.state,self.status)
        return repr


STATUSCODE  = { 'fail': 31, 'ok': 32}
STATESORDER = [ None, 'configured', 'submitted', 'running', 'finished', 'aborted' ]
NLETTERS = max(map(lambda x: len(str(x)),STATESORDER))
class job(object):
    """Class encapsulating a job. A job IS a "clusterspec" plus a 
    "workenv", i.e. a work to be performed in a cluster and a list
    of subjobs (or tasks, i.e: taskdescription). The class provides
    the following information (in parenthesis it is indicated which
    class is the responsible of filling the datamember):
     * path: the path where the job has been build (workenv)
     * script: the script to be sended to the cluster (workenv)
     * ID: job id in the cluster (clusterspec)
     * status: job status in the cluster (clusterspec)
     * index: index of the job (regarding workenv class)
    """
    def __init__(self,cluster,we,**kw):
        """Any job is defined by a cluster (the batch system where
        to send the job), a `workenv` (the type of job) and a list
        of taskdescription instances (the actual information of 
        every task in the cluster).

        Parameters
        ----------
        cluster clusterfactory.clustermanager 
            the concrete clustermanager instance
        we: workenvfactory.workenv
            the concrete workenv instance describing what type of jobs
            the user want to send

        Attributes
        ----------
        cluster: clusterfactor.clustermanager concrete instance
        weinst:  woekenvfactory.workenv concrete instance
        tasklist: list(taskdescription)
        jobID: list(int), the parent ID of the job (subsequent 
            retries are appended in the list)
        taskstates: dict(int: (str,str)), for each sub-job, the
            state and the status is given
        """
        self.cluster = cluster
        self.weinst  = we
        self.tasklist= None
        self.jobID   = []
        # XXX: TO BE PROPAGATE FROM THE taskdescription
        self.script  = None
        self.path    = None
        # XXX: OPTIONAL: as sum of its sub-tasks
        self.status  = None
        self.state   = None
        # Dict with keys are ID of the tasks, given the state and 
        # status, therefore no possibility to any task to be with 
        # two different states
        self.taskstates  = {}
        
        # Any extra?
        for _var,_value in kw.iteritems():
            setattr(self,_var,_value)

    def preparejobs(self,asetup_extra):
        """Wrapper to the workenv method. The tasks are initialized
        """
        self.tasklist = self.weinst.preparejobs(self.cluster.array_variable,asetup_extra)
        # obtain the path and the script (common to all tasks)
        self.script = self.tasklist[0].script
        self.path   = self.tasklist[0].path

    def submit(self):
        """Submit the array job, wrapper to the clusterspec method
        """
        self.cluster.submit(self)
    
    def resubmit(self,tasklist):
        """Resubmitting unsuccessful jobs. Note that only 'finished'
        with 'fail' status, 'aborted' and 'configured' states are 
        sensitives to be resubmitted. 

        Parameters
        ----------
        tasklist: list(int)
            the index of the tasks to be submitted
        """
        # Get the list of jobs-to-be-resubmitted (jtbr) from the 
        # ('finished','fail') or 'aborted' ones
        jobindexlist = map(lambda x: x.index,tasklist)
        abortedindexlist  = map(lambda x: x,self.getdictof('aborted').keys())
        configuredindexlist  = map(lambda x: x,self.getdictof('configured').keys())
        finishedindexlist  = map(lambda x: x[0],\
                filter(lambda (ind,(state,status)): status == 'fail', self.getdictof('finished').iteritems()))
        totalindexlist = abortedindexlist+finishedindexlist+configuredindexlist
        toresubmitindices = list(set(jobindexlist).intersection(totalindexlist))
        # Eliminated from the jtbr list the finished (fail) and aborted ones 
        # (picked them up above)
        renmant = set(jobindexlist).difference(toresubmitindices)
        if len(renmant) != 0:
            premessage = "\033[1;33mWARNING\033[1;m JOBS ["
            for i in sorted(renmant):
                premessage+='%i,' % i
            message =  premessage[:-1]
            message += "] are not in 'ABORTED' nor 'FINISHED' (and 'fail') nor 'CONFIGURED'"
            message += " state, resubmit has no sense in them, so they're ignored..."
            print message

        toresubmit = filter(lambda x: x.index in toresubmitindices,tasklist)
        if len(toresubmit) == 0:
            return
        print "Resubmitting jobs..."
        self.cluster.submit(self,toresubmit)

    def reconfigure(self,tasklist):
        """Just convert a job from 'None' state to 'configure' state

        Parameters
        ----------
        tasklist: list(jobsender.taskdescriptor)
        """
        # Get the list of jobs-to-be-reconfigured (jtbrc) from the submitted ones
        jobindexlist = map(lambda x: x.index,tasklist)
        indexlist  = map(lambda x: x,self.getdictof(None).keys())
        toreconfigureindices = list(set(jobindexlist).intersection(indexlist))
        # Eliminated from the jtbrc list the above ones
        renmant = set(jobindexlist).difference(toreconfigureindices)
        # Get the list of jtbrc from the running ones
        if len(renmant) != 0:
            premessage = "\033[1;33mWARNING\033[1;m JOBS ["
            for i in sorted(renmant):
                premessage+='%i,' % i
            message =  premessage[:-1]
            message += "] are not in 'SUBMITTED' nor 'RUNNING' state, kill has"
            message += " no sense in them, so they're ignored..."
            print message

        toreconfigure = filter(lambda x: x.index in toreconfigureindices,tasklist)
        print "Reconfiguring ..."
        for ik in toreconfigure:
            # FIXME: Sure? or must it be called from the self.workenv.reconfigure ??
            #        in this way is more coherent
            ik.state = 'configured'
            ik.status= 'ok'        

    def kill(self,tasklist):
        """Wrapper to the clusterspec kill method.
        Note that only 'submitted' and 'running'
        states are sensitives to killing

        Parameters
        ----------
        tasklist: list(jobsender.taskdescriptor)
        """
        # Get the list of jobs-to-be-killed (jtbk) from the submitted ones
        jobindexlist = map(lambda x: x.index,tasklist)
        sbindexlist  = map(lambda x: x,self.getdictof('submitted').keys())
        tokillsb = list(set(jobindexlist).intersection(sbindexlist))
        # Eliminated from the jtbk list the submitted ones (picked them up above)
        remaining = set(jobindexlist).difference(tokillsb)
        # Get the list of jtbk from the running ones
        runindexlist = map(lambda x: x,self.getdictof('running').keys())
        tokillrn = list(remaining.intersection(runindexlist))
        # Eliminated from the jtbk list the running ones (picked them up above)
        renmant = list(remaining.difference(tokillrn))
        if len(renmant) != 0:
            premessage = "\033[1;33mWARNING\033[1;m JOBS ["
            for i in sorted(renmant):
                premessage+='%i,' % i
            message =  premessage[:-1]
            message += "] are not in 'SUBMITTED' nor 'RUNNING' state, kill has"
            message += " no sense in them, so they're ignored..."
            print message

        tokillindices = tokillsb+tokillrn
        tokill = filter(lambda x: x.index in tokillindices,tasklist)
        print "Killing them..."
        for ik in tokill:
            self.cluster.kill(ik)


    def getlistoftasks(self):
        """Getter to the taskdescription list of instances, 
        i.e. the sub-jobs

        Return
        ------
        list(jobsender.taskdescriptor)
        """
        return self.tasklist

    def update(self):
        """Update the state and status of the tasks
        """
        import sys

        point = float(len(self.tasklist))/100.0
        # Just checking in those with possible changing of state
        checkabletasks = filter(lambda x: x.state != 'finished' or
                x.state != 'aborted',self.tasklist)
        for (i,task) in enumerate(checkabletasks):
            # Progress bar 
            sys.stdout.write("\r\033[1;34mINFO\033[1;m Checking job states "+\
                    "[ "+"\b"+str(int(float(i)/point)).rjust(3)+"%]")
            sys.stdout.flush()
            # end progress bar
            self.cluster.getnextstate(task,self.weinst.checkfinishedjob)
            self.taskstates[task.index] = (task.state,task.status)
        print

    def showstates(self):
        """Print a summary of the states and status of the tasks
        """
        #self.__cacheupdate__()
        message = "\033[1;34mINFO\033[1;m List of tasks with state:\n"
        for state in STATESORDER:
            listof,totaltasks = self.getlistofindices(state)
            if listof:
                decimal_length=len(str(len(self.tasklist)/10))+1
                preformat = " + [#{0} tasks] {1}: {2}\n".\
                        format("{0:"+str(decimal_length)+"d}",\
                         "{1:>"+str(NLETTERS)+"s}","{2}")
                message += preformat.format(totaltasks,state.upper(),listof)
                #preformat = " + [%"+str(len(self.tasklist)+"i tasks] %"+str(NLETTERS)+"s: %s\n"
                #message += preformat % (len(listof),str(state).upper(),listof)
        print message
        
    def getdictof(self,state):
        """ ..getdictof(state) -> '{ ind1: (ste1,stus1), ...}'
        return a kind sub-dict of taskstates with state==state 
        """
        l = filter(lambda (id,(ste,stus)): ste == state,self.taskstates.iteritems())
        return dict(l)
   
    def getlistofindices(self,state):
        """ ..getlistofindices(state) -> '[ind1, ind2, ...]', total_number
        return a string-like list of all the tasks indexs with the
        given state. Note that the status is coded in color (red is fail,
        green is ok)

        XXX: IMPLEMENT TO DEAL WITH A LIST (InSTEAD Of a STATE)
        """
        prestatedict = self.getdictof(state)
        if len(prestatedict) == 0:
            return None,None
        # As all the prestatedict contains the same state, let's skip this 
        # redundance: { 'id': st, ...} 
        statedict = dict( map(lambda (id,(ste,stus)): (id,stus), prestatedict.iteritems()) )
        total_number = len(statedict)
        # Obtaining a list of paired values. The edge are defining intervals
        # of numbers with the same state, note that all the operations are
        # done with the tuples (id,status)
        idinit = sorted(statedict.keys())[0]
        stinit = statedict[idinit]
        currentinit = (idinit,stinit)
        currentlast = currentinit
        compactlist = []
        for id in sorted(statedict.keys())[1:]:
            status = statedict[id]
            if id-1 != currentlast[0] or status != currentlast[1]:
                compactlist.append( (currentinit,currentlast) )
                currentinit = (id,status)
            currentlast = (id,status)
        # last set
        compactlist.append( (currentinit,currentlast) )
        
        premessage = "["
        for ((idi,statusi),(idf,statusf)) in compactlist:
            if idi == idf:
                premessage+= "\033[1;%im%i\033[1;m," % (STATUSCODE[statusi],idi)
            else:
                premessage+= "\033[1;%im%i\033[1;m-" % (STATUSCODE[statusi],idi)
                premessage+= "\033[1;%im%i\033[1;m," % (STATUSCODE[statusf],idf)

        message = premessage[:-1]+"]"

        return message,total_number


