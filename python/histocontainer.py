#!/usr/bin/env python
""":module:`histocontainer` -- Helper class for plottin histograms
==================================================================

.. module:: histocontainer    
      :platform: Unix
      :synopsis: Define a container of histograms class mainly 
                 devoted to the plotting of histograms on the 
                 same canvas

       .. scriptauthor:: Jordi Duarte-Campderros <jorge.duarte.campderros@cern.ch>
"""

class HistoContainer():
    """Container of ROOT.THX histograms. The class is useful
    to take care of the plotting of several histos in the same
    canvas, as well as the attribute settings and so on.
    The class is instantiated without arguments and there are
    two main methods to deal with the histogram booking: 
        * bookhisto: to book histograms already present
        * create_and_book_histo: to book histograms which should be
            created by the class
    """
    def __init__(self):
        """The instantiation of this class defines and populates a bunch 
        of useful data-members, the main initializator methods are:
            * bookhisto: to book histograms already present
            * create_and_book_histo: to book histograms which should be
                    created by the class
        """
        from PyAnUtils.pyanfunctions import ExtraOpt
        
        self._histos = {}
        self._usercreated = {}
        self._class  = {}
        self._associated = {}
        self._description= {}
        self._opts   = { 'create_and_book_histo': ExtraOpt( [('npoints_y',None),('ylow',None), ('yhigh',None),
                                    ('npoints_z',None), ('zlow',None), ('zhigh',None),
                                    ('description',''), ('color',None), ('title',''),
                                    ('xtitle',None),('ytitle',None),('ztitle',None)] ),

                          'book_histo': ExtraOpt( [('description',''), ('title',''),
                                    ('color',None),
                                    ('xtitle',None),('ytitle',None),('ztitle',None)] ),

                          'fill': ExtraOpt( [('weight',None)] ),
                          'plot': ExtraOpt( [('options',''), ('legend',True),
                                    ('legposition','RIGHT'),('legy',0.85),('textlength',0.31),
                                    ('normalize',True),
                                    ('log',False),
                                    ('setstyle',False)] )
                          }
    
    def book_histo(self,h,**kwd):
        """Book an ROOT.THX histogram already defined previously by
        the user. The histogram is uniquely identified by the name
        obtained by the ROOT.THX.GetName() method. An exception is
        raised when trying to book two histograms with the same name.
        Note that after the booking, the ROOT.THX object is 
        accesible through the instance attribute defined by the
        ROOT.THX.GetName() method.

        Parameters
        ----------
        name: ROOT.THX
            the histogram object
        title: str, optional
            the title to be put in the histogram, default is obtained
            trhough the method ROOT.THX.GetTitle()
        description: str, optional
            the sentence to be used when the histogram is legended,
            default ''

        Raises
        ------
        KeyError
            if an histogram with the same name already was booked
            
        """
        import ROOT
        from PyAnUtils.pyanfunctions import set_attr_plotobject

        opt = self._opts['book_histo']
        opt.reset()
        opt.setkwd(kwd)
        
        name = h.GetName()
        set_attr_plotobject(h,xtitle=opt.xtitle,ytitle=opt.ytitle,
                ztitle=opt.ztitle,title=opt.title,
                color=opt.color)

        if name in self._histos.keys():
            raise KeyError("Histogram name already in used" %  name)
        
        if not opt.title:
            title = h.GetTitle()
        
        self._histos[name] = h
        self._class[name]  = h.ClassName()
        self._description[name] = opt.description
        setattr(self,name,self._histos[name])
        self._usercreated[name] = True

    def create_and_book_histo(self,name,title,npoints,xlow,xhigh,**kwd):
        """Create and book the ROOT.THX histogram uniquely identified 
        by its name, therefore it is not allowed (and raise exception)
        trying to book two histograms with the same name.
        Note that after the booking, the ROOT.THX object is accesible
        through the instance attribute ``name``.

        Parameters
        ----------
        name: str
            the name of the histogram which also the name of a newly created
            attribute, a way to access directly to the ROOT.THX object
        title: str
            the title to be put in the histogram
        npoints: int
            number of bins
        xlow: float
            the lowest x-value 
        xhigh:float
            the maximum x-value 
        npoints_y: int, optional
            number of bins (y-axis) in a TH2/3 histo, default None
        ylow: float
            the lowest value (y-axis) in a TH2/3 histo, default None
        yhigh: float
            the maximum value (y-axis) in a TH2/3 histo, default None
        npoints_z: int, optional
            number of bins (z-axis) in a TH3 histo, default None
        zlow: float
            the lowest value (z-axis) in a TH3 histo, default None
        zhigh: float
            the maximum value (z-axis) in a TH3 histo, default None
        description: str, optional
            the sentence to be used when the histogram is legended,
            default ''
            
        Raises
        ------
        KeyError
            if an histogram with the same name already was booked
        RuntimeError
            if optional npoints_y(z) was used but not their ranges,
            y(z)low and y(z)high
        """
        import ROOT
        from PyAnUtils.pyanfunctions import set_attr_plotobject
        
        opt = self._opts['create_and_book_histo']
        opt.reset()
        opt.setkwd(kwd)
        
        if name in self._histos.keys():
            raise KeyError("Histogram '{0}' already in used".format(name))
        
        if opt.npoints_y: 
            if opt.ylow is None or opt.yhigh is None:
                raise RuntimeError("npoints_y option needs also"\
                        " ylow and yhigh")
            if opt.npoints_z:
                if opt.zlow is None or opt.zhigh is None:
                    raise RuntimeError("npoints_z option needs also"\
                            " zlow and zhigh")
                histoclass = "TH3F"
                h = ROOT.TH3F(name,title,npoints,xlow,xhigh,\
                        opt.npoints_y,opt.ylow,opt.yhigh,\
                        opt.npoints_z,opt.zlow,opt.zhigh)
            else:
                histoclass = "TH2F"
                h = ROOT.TH2F(name,title,npoints,xlow,xhigh,\
                        opt.npoints_y,opt.ylow,opt.yhigh)
        else:
            histoclass = "TH1F"
            h = ROOT.TH1F(name,title,npoints,xlow,xhigh)
        
        set_attr_plotobject(h,xtitle=opt.xtitle,ytitle=opt.ytitle,
                ztitle=opt.ztitle,title=opt.title,
                color=opt.color)
        
        self._histos[name] = h
        setattr(self,name,self._histos[name])
        self._class[name]  = histoclass
        self._description[name] = opt.description
        self._usercreated[name] = False
    
    def removehistos(self,memory=False):
        """Remove the histograms from the class.
        All histograms created with the method
        'create_and_book_histo' are also removed from 
        memory. Those created by the user and booked 
        with the 'book_histo' method are deleted from
        memory if memory=True, otherwise remains in memory
        and can be used.

        Parameters
        ----------
        memory: Bool
            Whether of not remove histograms from memory. 
            Only those not created by this class are affected
            by this method
        """
        for name,h in self._histos.iteritems():
            if not self._usercreated[name] or \
                    (self._usercreated[name] and memory):
                h.Delete()
            delattr(self,name)
            h = None
        names = self._histos.keys()
        for name in names:
            self._histos.pop(name)
    
    def checkhisto(self,name):
        """Method to raise an exception if there is no histograms
        book with the given name

        Parameters
        ----------
        name: str
            Name of the histogram to be checked

        Raises
        ------
            RuntimeError
                if the histogram is not booked
        """
        if name not in self._histos.keys():
            raise RuntimeError("No histogram booked with the name '%s'" % name)

    def associate(self,name,histonamelist):
        """ Associate histograms which are intented to be plotted together 
        in the same ROOT.TCanvas using the method plot. 
        The x,y and z must be the same. 

        Parameters
        ----------
        name: str
            the name of the central histogram (which are going to be 
            associated the list of histos)
        histonamelist: list(str)
            the list of names of the histograms to be associated

        Raises
        ------
            RuntimeError
                if any of the histograms in the list is not book
        """
        self.checkhisto(name)
        for associate_name in histonamelist:
            self.checkhisto(associate_name)
            try:
                self._associated[name] += associate_name
            except KeyError:
                # empty before, so include now the whole list
                self._associated[name] = filter(lambda x: x != name, histonamelist)
                # and we can go out, the work is done
                break
    
    def associated(self,histonamelist):
        """ Associate histograms which are intented to be plotted together 
        in the same ROOT.TCanvas using the method plot. 
        The x,y and z must be the same. 

        TO BE DEPRECATED, see associate above

        Parameters
        ----------
        histonamelist: list(str)
            the list of names of the histograms to be associated

        Raises
        ------
            RuntimeError
                if any of the histograms in the list is not book
        """
        for name in histonamelist:
            self.checkhisto(name)
            self._associated[name] = filter(lambda x: x != name, histonamelist)
            self._associated[name] += [name]

    def getassociated(self,name):
        """Return the full list of histograms associated with this one plus
        itself

        Parameters
        ----------
        name: str
            name of the histogram to obtain its associated

        Return
        ------
            list of the associated histograms, where the first
            element is the name of the current histo
        """
        return [name]+self._associated[name]

    def fill(self,name,x,y=None,z=None,**kwd):
        """Wrapper to the ROOT.THX.Fill method
        TO BE DEPRECATED (probably)

        Parameters
        ---------
        """
        opt = self._opts['fill']
        opt.reset()
        opt.setkwd(kwd)

        self.checkhisto(name)
        if y is not None:
            if z is not None:
                self._histos[name].Fill(x,y,z)
            else:
                self._histos[name].Fill(x,y)
            return 
        self._histos[name].Fill(x)

    def plot(self,name,plotname,canvas=None,**kwd):
        """Plot the histogram and save the ouput in the format
        especified by the suffix of the ``plotname`` argument.
        This method plot in the same canvas not only the histogram
        called but all those which were associated to it. All the
        histograms are provisionally normalized to 1 for the plot.

        Parameters
        ----------
        name: str
            name of the histogram
        plotname: str
            name of the ouput file, should contain the format 'name.suffix'
        canvas: ROOT.TCanvas|None
            a ROOT.TCanvas object where to perform the plot, if None
            is obtained, a ROOT.TCanvas is created inside the function

        options: str
            the options to be deliver to the ROOT.THX.Draw method
        legend: bool
            whether a legend should be drawn
        legposition: str
            the position of the legend, only accepted 'RIGHT' or 'LEFT',
            default 'RIGHT'
        legy: float
            the upper position of the legend in normalized coordinates (0,1),
            default 0.85
        textlength: float
            the length of the legend box, default 0.31
        log: bool
            activate the logarithmic scale in the y-axis 
        """
        from PyAnUtils.pyanfunctions import drawlegend
        from PyAnUtils.plotstyles import setpalette
        
        opt = self._opts['plot']
        opt.reset()
        opt.setkwd(kwd)

        if opt.setstyle:
            from PyAnUtils.plotstyles import setpalette
            stl = njStyle()
            stl.cd()
            #ROOT.gROOT.ForceStyle()
        setpalette('gray')

        self.checkhisto(name)
        
        canvascreatedhere=False
        if not canvas:
            import ROOT
            canvas = ROOT.TCanvas()
            canvascreatedhere=True
        # Check the associated histos to be plot with him
        # and draw the higher y-value as the first one
        orderednames = [name]
        if self._associated.has_key(name):
            unorderednames = self._associated[name]
            # Normalization
            if opt.normalize: 
                oldintegral = dict(map(lambda n: (n,self._histos[n].Integral()),unorderednames))
                __dummy = map(lambda n: self._histos[n].Scale(1.0/oldintegral[n]), unorderednames)
            orderednames   = sorted(unorderednames,key=lambda n: self._histos[n].GetMaximum(),reverse=True)

        self._histos[orderednames[0]].Draw(opt.options)
        for anotherh in orderednames[1:]:
            self._histos[anotherh].Draw("SAME"+opt.options)

        if opt.legend:
            import ROOT
            leg=ROOT.TLegend()
            for n in orderednames:
                leg.AddEntry(self._histos[n],self._description[n],"LF")
                drawlegend(leg,opt.legposition,opt.legy,textlength=opt.textlength)
        canvas.SaveAs(plotname)
        if opt.log:
            canvas.SetLogy()
            canvas.SaveAs(plotname.replace(".","_log."))
        # Deattach the legend from this canvas, otherwise violation segmentation
        canvas.Clear()
        leg.Delete()
        del leg
        if canvascreatedhere:
            del canvas
        # Reset the actual normalization, if there was more than one histo
        if opt.normalize:
            if self._associated.has_key(name):
                __dummy = map(lambda n: self._histos[n].Scale(oldintegral[n]), unorderednames)

