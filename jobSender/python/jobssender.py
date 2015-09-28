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

def bookeepingjobs(jobinstance):
    """.. function::bookeepingjobs(listjobs) 
    stores  the list of the jobdescription instances found in 'listjobs' and 
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
    retrieve a shelve object containing jobdescription objects
    """
    import shelve
    d = shelve.open(filename)
    #joblist = d['joblist'] 
    jobinstance = d['jobinstance']

    d.close()
    
    return jobinstance

class jobdescription(object):
    """..class:: jobdescription

    Class to store all the information relative to a job.
    This class is used by the "job" class, which keep a list
    of the tasks (jobdescription instances). The class provides 
    the following information (in parenthesis it is indicated 
    which class is the responsible of filling the datamember):
     * path: the path where the job has been build (jobspec)
     * script: the script to be sended to the cluster (jobspec)
     * ID: job id in the cluster (clusterspec)
     * status: job status in the cluster (clusterspec)
     * index: index of the job (regarding jobspec class)
    """
    def __init__(self,**kw):
        """..class:: jobdescription

        Class to store all the information relative to a job.
        This class is used by the "job" class, which keep a list
        of the tasks (jobdescription instances). The class provides 
        the following information (in parenthesis it is indicated 
        which class is the responsible of filling the datamember):
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

    def __str__(self):
        """..method ::__str__(self)
        representation of a jobdescription
        """
        repr = "<jobdescription instance>: Index:%i, ID:%i, state:%s (%s)" % \
                (self.index,self.ID,self.state,self.status)
        return repr


STATUSCODE  = { 'fail': 31, 'ok': 32}
STATESORDER = [ None, 'configured', 'submitted', 'running', 'finished', 'aborted' ]
NLETTERS = max(map(lambda x: len(str(x)),STATESORDER))
class job(object):
    """
    Class encapsulating a job. A job IS a "clusterspec" 
    plus a "workenv", i.e. a work to be performed in a cluster.
    The class provides the following information (in parenthesis 
    it is indicated which class is the responsible of filling 
    the datamember):
     * path: the path where the job has been build (jobspec)
     * script: the script to be sended to the cluster (jobspec)
     * ID: job id in the cluster (clusterspec)
     * status: job status in the cluster (clusterspec)
     * index: index of the job (regarding jobspec class)
    """
    def __init__(self,cluster,we,**kw):
        """...class:: job(cluster,we) 

        :param cluster: the cluster where the job is sent
        :type  cluster: clusterspec concrete class instance
        :param      we: the type of work the user want to perform
        :type       we: workenv concrete class instance
        """
        self.cluster = cluster
        self.weinst  = we
        self.tasklist= None
        # Dict with keys are ID of the tasks, given the state and 
        # status, therefore no possibility to any task to be with 
        # two different states
        self.taskstates  = {}
        
        # Any extra?
        for _var,_value in kw.iteritems():
            setattr(self,_var,_value)

    def preparejobs(self):
        """..method ::preparejobs()

        wrapper to the workenv method. The tasks
        are initialized
        """
        self.tasklist = self.weinst.preparejobs()

    def submit(self):
        """..method ::submit

        wrapper to the clusterspec method
        """
        for jb in self.tasklist:
            self.cluster.submit(jb)
    
    def resubmit(self,joblist):
        """..method ::resubmit(joblist) 

        wrapper to the clusterspec resubmit method.
        Note that only 'finished' with 'fail' status,
        'aborted' and 'configured' states are sensitives 
        to be resubmitted
        """
        # Get the list of jobs-to-be-resubmitted (jtbr) from the 
        # ('finished','fail') or 'aborted' ones
        jobindexlist = map(lambda x: x.index,joblist)
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

        toresubmit = filter(lambda x: x.index in toresubmitindices,joblist)
        print "Resubmitting jobs..."
        for ik in toresubmit:
            self.cluster.submit(ik)

    def reconfigure(self,joblist):
        """..method ::reconfigure(joblist) 

        reconfigure method, just convert a job from 'None' state
        to 'configure' state
        """
        # Get the list of jobs-to-be-reconfigured (jtbrc) from the submitted ones
        jobindexlist = map(lambda x: x.index,joblist)
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

        toreconfigure = filter(lambda x: x.index in toreconfigureindices,joblist)
        print "Reconfiguring ..."
        for ik in toreconfigure:
            # FIXME: Sure? or must it be called from the self.workenv.reconfigure ??
            #        in this way is more coherent
            ik.state = 'configured'
            ik.status= 'ok'        

    def kill(self,joblist):
        """..method ::kill(joblist) 

        wrapper to the clusterspec kill method.
        Note that only 'submitted' and 'running'
        states are sensitives to killing
        """
        # Get the list of jobs-to-be-killed (jtbk) from the submitted ones
        jobindexlist = map(lambda x: x.index,joblist)
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
        tokill = filter(lambda x: x.index in tokillindices,joblist)
        print "Killing them..."
        for ik in tokill:
            self.cluster.kill(ik)


    def getlistoftasks(self):
        """..method ::getlistoftasks() -> jobdescriptionlist

        return the jobdescription list of instances, i.e. the jobs
        """
        return self.tasklist

    def update(self):
        """..method ::update() 
        update the state and status of the job by looking at
        the state of its tasks
        """
        import sys

        i=0
        point = float(len(self.tasklist))/100.0
        # Just checking in those with possible changing of state
        checkabletasks = filter(lambda x: x.state != 'finished' or
                x.state != 'aborted',self.tasklist)
        for jdsc in checkabletasks:
            i+=1
            # Progress bar 
            sys.stdout.write("\r\033[1;34mINFO\033[1;m Checking job states "+\
                    "[ "+"\b"+str(int(float(i)/point)).rjust(3)+"%]")
            sys.stdout.flush()
            # end progress bar
            self.cluster.getnextstate(jdsc,self.weinst.checkfinishedjob)
            self.taskstates[jdsc.index] = (jdsc.state,jdsc.status)
        print

    def showstates(self):
        """..method ::showstates()
        print a summary of the states and status of the tasks
        """
        #self.__cacheupdate__()
        message = "\033[1;34mINFO\033[1;m List of tasks with state:\n"
        for state in STATESORDER:
            listof = self.getlistofindices(state)
            if listof:
                preformat = " + %"+str(NLETTERS)+"s: %s\n"
                message += preformat % (str(state).upper(),listof)
        print message
        
    def getdictof(self,state):
        """ ..getdictof(state) -> '{ ind1: (ste1,stus1), ...}'
        return a kind sub-dict of taskstates with state==state 
        """
        l = filter(lambda (id,(ste,stus)): ste == state,self.taskstates.iteritems())
        return dict(l)
   
    def getlistofindices(self,state):
        """ ..getlistofindices(state) -> '[ind1, ind2, ...]'
        return a string-like list of all the tasks indexs with the
        given state. Note that the status is coded in color (red is fail,
        green is ok)
        """
        prestatedict = self.getdictof(state)
        if len(prestatedict) == 0:
            return None
        # As all the prestatedict contains the same state, let's skip this 
        # redundance: { 'id': st, ...} 
        statedict = dict( map(lambda (id,(ste,stus)): (id,stus), prestatedict.iteritems()) )
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

        return message



