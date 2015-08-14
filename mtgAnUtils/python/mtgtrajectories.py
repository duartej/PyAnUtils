#!/usr/bin/env python
""":module:`mtgtrajectories` -- Geantino shoots related classes
===============================================================

.. module:: mtgtrajectories [OPTIONS]    
      :platform: Unix
      :synopsis: Encapsulates any trajectory followed by a geantino
      through its angles (theta,phi and eta). The material passed-
      through, the links between the geometries used are dealed with
      this class. The module also contains the functions to be used
      when create trajectories from the ROOT files `build_trajectory_list`
      and to deal with trajectory updates (`create_or_update_trajectory`)
      
      .. moduleauthor:: Jordi Duarte-Campderros <jorge.duarte.campderros@cern.ch>
"""

class trajectory:
    """Geantino (particle) trajectories with extra info

    trajectory(_type,theta,phi)

    Parameters
    ----------
    _type: str
        The geometry used. It must be "FULL" or "FAST" only
    theta: float
        The theta angle of the particle momentum
    phi: float
        The phi angle of the particle momentum

    Attributes
    ----------
    _theta: float
        The theta angle of the particle momentum
    _phi: float
        The phi angle of the particle momentum
    _fast: bool
        Indicates if the geometry used was fast simulation
    _full: bool
        Indicates if the geometry used was full simulation
    _origin: str
        The geometry used to simulate that particle ("FULL" or "FAST")
        See also `_full` and `_fast` data members
    _X0: float
        The radiation lenght traversed by the particle
    _mirrortrajectory: weakref(trajectory)
        A reference to the trajectory counterpart of the opposite
        geometry simulation
    _id: int
        An identifier [TO BE DEPRECATED] Can be use directly the
        built-in `id`
    _updates: int
        How many times the trajectory has been updated. This is equivalent
        to how many volumes crossed [TO BE DEPRECATED? It can be used the 
        length of any of the _position lists]
    _x_position: list((float,float))
        Every x position of the trajectory, whenever it crosses a volume
        the input and output
    _y_position: list((float,float))
        Every y position of the trajectory, whenever it crosses a volume
        the input and output
    _z_position: list((float,float))
        Every z position of the trajectory, whenever it crosses a volume
        the input and output

    Methods
    -------
    """
    def __init__(self,_type,theta,phi):
        self._theta = theta
        self._eta   = None
        self._phi   = phi

        self._tolerance = 0.01

        self._fast = False
        self._full = False
        if _type == "FAST":
            self._fast  = True
        elif _type == "FULL":
            self._full = True
        else:
            raise RuntimeError("Not valid type '%s'" % _type)
        self._origin = _type
        self._X0 = 0.0
        self._mirrortrajectory = None

        self._id = id(self)
        self._updates = 0
        self._x_position = []
        self._y_position = []
        self._z_position = []

    def __str__(self):
        out = '<geantino trajectory at theta=%.3f phi=%.3f>\n' % (self._theta,self._phi)
        out += 'Geometry: %s\n' % self.origin()
        out += 'It has counterpart: %s' % (self._mirrortrajectory != None)

        return out

    # FIXME: Incluir eta y phi de tal forma que pueda
    # usar sets en las trajectory list?

    #def __lt__(self,other):
    #    """Ordered with respect theta angle
    #    """
    #    return self.theta() < other.theta()
    #def __le__(self,other):
    #    """Ordered with respect theta angle
    #    """
    #    return self.theta() <= other.theta()
    #def __eq__(self,other):
    #    """Ordered with respect theta angle
    #    """
    #    return self.theta() == other.theta()
    def __eq__(self,other):
        """Ordered with respect eta and phi
        given a tolerance
        """
        from math import sqrt

        if abs(self.eta()-other.eta()) > self._tolerance:
            return False
        if abs(self.phi()-other.phi()) > self._tolerance:
            return False
        if sqrt((self.eta()-other.eta())**2.+
                (self.phi()-other.phi())**2.) > self._tolerance:
            return False
        return True
    #def __ne__(self,other):
    #    """Ordered with respect theta angle
    #    """
    #    return self.theta() != other.theta()
    #def __gt__(self,other):
    #    """Ordered with respect theta angle
    #    """
    #    return self.theta() > other.theta()
    #def __ge__(self,other):
    #    """Ordered with respect theta angle
    #    """
    #    return self.theta() >= other.theta()

    def theta(self):
        """ theta angle getter

        Return
        ------
        float
            theta angle
        """
        return self._theta

    def eta(self):
        """ psudorapidity

        Return
        ------
        float
            pseudorapidity

        Notes
        -----
        The pseudorapidity is defined as .. math:: \eta = -\log{(\tan{(theta/2.0)})}
        """
        from math import pi,log,tan
        self._eta   = -log(tan(self.theta()/2.0))
        
        # Once initialized, re-map  
        self.eta = self._eta_post
        
        return self._eta

    def _eta_post(self):
        """ pseudorapity 
        """
        return self._eta
    
    def phi(self):
        """ phi angle getter

        Return
        ------
        float
            phi angle
        """
        return self._phi

    def getX0(self):
        """Radiation lenght getter

        Return
        ------
        float
            The radiation length
        """
        return self._X0
    
    def origin(self):
        """The name of the geometry used

        Return
        ------
        str
            Name of the geometry used "FULL" or "FAST"
        """
        return self._origin

    
    def match(self,theta,phi,dRMax=0.01):
        """Extend the trajectory from a point (theta,phi) to a 
        circle defined by dRMax, i.e. theta**2 + phi**2 < dRMax**2,
        and check if the input theta and phi are inside the circle

        Parameters
        ----------
        theta: float
            The theta angle
        phi: float
            The phi angle
        dRMax: float, optional [0.05]
            The size of the cone 
        from math import sqrt

        Return
        ------
        bool
            Whether or not the input (theta,phi) point is inside
            the circle defined with this instance
        """
        from math import sqrt

        # FIXME: coherence
        dRMax=self._tolerance

        if abs(self.theta()-theta) > dRMax:
            return False
        if abs(self.phi()-phi) > dRMax:
            return False

        if sqrt((self.theta()-theta)**2.+(self.phi()-phi)**2.) > dRMax:
            return False
        return True

    
    def update(self,x0,xinit,xend):
        """Update the radiation lenght datamember by averaging
        each contribution 

        Parameters
        ----------
        x0: float
            The radiation lenght
        xinit: (float,float,float)
            The x,y,z of the entrace point (at the
            considered update volume)
        xend: (float,float,float)
            The x,y,z of the out point (of the 
            considered updatedv volume)
        """
        # Averaging the radiation lenght
        previousX0 = self._X0
        newX0 = (self._X0+x0)/2.0
        self._X0 = newX0
        self._x_position.append((xinit[0],xend[0]))
        self._y_position.append((xinit[1],xend[1]))
        self._z_position.append((xinit[2],xend[1]))
        self._updates += 1

    def setmirror(self,mirrortraj):
        """Set the input trajectory as mirror trajectory,
        and the mirrored one with this instance

        Parameters
        ----------
        mirrortraj: trajectory instance
            The trajectory to be mirrorwed with this one
        """
        import weakref

        if self._mirrortrajectory and \
                (self._mirrortrajectory()._id == mirrortraj._id):
            return        
        self._mirrortrajectory = weakref.ref(mirrortraj)
        mirrortraj.setmirror(self)

    def getmirror(self):
        """Mirror trajectory getter

        Return
        ------
        trajectory instance
            The mirror trajectory 
        """
        if self._mirrortrajectory:
            return self._mirrortrajectory()
        else:
            return None

    def get_rad_length_diff(self):
        """Get the radiation length difference between this 
        trajectory and its mirror if exists

        Return
        ------
        ntuple with the absolute and relative (with respect this
        instance, i.e., ..math:\frac{X0-X0_{mirror}}{X0}) differences
    
        """
        mirror = self.getmirror()
        if not mirror:
            return 0.0,0.0
        d    = self._X0-mirror.getX0()
        if self._X0 < 1e-10:
            drel = 0.0
        else:
            drel = d/self._X0

        return d,drel


    def number_of_crossed_volumes(self):
        """Number of volumes the trajectory crossed.
        Note that actually is checking how many updates
        have received.
        TO BE DEPRACATED: There is no volumes, what
        it can be checked is how many trajectories were
        found compatibles with the (eta+Delta_eta,phi+Delta_phi)
        cone
        """
        return self._updates

    def get_in_position(self,i):
        """The inner position through the i-volume

        Parameters
        ----------
        i: int
            The number of crossed volume

        Return
        ------
        (x,y,z): (float,float,float)
            The inner position vector
        """
        return (self._x_position[i][0],self._y_position[i][0],
                    self._z_position[i][0])
    
    def get_exit_position(self,i):
        """The exit position from the i-volume

        Parameters
        ----------
        i: int
            The number of crossed volume

        Return
        ------
        (x,y,z): (float,float,float)
            The exit position vector
        """
        return (self._x_position[i][1],self._y_position[i][1],
                    self._z_position[i][1])

def gettreefile(filename):
    """Auxiliary function to create from the input filename,
    the 'particle tree' [TO BE PROMOTED, adding the tree name
    as argument]
    
    Parameters
    ----------
    filename: str
        The ROOT file path

    Return
    ------
    (ROOT.TFile,ROOT.TTree)
    """
    import ROOT
    f = ROOT.TFile(filename)
    if f.IsZombie():
        raise IOError("Root file not found '%s'" % filename)
    t = f.Get('particles')
    return t,f

def getposition(theta,phi,p):
    """The points x,y,z are returned given the magnitud and 
    angles of a vector

    Parameters
    ----------
    theta: float
        The theta angle (in spheric coordinates)
    phi: float
        The phi angle (in spheric coordinates)
    p: float
        The magnitude of the vector

    Return
    ------
    (x,y,z): tuple(float,float,float)
    """
    from math import sin,cos
    
    pt = p*sin(theta)
    return (pt*cos(phi),pt*sin(phi), p*cos(theta))

def create_or_update_trajectory(iEvent,trajectorylist,trajectory_type):
    """A new trajectory is created and is appended to the input 
    trajectory list if there was none trajectory in the input list 
    before matched with the (theta,phi) values of the current
    tree entry. On the other hand, if there is already a trajectory
    with the same (theta,phi)-values it means that was created a 
    particle with the same (inside tolerance) topology. Therefore, 
    the stored trajectory is updated with the radiation length 
    averaged between the measured previously and the current one

    Parameters
    ----------
    iEvent: ROOT.TTree
        The TTree (RPVMCInfoTree) in a valid entry state
    trajectorylist: list(trajectory)
        The list of trajectory instances to be compare with
        the new entries (theta and phi) and update it
        accordingly if needed
    trajectory_type: str
        The geometry type used with the new created trajectory,
        only use "FULL" or "FAST"

    Return
    ------
    trajectorynew: trajectory|None
        The newly created trajectory if it was created, if
        not was created the return value is a None
    """
    _matched = filter(lambda x: x.match(iEvent.pth,iEvent.pph),trajectorylist)
    if len(_matched) == 0:
        trajectorynew = trajectory(trajectory_type,iEvent.pth,iEvent.pph)
        inpoint  = getposition(iEvent.thIn,iEvent.phIn,iEvent.dIn)
        outpoint = getposition(iEvent.thEnd,iEvent.phEnd,iEvent.dEnd)
        trajectorynew.update(iEvent.X0,inpoint,outpoint)
        trajectorylist.append(trajectorynew)
    else:
        for traj in _matched:
            inpoint  = getposition(iEvent.thIn,iEvent.phIn,iEvent.dIn)
            outpoint = getposition(iEvent.thEnd,iEvent.phEnd,iEvent.dEnd)
            traj.update(iEvent.X0,inpoint,outpoint)
        trajectorynew = None

    return trajectorynew

def build_trajectory_lists(fullfilename,fastfilename,verbose=False):
    """Given the full and fast geometries ROOT filenames, a trajectory
    instances list is created for each geometry, by calling the 
    `create_or_update_trajectory` function at each event. 
    Note that only MuonSpectrometer events are stored [this can
    be easly extended to other volumes by entering a new argument in 
    the function]

    Parameters
    ----------
    fullfilename: str
        The path to the ROOT file which contains the RPVMCInfoTree built
        with the FULL geometry (using Geant4 geometry)
    fastfilename: str
        The path to the ROOT file which contains the RPVMCInfoTree built
        with the FAST geometry (using Track Geometry)
    verbose: bool
        Whether to activate the print of extra information about the found
        trajectories. In particular the trajectories with higher differences
        are reported.

    Return
    ------
    tuple(list(trajectory),list(trajectory))
        A 2-tuple with the list of trajectories per each geometry: (full,fast)

    See Also
    --------
    `create_or_update_trajectory`
    """
    import sys
    import os
    from ROOT import TFile

    tfull,rfull = gettreefile(fullfilename)
    #tfull_raw,rfull = gettreefile(fullfilename)
    
    # Just create to associate the copied trees
    #_dummyname = '__d.root'
    #_dummyf = TFile(_dummyname,'RECREATE')

    #_dummyf.cd()
    #tfull = tfull_raw.CopyTree('geoID==4')
    
    # Progress bar
    ipb=0
    point = float(tfull.GetEntries()-1)/100.0
    traj_in_MS_full = []
    for iEvent in tfull:
        ipb +=1 
        # Progress bar 
        sys.stdout.write("\r\033[1;34mINFO\033[1;m Evaluating FULL geometry"+\
                " file [ "+"\b"+str(int(float(ipb)/point)).rjust(3)+"%]")
        sys.stdout.flush()
        # end progress bar
        # Only MS (easy to extend to others)
        if iEvent.geoID == 4:            
            dummy = create_or_update_trajectory(iEvent,traj_in_MS_full,"FULL")
    print
    #rfull.Close()

    #_dummyf.cd()
    tfast,rfast = gettreefile(fastfilename)
    #tfast_raw,rfast = gettreefile(fastfilename)
    #tfast = tfast_raw.CopyTree('geoID==4')
    # Progress bar
    ipb=0
    point = float(tfast.GetEntries()-1)/100.0    
    # - progress bar
    traj_in_MS_fast = []
    for iEvent in tfast:
        ipb +=1 
        # Progress bar 
        sys.stdout.write("\r\033[1;34mINFO\033[1;m Evaluating FAST geometry "+\
                " (and associating with trajectories with FULL) "+\
                " file [ "+"\b"+str(int(float(ipb)/point)).rjust(3)+"%]")
        sys.stdout.flush()
        # Only MS
        if iEvent.geoID == 4:             
            newtrajectory = create_or_update_trajectory(iEvent,traj_in_MS_fast,"FAST")
            # link with the full counterpart (if any)
            if newtrajectory:
                #_matched = filter(lambda x: x.match(newtrajectory.theta(),
                #                newtrajectory.phi()),traj_in_MS_full)
                _matched = filter(lambda x: x == newtrajectory,traj_in_MS_full)
                nmatchs = len(_matched)
                if nmatchs == 1:
                    newtrajectory.setmirror(_matched[0])
                elif nmatchs > 1:
                    print 
                    print "++"*50
                    print "More than one matched!"
                    print "FAST: (%6.4f,%6.4f)" % (newtrajectory.theta(),newtrajectory.phi())
                    for _i in _matched:
                        print "FULL: (%6.4f,%6.4f)" % (_i.theta(),_i.phi())
                    raise RuntimeError("Unexpected number of matched particles!"\
                            " \nMore than one FULL trajectory matches with the same"\
                            " FAST trajectory. The dR cone should be lowered!")
    print
    rfast.Close()
    rfull.Close()
    #_dummyf.Close()
    #os.remove(_dummyname)
    
    # Verbosity
    if verbose:
        SPOTIF = 10.0
        verblist = []
        for traj in traj_in_MS_full:
            if traj.get_rad_length_diff()[1]*100. > SPOTIF \
                    or not traj.getmirror():
                verblist.append(traj)
        ordverb = sorted(verblist,reverse=True)
        message=''
        if len(ordverb) > 0:
            message  = "="*80
            message += "\nSUMMARY OF MAIN DISCREPANCIES\n"
            message += "[relative diff. higher than %i%s and not-found points]\n" % (SPOTIF,"%")
            #message +=  " [%5s,%5s] | %s | %s | %s | %s\n" % \
            #        ('eta','phi', 'rel. diff [%]', 'abs. diff', 'X0 (FULL)', 'X0 (FAST)')
            message +=  " [{0:5},{1:5}] | {2} | {3} | {4} | {5}\n".format('eta','phi',\
                         'rel. diff [%]', 'abs. diff', 'X0 (FULL)', 'X0 (FAST)')
            for traj in ordverb:
                diff,reldiff = traj.get_rad_length_diff()
                reldiff*=100.
                try:
                    x0mirrorfloat = traj.getmirror().getX0()
                    x0mirror = '%10.3f' % x0mirrorfloat
                except AttributeError:
                    x0mirror = 'NOT FOUND'
                message += " [%5.2f,%5.2f]     %6.2f   %11.2f   %10.3f   %10s\n" % \
                    (traj.eta(),traj.phi(), reldiff, diff,traj.getX0(), x0mirror)
            message += "="*80+"\n"
        print message
        with open('summary.txt','w') as _out:
            _out.write(message)

    

    return traj_in_MS_full,traj_in_MS_fast
    
