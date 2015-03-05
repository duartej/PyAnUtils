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
    """ ..class:: clusterspec
    
    Class to deal with an specific cluster (cern/tau/...) cluster.
    This base class serves as placeholder for the concrete implementation
    of a cluster commands, environments,...
    
    Virtual Methods:
     * simulatedresponse (debugging method)
     * getjobidfromcommand
     * getstatefromcommandline
     * done
     * failed
     """
    __metaclass__ = ABCMeta
    
    def __init__(self,joblist,**kw):
        """ ..class:: jobspec
        
        Class to deal with an specific cluster (cern/tau/...) cluster.
        This base class serves as placeholder for the concrete implementation
        of a cluster commands, environments,...
        
        Virtual Methods (to be implemented in the concrete classes):
         * simulatedresponse (debugging method)
         * getjobidfromcommand    
         * getstatefromcommandline
         * failed
         * done
        """
        # If true, do not interact with the cluster, just for debugging
        self.simulate = False
        if kw.has_key('simulate'):
            self.simulate=kw['simulate']
        # Actual command to send jobs
        self.sendcom     = None
        # Extra parameters/option to the command 
        self.extraopt    = []
        # Actual command to obtain the state of a job
        self.statecom    = None
        # Actual command to kill a job
        self.killcom     = None
        # List of jobdescription instances
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

        :param jobdsc: jobdescription instance to be submitted
        :type  jobdsc: jobdescription instance
        """
        from subprocess import Popen,PIPE
        import os
        cwd = os.getcwd()
        # Going to directory of sending
        os.chdir(jobdsc.path)
        # Building the command to send to the shell:
        command = [ self.sendcom ]
        for i in self.extraopt:
            command.append(i)
        command.append(jobdsc.script+'.sh')
        # Send the command
        if self.simulate:
            p = self.simulatedresponse('submit')
        else:
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
        # Updating the state and status of the job
        jobdsc.state  = 'submitted'
        jobdsc.status = 'ok'
        # Coming back to the original folder
        os.chdir(cwd)
    
    def getnextstate(self,jobdsc,checkfinishedjob):
        """..method:: getnextstate() -> nextstate,nextstatus
        check the state and status of the job.

        The life of a job follows the state workflow
        None -> configured -> submitted -> running -> finished
        Per each possible state (and status), just a few commands
        can be used:
        """
        if not jobdsc.state:
            print "Job not configured yet, you should call the"\
                    " jobspec.preparejobs method"            
        elif jobdsc.state == 'submitted' or jobdsc.state == 'running':
            jobdsc.state,jobdsc.status=self.checkstate(jobdsc)
            if jobdsc.state == 'finished':
                if self.simulate:
                    self.status = self.simulatedresponse('finishing')
                else:
                    jobdsc.status = checkfinishedjob(jobdsc)

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
            command = [ self.statecom, str(jobdsc.ID) ]
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
    def __init__(self,joblist=None,**kw):
        """..class:: cerncluster 
        Concrete implementation of the clusterspec class dealing with
        the cluster at cern (usign lxplus as UI)
        """
        super(cerncluster,self).__init__(joblist,**kw)
        self.sendcom   = 'bsub'
        self.statecom  = 'bjobs'
        self.statuskill= 'bkill'
        if kw.has_key('queue'):
            queue = kw['queue']
        else:
            queue = '8nh'
        self.extraopt  += [ '-q', queue ]
    
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
                mess = ("","")
            return mess
        elif action == 'finishing':
            simstatus = [ 'ok','ok','ok','fail','ok','ok','ok']
            return random.choice(simstatus)
        elif action == 'killing':
            return 'configured','ok'
        else:
            raise RuntimeError('Undefined action "%s"' % action)


    def getjobidfromcommand(self,p):
        """..method:: getjobidfromcommand()
        function to obtain the job-ID from the cluster command
        when it is sended (using sendcom)
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
            message+='(athenajob.getstatefromcommandline method).'
            message+='\nWARNING: forcing "aborted" state'
            print message
            return 'aborted','fail'

    def setjobstate(self,jobds,command):
        """..method:: setjobstate(jobds,action) 
        establish the state (and status) of the jobds ('jobdescription' 
        instance) associated to this clusterspec instance, depending
        of the 'command' being executed
        """
        if commad == 'configuring':
            self.joblist[-1].state   = 'configured'
            self.joblist[-1].status  = 'ok'
            self.joblist[-1].jobspec = self
        elif command == 'submitting':
            self.joblist[-1].state   = 'submit'
            self.joblist[-1].status  = 'ok'
        else:
            raise RuntimeError('Unrecognized command "%s"' % command)
    
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
