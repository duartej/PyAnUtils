#!/usr/bin/env python
""":mod:`clusterfactory` -- clusterspec abstract and concrete classes
======================================================================

.. module:: clusterfactory
   :platform: Unix
   :synopsis: Module which contains the clusterspec abstract class
              and its concrete cluster classes.
              The clusterspec classes interact with the cluster in order
              to send, check, retrieve, abort, ... jobs. The 'clusterspec'
              base class contains those methods which are generic in order
              to deal with any kind of cluster, and defines the virtual
              methods which have to be implemented in each class defining
              a concrete cluster. In this way, the clusterspec class can be 
              used as interface to any client which wants to interact with
              a cluster.
              This module can be use to incorporate the concrete clusterspec
              classes.
.. moduleauthor:: Jordi Duarte-Campderros <jorge.duarte.campderros@cern.ch>
"""

from abc import ABCMeta
from abc import abstractmethod

class clusterspec(object):
    """Abstract class to deal with the cluster interaction. The
    commands to send and monotoring jobs to a batch systems are
    encapsulated here. The concrete classes are defined depending
    the batch manager system and therefore, the specific commands
    to be used, the specific environment variables, ...
    """
    __metaclass__ = ABCMeta
    
    def __init__(self,array_variable,**kw):#joblist,**kw):
        """Abstract class to deal with the cluster interaction. The
        commands to send and monotoring jobs to a batch systems are
        encapsulated here. The concrete classes are defined depending
        the batch manager system and therefore, the specific commands
        to be used, the specific environment variables, ...
        
        Attributes
        ----------
        simulate: bool
            whether is a simulation or not
        array_variable: str (NOT IMPLEMENTED, VIRTUAL ATTRIBUTE)
            the name of the environment variable used by the batching
            system to identify an array job
        logout_file: str
            the name of the log output file
        logerr_file: str
            the name of the log error file
        sendcom: str (NOT IMPLEMENTED, VA)
            the name of the command from the batching system to send
            jobs
        extraopt: list(str)
            the options which populate the `sendcom` command
        arrayopt: [str,str]  (NOT IMPLEMENTED, VA)
            the option to deal with the array jobs in the batch system
        arrayformat: (NOT IMPLEMENTED, VA)
            the format of the task jobs (the argument of the array job
            option in the cluster batch system sender command)
        statecom: str (NOT IMPLEMENTED, VA)
            the name of the command to monitor the jobs
        killcom: str (NOT IMPLEMENTED, VA)
            the name of the command to kill jobs
        ID: int  [TO BE DEPRECATED, ACTUALLY NOT NEEDED]
            the identification number of the job in the batch system

        Virtual methods
        ---------------
        simulatedresponse: debugging function
        getjobidfromcommand: extract the job identifier 
        getstatefromcommandline: extract the job state
        failed
        done
        """
        # If true, do not interact with the cluster, just for debugging
        self.simulate = False
        if kw.has_key('simulate'):
            self.simulate=kw['simulate']
        # Name of the standard and error outputfile
        self.array_variable = array_variable
        self.logout_file = "STDOUT.{0}".format(self.array_variable)
        self.logerr_file = "STDERR.{0}".format(self.array_variable)
        # Actual command to send jobs
        self.sendcom     = None
        # Extra parameters/option to the command 
        self.extraopt    = [ '-o', self.logout_file, '-e', self.logerr_file]
        # The option to be used for the array jobs
        self.arrayopt = None
        # The generic format for the array option (i.e, the format for 
        # the arrayopt[0]).  The format will contain a {0} in order to 
        # be used to set the tasks
        self.arrayformat = None
        # Actual command to obtain the state of a job
        self.statecom    = None
        # Actual command to kill a job
        self.killcom     = None
        # List of jobdescription instances
        #self.joblist     = joblist

    def submit(self,jobdsc,taskstosend=None):
        """Send an array job to the cluster.

        Parameters
        ----------
        jobdsc: jobSender.jobssender.job instance
            the job to be submitted
        tasklist: list(jobsender.taskdescriptor) [Default: None)
            the list of tasks to be sent. If None, 
            it will send `self.njobs` tasks
        """
        from subprocess import Popen,PIPE
        import os
        cwd = os.getcwd()
        # Going to directory of sending
        os.chdir(jobdsc.path)
        taskslist = []
        # Filling the missing array info: ("-option","cluster_dep({0}-{1})")
        if taskstosend:
            taskslist = map(lambda x: x.index,taskstosend)
            # Only the given tasks
            self.arrayopt[1] = self.arrayformat.format("%PLACE")
            for _task in taskstosend:
                self.arrayopt[1] = self.arrayopt[1].replace("%PLACE",\
                        "{0},%PLACE".format(_task.index))
            # remove last comma and %PLACE
            self.arrayopt[1] = self.arrayopt[1].replace(",%PLACE","")
        else:
            # No tasks listed, so all the available
            taskslist = map(lambda x: x.index,jobdsc.tasklist)
            self.arrayopt[1] = self.arrayopt[1].format(jobdsc.tasklist[0].index,\
                    jobdsc.tasklist[-1].index)
        # Building the command to send to the shell:
        command = [ self.sendcom ]
        for i in self.extraopt:
            command.append(i)
        for _i in self.arrayopt:
            command.append(_i)
        # FIXME: 
        command.append(jobdsc.script+'.sh') 
        # Send the command
        if self.simulate:
            p = self.simulatedresponse('submit')
        else:
            p = Popen(command,stdout=PIPE,stderr=PIPE).communicate()

        if p[1] != "":
            message = "ERROR from {0}:\n".format(self.sendcom)
            message += p[1]+"\n"
            os.chdir(cwd)
            print "\033[1;31mERROR SENDING JOB TO CLUSTER\033[1;m {0}".format(message)
            self.ID = None
            jobdsc.jobID.append(self.ID)
            for task in jobdsc.tasklist:
                task.status = 'fail'
            os.chdir(cwd)
            return
        ## The job-id is released in the message:
        self.ID = self.getjobidfromcommand(p[0])
        jobdsc.jobID.append(self.ID)
        # FIXME: the compact list of jobs
        print "\033[1;34mINFO\033[1;m: Array job {0} submitted with cluster "\
                "ID: {1}".format(jobdsc.script,jobdsc.jobID[-1])
        if len(jobdsc.jobID) !=1: 
            print "\033[1;34mINFO\033[1;m: Retrying JOB ({0}-attempt)".\
                    format(len(jobdsc.jobID))
        print "\033[1;34mINFO\033[1;m: with {0} tasks: {1}".format(len(taskslist),taskslist)
        # Updating the state and status of the job tasks
        for task in jobdsc.tasklist:
            task.parentID = jobdsc.jobID[-1]
            task.ID       = "{0}[{1}]".format(task.parentID,task.index)
            task.state  = 'submitted'
            task.status = 'ok'
        # Coming back to the original folder
        os.chdir(cwd)
    
    def getnextstate(self,taskdsc,checkfinishedjob):
        """Check the state and status of the job. The life of a job 
        follows the state workflow
            None -> configured -> submitted -> running -> finished
        Per each possible state (and status), just a few commands
        can be used.

        Parameters
        ----------
        taskdsc: jobsender.taskdescriptor
        checkfinishedjob: workenvfactory.workenv.checkfinishedjob 
            the function to check if the job has finished or not
        """
        if not taskdsc.state:
            print "Job not configured yet, you should call the"\
                    " jobspec.preparejobs method"            
        elif taskdsc.state == 'submitted' or taskdsc.state == 'running':
            taskdsc.state,taskdsc.status=self.checkstate(taskdsc)
            if taskdsc.state == 'finished':
                if self.simulate:
                    taskdsc.status = self.simulatedresponse('finishing')
                else:
                    taskdsc.status = checkfinishedjob(taskdsc,self.logout_file)
        #elif (taskdsc.state == 'finished' and taskdsc.status = 'fail') \
        #        or taskdsc.state == 'aborted':

    @abstractmethod
    def simulatedresponse(self,action):
        """..method:: simulatedresponse() -> clusterresponse
        DO NOT USE this function, just for debugging proporses
        method used to simulate the cluster response when an
        action command is sent to the cluster, in order to 
        proper progate the subsequent code.
        """
        raise NotImplementedError("Class %s doesn't implement "\
                "simulatedresponse()" % (self.__class__.__name__))
    
    @abstractmethod
    def getjobidfromcommand(self,p):
        """..method:: getjobidfromcommand()
        
        function to obtain the job-ID from the cluster command
        when it is sended (using sendcom)
        """
        raise NotImplementedError("Class %s doesn't implement "\
                "getjobidfromcommand()" % (self.__class__.__name__))
    
    
    def checkstate(self,jobdsc):
        """..method:: checkstate()
        
        function to check the status of a job (running/finalized/
        aborted-failed,...). 
        """
        from subprocess import Popen,PIPE
        import os
        if jobdsc.state == 'submitted' or jobdsc.state == 'running':
            command = [ self.statecom, "{0}".format(jobdsc.ID) ]
            if self.simulate:
                p = self.simulatedresponse('checking')
            else:
                p = Popen(command,stdout=PIPE,stderr=PIPE).communicate()
            return self.getstatefromcommandline(p)
        else:
            return jobdsc.state,jobdsc.status

    @abstractmethod
    def getstatefromcommandline(self,p):
        """..method:: getstatefromcommandline() -> status
        
        function to obtain the status of a job. Cluster dependent
        """
        raise NotImplementedError("Class %s doesn't implement "\
                 "getstatefromcommandline()" % (self.__class__.__name__))
    
    def kill(self,jobdsc):
        """..method:: kill()
        method to kill running-state jobs.
        """
        from subprocess import Popen,PIPE
        import os
        if jobdsc.state == 'running' or jobdsc.state == 'submitted':
            command = [ self.killcom, str(jobdsc.ID) ]
            if self.simulate:
                p = self.simulatedresponse('killing')
            else:
                p = Popen(command,stdout=PIPE,stderr=PIPE).communicate()
            jobdsc.state  = 'configured'
            jobdsc.status = 'ok'
        else:
            print "WARNING::JOB [%s] not in running or submitted state,"\
                    " kill has no sense" % jobdsc.index


    @abstractmethod
    def failed(self):
        """..method:: failed()
        steering the actions to proceed when a job has failed.
        Depend on the type of cluster
        """
        raise NotImplementedError("Class %s doesn't implement "\
                 "failed()" % (self.__class__.__name__))

    @abstractmethod
    def done(self):
        """..method:: done()
        steering the actions to be done when the job has been complete
        and done. Depend on the type of the cluster
        """
        raise NotImplementedError("Class %s doesn't implement "\
                 "done()" % (self.__class__.__name__))


# --- Concrete class for the CERN cluster (using the lxplus UI)
class cerncluster(clusterspec):
    """..class:: cerncluster
    Concrete implementation of the clusterspec class dealing with
    the cluster at cern (usign lxplus as UI)
    """
    def __init__(self,**kw):
        """..class:: cerncluster 
        Concrete implementation of the clusterspec class dealing with
        the cluster at cern (usign lxplus as UI)
        """
        super(cerncluster,self).__init__("${$LSB_JOBINDEX}",**kw)#joblist,**kw)
        self.sendcom   = 'bsub'
        self.statecom  = 'bjobs'
        self.killcom   = 'bkill'
        if kw.has_key('queue') and kw['queue']:
            queue = kw['queue']
        else:
            queue = '8nh'
        self.extraopt  += [ '-q', queue ]
        # And the array option: 
        self.arrayformat = '"arrayJob[{0}]"'
        self.arrayopt = ['-J', self.arrayformat.format("{0}-{1}") ]
    
    def simulatedresponse(self,action):
        """..method:: simulatedresponse() -> clusterresponse
        DO NOT USE this function, just for debugging proporses
        method used to simulate the cluster response when an
        action command is sent to the cluster, in order to 
        proper progate the subsequent code.
        """
        import random

        if action == 'submit':
            i=xrange(0,9)
            z=''
            for j in random.sample(i,len(i)):
                z+=str(j)
            return ("Job SIMULATED-RESPONSE <%s>" % (z),"")
        elif action == 'checking':
            potentialstate = [ 'submitted', 'running', 'finished', 'aborted',
                    'submitted','running','finished', 'running', 'finished',
                    'running', 'finished', 'finished', 'finished' ]
            # using random to choose which one is currently the job, biasing
            # to finished and trying to keep aborted less probable
            simstate = random.choice(potentialstate)
            if simstate == 'submitted':
                mess = ("JOBID <123456789>:\njob status PEND","")
            elif simstate == 'running':
                mess = ("JOBID <123456789>:\njob status RUN","")
            elif simstate == 'finished':
                mess =  ("Job <123456789> is not found","Job <123456789> is not found")
            elif simstate == 'aborted':
                mess = ("JOBID <123456789>:\njob status EXIT","")
            return mess
        elif action == 'finishing':
            simstatus = [ 'ok','ok','ok','fail','ok','ok','ok']
            return random.choice(simstatus)
        elif action == 'killing':
            return 'configured','ok'
        else:
            raise RuntimeError('Undefined action "%s"' % action)


    def getjobidfromcommand(self,p):
        """Obtain the job-ID from the output returned by the `bsub` 
        command

        Parameters
        ----------
        p: str
            the ouput of the `bsub` command 
        """
        return int(p.split('Job')[-1].split('<')[1].split('>')[0])
    
    def getstatefromcommandline(self,p):
        """..method:: getstatefromcommandline() -> state,status
        function to parse the state of a job
        """
        # bjobs output
        # JOBID USER STAT QUEUE FROM_HOST EXEC_HOST JOB_NAME SUBMIT_TIME

        isfinished=False
        if p[0].find('not found') != -1 or \
                p[1].find('not found') != -1: 
            return 'finished','ok'
        elif p[0].find('JOBID') == 0:
            jobinfoline = p[0].split('\n')[1]
            # Third element
            status = jobinfoline.split()[2]
            if status == 'PEND':
                return 'submitted','ok'
            elif status == 'RUN':
                return 'running','ok'
            elif status == 'DONE':
                return 'finished','ok'
            elif status == 'EXIT':
                return 'aborted','ok'
            else:
                message='I have no idea of the state parsed in the cluster'
                message+=' as "%s". Parser should be updated\n' % status
                message+='WARNING: forcing "None" state'
                print message
                return None,'fail'
        else:
            message='No interpretation yet of the message (%s,%s).' % (p[0],p[1])
            message+='Cluster message parser needs to be updated'
            message+='(cerncluster.getstatefromcommandline method).'
            message+='\nWARNING: forcing "aborted" state'
            print message
            return 'aborted','fail'
    
    def failed(self):
        """..method:: failed()
         
        steering the actions to proceed when a job has failed.
        Depend on the type of cluster
        """
        raise NotImplementedError("Class %s doesn't implement "\
                 "failed()" % (self.__class__.__name__))

    def done(self):
        """..method:: done()
        steering the actions to be done when the job has been complete
        and done. Depend on the type of the cluster
        """
        raise NotImplementedError("Class %s doesn't implement "\
                 "done()" % (self.__class__.__name__))
    
clusterspec.register(cerncluster)


class taucluster(clusterspec):
    """Concrete implementation of the clusterspec class dealing with
    the cluster at Israel T2 (usign t302.hep.tau.ac.il and 
    t302.hep.tau.ac.ilas UI)
    """
    def __init__(self,**kw):#joblist=None,**kw):
        """
        Parameters
        ----------
        queue: str, { 'N', 'P', 'S', 'atlas', 'HEP' }
            the name of the queue, see details and requirements of each
            queue in `qstat -Q -f`

        """
        super(taucluster,self).__init__("${PBS_ARRAYID}",**kw)
        self.sendcom   = 'qsub'
        self.statecom  = 'qstat'
        self.killcom   = 'qdel'
        if kw.has_key('queue') and kw['queue']:
            queue = kw['queue']
        else:
            queue = 'N'
        self.extraopt += [ '-q', queue , '-V' ]
        # Extra options to accomodate
        if kw.has_key('extra_opts') and kw["extra_opts"]:
            for _at in kw['extra_opts'].split(" "):
                self.extraopt.append(_at)
        # And the array option and format
        self.arrayformat = "{0}"
        self.arrayopt = [ "-t", self.arrayformat.format("{0}-{1}") ]
    
    def simulatedresponse(self,action):
        """ DO NOT USE this function, just for debugging proporses
        method used to simulate the cluster response when an
        action command is sent to the cluster, in order to 
        proper progate the subsequent code.

        Parameters
        ----------
        action: str 
            the action to be simulated {'submit','checking','finishing',
            'killing'} 

        Returns
        -------
        clusterresponse: str
            mimic the cluster response of the simulated job depending
            the state and status randomly choosen

        Raises
        ------
        RunTimeError
            if the action parameter is not valid
        """
        import random

        if action == 'submit':
            i=xrange(0,9)
            z=''
            for j in random.sample(i,len(i)):
                z+=str(j)
            return ("{0}.tau-cream.hep.tau.ac.il".format(z),"")
        elif action == 'checking':
            potentialstate = [ 'submitted', 'running', 'finished', 'aborted',
                    'submitted','running','finished', 'running', 'finished',
                    'running', 'finished', 'finished', 'finished' ]
            # using random to choose which one is currently the job, biasing
            # to finished and trying to keep aborted less probable
            simstate = random.choice(potentialstate)
            if simstate == 'submitted':
                mess = ("Job id <123456789>:\n----\nsim the job status Q","")
            elif simstate == 'running':
                mess = ("Job id <123456789>:\n----\nsim the job status R","")
            elif simstate == 'finished':
                mess = ("Job id <123456789>:\n----\nsim the job status C","")
            elif simstate == 'aborted':
                mess = ("Job id <123456789>:\n----\nsim the job status E","")
            return mess
        elif action == 'finishing':
            simstatus = [ 'ok','ok','ok','fail','ok','ok','ok']
            return random.choice(simstatus)
        elif action == 'killing':
            return 'configured','ok'
        else:
            raise RuntimeError('Undefined action "%s"' % action)


    def getjobidfromcommand(self,p):
        """Obtain the job-ID from the cluster command
        when it is sended (using sendcom)
        
        Parameters
        ----------
        p: (str,str)
            tuple corresponding to the return value of the 
            subprocess.Popen.communicate, i.e. (stdoutdata, stderrdat)

        Returns
        -------
        id: int
            the job id 

        Notes
        -----
        The generic job-id is given by a INT.tau-cream.hep.tau.ac.il,
        being INT an integer followed by the server name

        The new attribute `server_name` is created in this method 
        if does not exist before
        """
        # new attribute
        if not hasattr(self,"server_name"):
            self.server_name = '.'.join(p.split('.')[1:])
        return int(p.split('.')[0].replace("[]",""))
    
    def getstatefromcommandline(self,p):
        """parse the state of a job
        
        Parameters
        ----------
        p: (str,str)
            tuple corresponding to the return value of the 
            subprocess.Popen.communicate, i.e. (stdoutdata, stderrdat)

        Returns
        -------
        id: (str,str)
            the state and status

        Notes
        -----
        The way is obtained the status is through the qstat JOBID which
        follows the structure
            Job id          Name    User    Time    Use   Status  Queue
            -----------------------------------------------------------
            JOBID_INT       blah     me      blah   bleh    S     bleah
        """
        # qstat output
        # Job id  Name User Time Use Status Queue

        isfinished=False
        if p[0].find('qstat: Unknown Job Id') != -1 or \
                p[1].find('qstat: Unknown Job Id') != -1: 
            return 'finished','ok'
        elif p[0].find('Job id') == 0:
            # -- second line (after header and a line of -)
            jobinfoline = p[0].split('\n')[2]
            # fourth element
            status = jobinfoline.split()[4]
            if status == 'Q':
                return 'submitted','ok'
            elif status == 'R':
                return 'running','ok'
            elif status == 'C':
                return 'finished','ok'
            elif status == 'E':
                return 'aborted','ok'
            else:
                message='I have no idea of the state parsed in the cluster'
                message+=' as "%s". Parser should be updated\n' % status
                message+='WARNING: forcing "None" state'
                print message
                return None,'fail'
        else:
            message='No interpretation yet of the message (%s,%s).' % (p[0],p[1])
            message+=' Cluster message parser needs to be updated'
            message+='(taucluster.getstatefromcommandline method).'
            message+='\nWARNING: forcing "aborted" state'
            print message
            return 'aborted','fail'
    
    def failed(self):
        """..method:: failed()
         
        steering the actions to proceed when a job has failed.
        Depend on the type of cluster
        """
        raise NotImplementedError("Class %s doesn't implement "\
                 "failed()" % (self.__class__.__name__))

    def done(self):
        """..method:: done()
        steering the actions to be done when the job has been complete
        and done. Depend on the type of the cluster
        """
        raise NotImplementedError("Class %s doesn't implement "\
                 "done()" % (self.__class__.__name__))
    
clusterspec.register(taucluster)


def cluster_builder(**kw):
    """builder checking the running machine and instantiate
    the proper clusterspec class

    See Also
    --------
    cerncluster: the concrete class for the CERN LXBATCH system
    taucluster : the concrete class for the T2 @ TAU 

    Raises
    ------
    NotImplementedError
        whenever this method is called in an unknown machine
    """
    import socket
    machine = socket.gethostname()

    # build the proper cluster depending where we are
    # cern and T2 at tau 
    if machine.find('lxplus') == 0:
        return cerncluster(**kw)
    elif machine.find('tau.ac.il') != -1:
        return taucluster(**kw)
    else:
        raise NotImplementedError("missing cluster for UI: '{0}'".format(machine))             

