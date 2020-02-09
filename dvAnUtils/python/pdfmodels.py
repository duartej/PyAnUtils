#!/usr/bin/env python
""":mod:`pdfmodels` -- ROOT.RooAbsPdf wrappers to be used by samplingprob class
===============================================================================

.. module:: pdfmodels
   :platform: Unix
      :synopsis: ROOT.RooAbsPdf wrappers to be used by the samplingprob class
    .. moduleauthor:: Jordi Duarte-Campderros <jorge.duarte.campderros@cern.ch>

XXX --- TO BE MOVE INTO sifca-utils package --- XXX
"""
import ROOT

from PyAnUtils.pyanfunctions import ExtraOpt

# ------------------  HELPER FUNCTION ---------------------------
def get_ordered_models(family):
    """Returns a list of the available models for a given family
    in complexity order (from simplest to more parameters models)

    Parameters
    ----------
    family: str
        The name of the Pdf family. Valid families are: 
            * negative_binomial
            * negative_binomial_conditional

    Returns
    -------
    pdfs: list(str)
        The ordered list of PDFs belonging to that family, ordered
        from simplest to more complicated
    """
    if family == 'negative_binomial':
        basename = 'negative_binomial_pdf'
        pdfs = [ basename ]
        sumbasename = family
        for i in xrange(2,4):
            istr = str(i)
            pdfs.append( '{0}_{1}sum_pdf'.format(sumbasename,i) )
    elif family == 'negative_binomial_conditional':
        basename = 'negative_binomial_pdf_conditional'
        pdfs = [ basename ]
        sumbasename = 'negative_binomial'
        for i in xrange(2,4):
            istr = str(i)
            pdfs.append( '{0}_{1}sum_pdf_conditional'.format(sumbasename,i) )
    else:
        raise AttributeError("PDFs family '{0}' not implemented "\
                "yet".format(family))
    return pdfs


# ------------------ AVAILABLE MODELS ---------------------------
def negative_binomial_pdf(obs,**kwd):
    # FIXME:: Change names to a more meaninful ones
    """Build a negative binomial ROOT.RooRealPdf 

    Parameters
    ----------
    obs: ROOT.RooRealVar
        The observable associated to the PDF

    k_title, p_title, eff_tr_title: str, optional
        The title to be used for the observables
    kinit, pinit, eff_trinit: int, float, optional
        The initial value of the observable. The default is None
    kmin, pmin, eff_trmin: int, float, optional
        The minimum allowed value. Defaults are 0
    kmax, pmax, eff_trmax: int, float, optional
        The maximum allowed value
        Defaults:
            * kmax = 100
            * pmax, eff_trmax = 1.0

    Returns
    -------
    (nbd,k,p)

    nbd: ROOT.RooGenericPdf
        The negative binomial pdf
    k: ROOT.RooRealVar
        The rate of failures observable
    p: ROOT.RooRealVar
        The success probability observable

    Notes
    -----
    The implementation in ROOT::Math::negative_binomial_pdf(x,p,r):
    .. math::
        :nowrap:

        \begin{equation*}
            f(x;p,n) = \frac{x+n-1}{x}p^n(1-p)^x
        \end{equation*}
    describes the probability to have *x-1* successes and r-failures
    after x+r-1 trials. 
    
    Note that the variable in *f* is the failure (r). Our implementation deals 
    with the success variable, therefore we switch x --> r:
    .. math::
        :nowrap:

        \begin{eqnarray*}
            f(n;p,x) &=& \frac{x+n-1}{n}p^x(1-p)^n\\
            f(n;(1-\varepsilon),x) &=& \frac{x+n-1}{n}(1-\varepsilon)^x\varepsilon^n
        \end{eqnarray*}
    describing now, the probability of having *n* successes and *x-1* failures,
    with a success efficiency (probability) of 
    .. math:: \varepsilon=1-p
    """
    opt = ExtraOpt( [('k','k'), ('k_title','number of failures'), 
        ('kmin',0),('kmax',100),('kinit',None),
        ('p','p'),('p_title','success probability'),
        ('pmin',0.0),('pmax',1.0),('pinit',None),
        ('pdf_name','nbd')] )
    opt.setkwd(kwd)    

    k   = ROOT.RooRealVar(opt.k,opt.k_title,opt.kmin,opt.kmax)
    if opt.kinit:
        k.setVal(opt.kinit)
    
    p   = ROOT.RooRealVar(opt.p,opt.p_title,opt.pmin,opt.pmax)
    if opt.pinit:
        p.setVal(opt.pinit)

    func_str ="ROOT::Math::negative_binomial_pdf({observable},"\
            "(1.0-{p}),{k})".format(observable=obs.GetName(),p=opt.p,k=opt.k)
    
    nbd = ROOT.RooGenericPdf(opt.pdf_name,"Negative Binomial",func_str,
            ROOT.RooArgList(obs,p,k))

    return nbd,k,p

def negative_binomial_pdf_conditional(obs,**kwd):
    """Build a negative binomial ROOT.RooRealPdf using 4-observables.
    This model assumes that this nbp is result of a convolution (conditional
    probability) of a primordial bnp and a binomial pdf (describing Bernoulli
    experiments). Therefore, the parameters of the nbp are obtained via the 
    parameters of the primordial bnp and the binomial

    Parameters
    ----------
    obs: ROOT.RooRealVar
        The observable associated to the PDF

    k_title, p_title, eff_tr_title: str, optional
        The title to be used for the observables
    kinit, pinit, eff_trinit: int, float, optional
        The initial value of the observable. The default is None
    kmin, pmin, eff_trmin: int, float, optional
        The minimum allowed value. Defaults are 0
    kmax, pmax, eff_trmax: int, float, optional
        The maximum allowed value
        Defaults:
            * kmax = 100
            * pmax, eff_trmax = 1.0
    
    Returns
    -------
    (nbd,k,p,eff_tr)

    nbd: ROOT.RooGenericPdf
        The negative binomial pdf
    k: ROOT.RooRealVar
        The rate of failures observable
    p: ROOT.RooRealVar
        The success probability for the primordial bnd
    eff_tr: ROOT.RooRealVar
        The success probability for the binomial
        
    Notes
    -----
    The current negative binomial pdf is assumed to be the output of a conditional
    probability of a primordial negative binomial and a binomial distributions:
    .. math::
        :nowrap:

        \begin{equation*}
          p(n_t;k,\varepsilon,p)=\binom{n_t+k-1}{n_t}
                \left(\frac{p\,\varepsilon}{1-p(1-\varepsilon)}\right)^{n_t}\,
                       \left(\frac{1-p}{1-p(1-\varepsilon)}\right)^k
                       \end{equation*}

        \end{equation*}
    being:
        * p = success probability on the primordial negative binomial
        * k = number of failures on the primordial negative binomial
        * .. math:: \varepsilon \text{ success probability on the binomial pdf)
    
    See Also
    --------
    negative_binomial_pdf: see the implementation notes
    """
    opt = ExtraOpt( [('k','k'), ('k_title','number of failures'), 
        ('kmin',0),('kmax',100),('kinit',None),
        ('p','p'),('p_title','success probability from conditional nbd'),
        ('pmin',0.0),('pmax',1.0),('pinit',None),
        ('eff_tr','eff_tr'), ('eff_tr_title','success probability from conditional binomial'),
        ('eff_trmin',0.0),('eff_trmax',1.0),('eff_trinit',None),        
        ('pdf_name','nbd')] )
    opt.setkwd(kwd)    

    k   = ROOT.RooRealVar(opt.k,opt.k_title,opt.kmin,opt.kmax)
    if opt.kinit:
        k.setVal(opt.kinit)
    
    p   = ROOT.RooRealVar(opt.p,opt.p_title,opt.pmin,opt.pmax)
    if opt.pinit:
        p.setVal(opt.pinit)

    eff_tr = ROOT.RooRealVar(opt.eff_tr,opt.eff_tr_title,opt.eff_trmin,opt.eff_trmax)
    if opt.eff_trinit:
        eff_tr.setVal(opt.eff_trinit)

    # given the value of the pre-fit (pre_fit_p)
    #              or even without pre-fitting
    #              eff_tr = (P/(1-P))*p-1+(P/(1-P))
    # Note that this is the failure probability, therefore
    # the success is P=1-Q
    # =======================================================
    q_total_name = 'p_total'
    q_total_suffix = opt.p.split('_')[-1]
    if q_total_suffix.isdigit():
        q_total_name += '_{0}'.format(q_total_suffix)
    q_total = ROOT.RooFormulaVar(q_total_name,"total success probability",
            "(1.0-{p})/(1.0-{p}*(1.0-{eff_tr}))".format(
                observable=obs.GetName(),p=opt.p,k=opt.k,eff_tr=opt.eff_tr),
            ROOT.RooArgList(p,eff_tr))

    func_str = "ROOT::Math::negative_binomial_pdf({observable},"\
            "{q_total},{k})".format(observable=obs.GetName(),q_total=q_total_name,k=opt.k)
    
    nbd = ROOT.RooGenericPdf(opt.pdf_name,"Negative Binomial",func_str,
            ROOT.RooArgList(obs,q_total,k))

    return nbd,k,p,eff_tr,q_total

def negative_binomial_sum_pdf(obs):
    """Build a negative binomial ROOT.RooRealPdf 

    Parameters
    ----------
    obs: ROOT.RooRealVar
        The observable associated to the PDF

    Returns
    -------
    (nbd,ndb_1,nbd_2,k_1,p_1,k_3,p_2,signalfrac)
    
    Returns
    -------
    (nbd,k,p,eff_tr)

    nbd: ROOT.RooGenericPdf
        The sum of two negative binomial pdf 
    nbd_i: ROOT.RooGenericPdf
        The negative binomial pdf i-component 
    k_i: ROOT.RooRealVar
        The rate of failures observable for the i-nbd component
    p_i: ROOT.RooRealVar
        The success probability for the i-nbd component
    signalfrac: ROOT.RooRealVar
        The relative number of entries of the Displaced Vertex component

    See Also
    --------
    negative_binomial_pdf
    """
    obsname = obs.GetName()

    # first binomial
    nbd_1,k_1,p_1 = negative_binomial_pdf(obs,
            k='k_1',p='p_1',pdf_name='nbd_1')
    # second binomial
    nbd_2,k_2,p_2 = negative_binomial_pdf(obs,
            k='k_2',p='p_2',pdf_name='nbd_2')
    # Plus extra variable
    signalfrac = ROOT.RooRealVar("signalfrac","DV-fraction in the RoIs signal",0.5,0.,1.)
    
    # Two NBD added
    nbd = ROOT.RooAddPdf("signalRoI","Signal RoIS with two populations",
            nbd_1,nbd_2,signalfrac)

    return nbd,nbd_1,nbd_2,k_1,p_1,k_2,p_2,signalfrac

def negative_binomial_sum_pdf_conditional(obs):
    """Build a negative binomial ROOT.RooRealPdf 

    Parameters
    ----------
    obs: ROOT.RooRealVar
        The observable associated to the PDF

    Returns
    -------
    (nbd,ndbDV,nbdbkg,r_DV,e_DV,r_IP_sig,e_IP_sig,signalfrac)

    nbd: ROOT.RooGenericPdf
        The sum of two negative binomial pdf
    nbdDV: ROOT.RooGenericPdf
        The negative binomial pdf component due to the Displaced Vertex
    nbdbkg: ROOT.RooGenericPdf
        The negative binomial pdf component due to the Interaction Point
    r_DV: ROOT.RooRealVar
        The rate of failures observable from the Displaced Vertex
        component
    e_DV: ROOT.RooRealVar
        The success efficiency from the Displaced Vertex component
    r_IP_sig: ROOT.RooRealVar
        The rate of failures observable from the Interaction Point
        component
    e_IP_sig: ROOT.RooRealVar
        The success efficiency from the Interaction Point component
    signalfrac: ROOT.RooRealVar
        The relative number of entries of the Displaced Vertex component

    See Also
    --------
    negative_binomial_pdf
    """
    obsname = obs.GetName()

    # first binomial
    nbd_1,k_1,p_1,eff_tr_1,q_total_1 = negative_binomial_pdf_conditional(obs,
            k='k_1',p='p_1',eff_tr='eff_tr_1',pdf_name='nbd_1')
    # second binomial
    nbd_2,k_2,p_2,eff_tr_2,q_total_2 = negative_binomial_pdf_conditional(obs,
            k='k_2',p='p_2',eff_tr='eff_tr_2',pdf_name='nbd_2')
    # Plus extra variable
    signalfrac = ROOT.RooRealVar("signalfrac","DV-fraction in the RoIs signal",0.5,0.,1.)
    
    # Two NBD added
    nbd = ROOT.RooAddPdf("signalRoI","Signal RoIS with two populations",
            nbd_1,nbd_2,signalfrac)

    return nbd,nbd_1,nbd_2,k_1,p_1,eff_tr_1,k_2,p_2,eff_tr_2,q_total_1,q_total_2,signalfrac

def negative_binomial_Ksum_pdf_conditional(order,obs):
    """Build a sum of k-negative binomial ROOT.RooRealPdf 

    Parameters
    ----------
    obs: ROOT.RooRealVar
        The observable associated to the PDF
    order: int
        The number of NBDs to be summed
    Returns
    -------
    (nbdSum,NBDs,ks,ps,eff_trs,signalfracs)

    nbdSum: ROOT.RooGenericPdf
        The sum of k-negative binomial pdf
    NBDs: tuple(ROOT.RooGenericPdf)
        The negative binomial pdf component due to the Displaced Vertex
    nbdbkg: ROOT.RooGenericPdf
        The negative binomial pdf component due to the Interaction Point
    r_DV: ROOT.RooRealVar
        The rate of failures observable from the Displaced Vertex
        component
    e_DV: ROOT.RooRealVar
        The success efficiency from the Displaced Vertex component
    r_IP_sig: ROOT.RooRealVar
        The rate of failures observable from the Interaction Point
        component
    e_IP_sig: ROOT.RooRealVar
        The success efficiency from the Interaction Point component
    signalfrac: ROOT.RooRealVar
        The relative number of entries of the Displaced Vertex component

    See Also
    --------
    negative_binomial_pdf
    """
    obsname = obs.GetName()

    nbd_s  = []
    k_s    = []
    p_s    = []
    eff_s  = []
    q_tot_s= []
    signalfrac_s = []

    nbdsList = ROOT.RooArgList()
    signalfracList = ROOT.RooArgList()

    for i in xrange(order):
        istr = str(i)
        _nbd,_k,_p,_eff,_q_total = negative_binomial_pdf_conditional(obs,
            k='k_'+istr,p='p_'+istr,eff_tr='eff_tr_'+istr,pdf_name='nbd_'+istr)
        nbd_s.append(_nbd)
        k_s.append(_k)
        p_s.append(_p)
        eff_s.append(_eff)
        q_tot_s.append(_q_total)
        # RooArgLists
        nbdsList.add(_nbd)
        
        if i == 0:
            signalfrac_s.append(None)
        else:
            _sf = ROOT.RooRealVar("signalfrac_"+istr,
                    "fraction of events of the "+istr+" negative binomial",0.5,0.,1.)
            signalfrac_s.append(_sf)
            signalfracList.add(_sf)
        # The k-summ of NBDs
        nbd = ROOT.RooAddPdf("nbd_add_"+str(order),str(order)+" populations",
                nbdsList,signalfracList)
    
    return nbd,nbd_s,k_s,p_s,eff_s,q_tot_s,signalfrac_s

# Cannot be done automatically?
def negative_binomial_2sum_pdf_conditional(obs):
    return negative_binomial_Ksum_pdf_conditional(2,obs)
def negative_binomial_3sum_pdf_conditional(obs):
    return negative_binomial_Ksum_pdf_conditional(3,obs)
def negative_binomial_4sum_pdf_conditional(obs):
    return negative_binomial_Ksum_pdf_conditional(4,obs)
def negative_binomial_5sum_pdf_conditional(obs):
    return negative_binomial_Ksum_pdf_conditional(5,obs)


def double_gauss(mass,**opt):
    """Build a double gaussian with same mean and different variance plus
    a polynomial background (first order Chebychev)

    FIXME: CHANGE NAME double_gauss_plus_polynomial

    Parameters
    ----------
    nass: ROOT.RooRealVar
        The observable associated to the PDF
    
    opt: dict(), optional
        the keyword dictionary intended to be used for the initial
        values for the parameters of the PDF. See below

    low_mass: 350.0, range (low) for the observable
    high_mass: 650, range (up) for the observable
    mean: 497.0,  gaussian initial mean
    low_mean: 490.0, mean parameter minimum
    high_mean: 510., mean parameter maximum
    sgm_narrow: 5.0, narrow variance initial value
    low_sgm_narrow: 0.01, narrow variance minimum
    high_sgm_narrow: 10.0, narrow variance maximum
    sgm_broad': 10.0, broad variance initial value
    low_sgm_broad: 2.0, broad variance minimum
    high_sgm_broad: 25.0, broad variance maximum
    frac_gauss_nw: 0.8, fraction of events corresponding to 
        the narrow gaussian in the sum of the double gaussian 
    low_frac_gauss_nw: 0.0, fraction of events narrow minimum
    high_frac_gauss_nw: 1.0, fraction of events narrow maximum
    c0_bkg: 1.0,  order 0 Chebychev coefficient initial value
    low_c0_bkg: -1.0, order 0 Chebychev coefficient minimum
    high_c0_bkg: 1.0, order 0 Chebychev coefficient maximum
    c1_bkg: 0.1, order 1 Chebychev coefficient initial value
    low_c1_bkg -1.0, order 1 Chebychev coefficient minimum
    high_c1_bkg: 1.0, order 1 Chebychev coefficient maximum
    nsig': 0.5*1e9, number of events correspondint to the double gauss
    low_nsig: 0.0, number of events for double gauss minimum
    high_nsig: 1.0*2e9, number of events DG maximum
    nbkg: 0.5*1e9, number of events for the Chebychev initial value
    low_nbkg: 0.0 , number of events for the Chebychev minimum
    high_nbkg: 1.0*2e9, number of events for the Chebychev maximum
    
    
    Returns
    -------
    (model,esig,sig,sig_narrow,sig_broad,
    ebkg,bkg,nsig,nbkg,mean,sgm_narrow,sgm_broad,
    frac_gauss_nw,c0_bkg,c1_bkg)

    model: ROOT.RooAddPdf
        The sum of the Double Gaussian and Chebychev 
    esig: ROOT.RooExtendPdf
        The extended DG (used for the model)
    sig: ROOT.RooAddPdf
        The DG 
    sig_narrow, sig_broad: ROOT.RooGaussian
        the two gaussian
    ebkg: ROOT.RooExtendPdf
        The extended Chebychev (used for the model)
    bkg: ROOT.RooChebychev
        The polynomial for the background
    nsig: ROOT.RooRealVar
        The number of events correspoding to the DG
    nbkg: ROOT.RooRealVar
        The number of events correspoding to the Chebychev polynom
    mean: ROOT.RooRealVar
        The mean parameter of the DG
    sgm_narrow: ROOT.RooRealVar
        The variance parameter of one gaussian
    sgm_broad: ROOT.RooRealVar
        The variance parameter of one gaussian
    frac_gausss_nw ROOT.RooRealVar
        The fraction of events corresponding to one of the gaussians
    c0_bkg: ROOT.RooRealVar
        The order 0 coefficient of the Chebychev pol.
    c1_bkg: ROOT.RooRealVar
        The order 1 coefficient of the Chebychev pol.
    """
    defaults = { 'low_mass': 350.0, 'high_mass':650.,
            'mean': 497.0, 'low_mean': 490., 'high_mean': 510.,
            'sgm_narrow': 5.0, 'low_sgm_narrow': 0.01, \
                    'high_sgm_narrow': 10.0,
            'sgm_broad': 10.0, 'low_sgm_broad': 2., \
                    'high_sgm_broad': 25.0,
            'frac_gauss_nw': .8, 'low_frac_gauss_nw': .0, \
                    'high_frac_gauss_nw': 1.,
            'c0_bkg': 1.0, 'low_c0_bkg': -1.0, 'high_c0_bkg': 1.0,
            'c1_bkg': 0.1, 'low_c1_bkg': -1.0, 'high_c1_bkg': 1.0,
            'nsig': 0.5*1e9, 'low_nsig': 0.0, 'high_nsig': 1.0*2e9,
            'nbkg': 0.5*1e9, 'low_nbkg': 0.0, 'high_nbkg': 1.0*2e9
            }
    class final_vals():
        """ empty placeholder 
        """
        def __init__(self):
            pass
    fv = final_vals()

    for key,value in defaults.iteritems():
        if key in opt.keys():
            setattr(fv,key,opt[key])
        else:
            setattr(fv,key,value)
    
    # variables and models declaration
    # ================================
    #mass = ROOT.RooRealVar("mass","Particle Mass",fv.low_mass,\
    #        fv.high_mass,"MeV")
    mean = ROOT.RooRealVar("mean","mean",fv.mean,fv.low_mean,fv.high_mean)
    sgm_narrow = ROOT.RooRealVar("sgm_narrow","sigma1", fv.sgm_narrow,
            fv.low_sgm_narrow,fv.high_sgm_narrow)
    sgm_broad  = ROOT.RooRealVar("sgm_broad","sigma2",fv.sgm_broad,
            fv.low_sgm_broad,fv.high_sgm_broad)
    frac_gauss_nw = ROOT.RooRealVar("frac_gauss_nw","frac narrow Gauss",
            fv.frac_gauss_nw, fv.low_frac_gauss_nw,fv.high_frac_gauss_nw)
    # Two gaussians signal:
    sig_narrow = ROOT.RooGaussian("sig_narrow","Narrow component of "\
            "the signal PDF", mass, mean,sgm_narrow)
    sig_broad = ROOT.RooGaussian("sig_broad","Narrow component of the "\
            " signal PDF", mass, mean,sgm_broad)
    sig = ROOT.RooAddPdf("sig","Signal narrow+broad",
            ROOT.RooArgList(sig_narrow,sig_broad),
            ROOT.RooArgList(frac_gauss_nw))#,frac_gauss_bd))
    
    # Background (flat):    
    c0_bkg = ROOT.RooRealVar("c0_bkg","coeff #0",fv.c0_bkg,
            fv.low_c0_bkg,fv.high_c0_bkg)
    c1_bkg = ROOT.RooRealVar("c1_bkg","coeff #1",fv.c1_bkg,
            fv.low_c1_bkg,fv.high_c1_bkg)
    bkg = ROOT.RooChebychev("bkg","background PDF",mass,
            ROOT.RooArgList(c0_bkg,c1_bkg))

    # Final model
    nsig  = ROOT.RooRealVar("nsig","extended number of signal events",fv.nsig,
            fv.low_nsig,fv.high_nsig)
    nbkg  = ROOT.RooRealVar("nbkg","extended number of background events",fv.nbkg,
            fv.low_nbkg,fv.high_nbkg)
    esig  = ROOT.RooExtendPdf("esig","extended Double Gauss signal",sig,nsig)
    ebkg  = ROOT.RooExtendPdf("ebkg","extended Chebychev background",bkg,nbkg)
    model = ROOT.RooAddPdf("model","Double Gauss (Signal) + Chebychev (Background)",
            ROOT.RooArgList(esig,ebkg))
    #model = ROOT.RooAddPdf("model","Double Gauss (Signal) + Chebychev (Background)",
    #        ROOT.RooArgList(sig,bkg),ROOT.RooArgList(nsig,nbkg))
    # see here
    #https://root.cern.ch/root/html/tutorials/roofit/rf202_extendedmlfit.C.html

    return model,esig,sig,sig_narrow,sig_broad,ebkg,bkg,\
            nsig,nbkg,mean,sgm_narrow,sgm_broad,\
              frac_gauss_nw,c0_bkg,c1_bkg


def langaus(obs,**opt):
    """Build a Landau convoluted with a Gaussian ROOT.RooRealPdf

    Parameters
    ----------
    obs: ROOT.RooRealVar
        The observable associated to the PDF
    
    opt: dict(), optional
        the keyword dictionary intended to be used for the initial
        values for the parameters of the PDF. See below
        
        low_obs: 0.0,   range (low) for the observable
        high_obs: 20,   range (up) for the observable
        mean: 10.0,     MPV-landau initial
        low_mean: 1.0,  mean parameter minimum
        high_mean: 14., mean parameter maximum
        sigma: 2.0,     standard deviation initial value
        low_sigma: 0.01 std. dev. minimum
        low_sigma: 10.0 std. dev. maximum
        sigma_lan: 0.4, Landau sigma initial value (scale parameter)
        low_sigma_lan: 0.0 Landau sigma minimum
        low_sigma_lan: 1.0 Landau sigma maximum

    Returns
    -------
    lang,landau,gaus,mpv,sl,mg,sg

    lang: ROOT.RooFFTConvPdf
        The convolution of the Landau x Gaus
    landau: ROOT.RooLandau
        The Landau distribution related with the particle energy lost
    gaus: ROOT.RooGaussian
        The gauss related with the electronic resolution
    mpv: ROOT.RooRealVar
        The energy lost most probable value in ToT units
    sl: ROOT.RooRealVar
        The scale parameter of the Landau
    mg: ROOT.RooRealVar
        The mean of the gaus (fixed ot zero as it is convoluted, assumed
        no bias in the ToT, just resolution effects)
    sg: ROOT.RooRealVar
        The standard deviation given by the resolution of the electronics 
    """
    defaults = { 'low_obs': 0.0, 'high_obs':20.,
            'mean': 10.0, 'low_mean': 1.0, 'high_mean': 14.,
            'sigma': 2.0, 'low_sigma': 0.01, 'high_sigma': 10.0,
            'sigma_lan': 0.4, 'low_sigma_lan': 0.0, 'high_sigma_lan': 1.0
            }
    obsname = obs.GetName()
    
    class final_vals():
        """ empty placeholder 
        """
        def __init__(self):
            pass
    fv = final_vals()

    for key,value in defaults.iteritems():
        if key in opt.keys():
            setattr(fv,key,opt[key])
        else:
            setattr(fv,key,value)

    # Construct gauss(t,mg,sg)
    # mean gaus
    mg = ROOT.RooRealVar("mg","mg",0)
    sg = ROOT.RooRealVar("sg","sg",fv.sigma,fv.low_sigma,fv.high_sigma)
    gaus = ROOT.RooGaussian("gauss","gauss",obs,mg,sg)

    # The most probable value of the Landau
    mpv = ROOT.RooRealVar("mpv","mpv landau",fv.mean,fv.mean-fv.sigma,fv.mean+fv.sigma)
    # The landau sigma
    sl  = ROOT.RooRealVar("sl","sigma landau",fv.sigma_lan,fv.low_sigma_lan,fv.high_sigma_lan) 
    landau = ROOT.RooLandau("landau","landau",obs,mpv,sl)

    # Contstruct convolution
    #bins to be used for FFT sampling
    obs.setBins(5000,"cache")
    ## Construct landau (x) gauss
    lang = ROOT.RooFFTConvPdf("landxgaus","landau (X) gauss",obs,landau,gaus)

    return lang,landau,gaus,mpv,sl,mg,sg

def langaus_plus_poisson(obs,**opt):
    """Build a Landau convoluted with a Gaussian ROOT.RooRealPdf, plus
    a Poissonian, to take into account a large inefficiency area. In this
    area, the charge carriers can be trapped or suffer different effects 
    and not measuring the whole available energy. 
    XXX --  Poissonan process?? -- XXX

    Parameters
    ----------
    obs: ROOT.RooRealVar
        The observable associated to the PDF
    
    opt: dict(), optional
        the keyword dictionary intended to be used for the initial
        values for the parameters of the PDF. See below
        
        low_obs: 0.0,   range (low) for the observable
        high_obs: 20,   range (up) for the observable
        mean: 10.0,     MPV-landau initial
        low_mean: 1.0,  mean parameter minimum
        high_mean: 14., mean parameter maximum
        sigma: 2.0,     standard deviation initial value
        low_sigma: 0.01 std. dev. minimum
        low_sigma: 10.0 std. dev. maximum
        sigma_lan: 0.4, Landau sigma initial value (scale parameter)
        low_sigma_lan: 0.0 Landau sigma minimum
        low_sigma_lan: 1.0 Landau sigma maximum
        lmbda: 1.0, Poisson scale or mean number of ocurrences
        low_lmbda: 0.01 Poisson scale mininum
        low_lmbda: 2.0  Poisson scale maximum

    Returns
    -------
    lg,lang,poisson,landau,gaus,mpv,sl,mg,sg,lmbda,signalfrac

    lg: ROOT.RooAddPdf
        The langaus + poisson
    lang: ROOT.RooFFTConvPdf
        The convolution of the Landau x Gaus
    poisson: ROOT.RooPoisson
        The Poisson distribution to model the ineficient area
    landau: ROOT.RooLandau
        The Landau distribution related with the particle energy lost
    gaus: ROOT.RooGaussian
        The gauss related with the electronic resolution
    mpv: ROOT.RooRealVar
        The energy lost most probable value in ToT units
    sl: ROOT.RooRealVar
        The scale parameter of the Landau
    mg: ROOT.RooRealVar
        The mean of the gaus (fixed ot zero as it is convoluted, assumed
        no bias in the ToT, just resolution effects)
    sg: ROOT.RooRealVar
        The standard deviation given by the resolution of the electronics 
    lmbda: ROOT.RooRealVar
        The average amount of measured energy in the inefficient region
    signalfrac: ROOT.RooRealVar
        The fraction of landau events over the total
    """
    defaults = { 'low_obs': 0.0, 'high_obs':20.,
            'mean': 10.0, 'low_mean': 1.0, 'high_mean': 14.,
            'sigma': 2.0, 'low_sigma': 0.01, 'high_sigma': 10.0,
            'sigma_lan': 0.4, 'low_sigma_lan': 0.0, 'high_sigma_lan': 1.0,
            'lmbda': 1.0, 'low_lmbda': 0.01, 'high_lmbda': 2.0,
            }
    class final_vals():
        """ empty placeholder 
        """
        def __init__(self):
            pass
    fv = final_vals()

    for key,value in defaults.iteritems():
        if key in opt.keys():
            setattr(fv,key,opt[key])
        else:
            setattr(fv,key,value)
    
    # langaus
    lang,landau,gaus,mpv,sl,mg,sg = langaus(obs,low_obs=fv.low_obs,high_obs=fv.high_obs,
            mean=fv.mean, low_mean=fv.low_mean, high_mean=fv.high_mean,
            sigma=fv.sigma, low_sigma=fv.low_sigma, high_sigma=fv.high_sigma,
            sigma_lan=fv.sigma_lan, low_sigma_lan=fv.low_sigma_lan, high_sigma_lan=fv.high_sigma_lan)
    # Poisson
    # The poisson mean
    lmbda = ROOT.RooRealVar("lambda","lambda poisson",fv.lmbda,fv.low_lmbda,fv.high_lmbda)
    # Note the True to avoid discrete bins
    poisson = ROOT.RooPoisson('bkg','poisson bkg',obs,lmbda,True)
    
    # Plus extra variable
    signalfrac = ROOT.RooRealVar("signalfrac","Fraction of low charge clusters",0.5,0.,1.)
    
    # Adding them
    lg = ROOT.RooAddPdf("clusterToT","Cluster charge with low cluster charge",lang,poisson,signalfrac)

    return lg,lang,poisson,landau,gaus,mpv,sl,mg,sg,lmbda,signalfrac


def langaus_plus_exp(obs,**opt):
    """Build a Landau convoluted with a Gaussian ROOT.RooRealPdf, plus
    a Exponential, to take into account a large inefficiency area. In this
    area, the charge carriers can be trapped or suffer different effects 
    and not measuring the whole available energy. 
    XXX --  Exponential process?? -- XXX

    Parameters
    ----------
    obs: ROOT.RooRealVar
        The observable associated to the PDF
    
    opt: dict(), optional
        the keyword dictionary intended to be used for the initial
        values for the parameters of the PDF. See below
        
        low_obs: 0.0,   range (low) for the observable
        high_obs: 20,   range (up) for the observable
        mean: 10.0,     MPV-landau initial
        low_mean: 1.0,  mean parameter minimum
        high_mean: 14., mean parameter maximum
        sigma: 2.0,     standard deviation initial value
        low_sigma: 0.01 std. dev. minimum
        low_sigma: 10.0 std. dev. maximum
        sigma_lan: 0.4, Landau sigma initial value (scale parameter)
        low_sigma_lan: 0.0 Landau sigma minimum
        low_sigma_lan: 1.0 Landau sigma maximum
        lmbda: 1.0, Exponential mean number of ocurrences
        low_lmbda: 0.01 exp scalemininum
        low_lmbda: 2.0  exp scalemaximum

    Returns
    -------
    lg,lang,exp,landau,gaus,mpv,sl,mg,sg,lmbda,signalfrac

    lg: ROOT.RooAddPdf
        The langaus + poisson
    lang: ROOT.RooFFTConvPdf
        The convolution of the Landau x Gaus
    exp: ROOT.RooExponential
        The Exp distribution to model the ineficient area
    landau: ROOT.RooLandau
        The Landau distribution related with the particle energy lost
    gaus: ROOT.RooGaussian
        The gauss related with the electronic resolution
    mpv: ROOT.RooRealVar
        The energy lost most probable value in ToT units
    sl: ROOT.RooRealVar
        The scale parameter of the Landau
    mg: ROOT.RooRealVar
        The mean of the gaus (fixed ot zero as it is convoluted, assumed
        no bias in the ToT, just resolution effects)
    sg: ROOT.RooRealVar
        The standard deviation given by the resolution of the electronics 
    lmbda: ROOT.RooRealVar
        The average amount of measured energy in the inefficient region
    signalfrac: ROOT.RooRealVar
        The fraction of landau events over the total
    """
    defaults = { 'low_obs': 0.0, 'high_obs':20.,
            'mean': 10.0, 'low_mean': 1.0, 'high_mean': 14.,
            'sigma': 2.0, 'low_sigma': 0.01, 'high_sigma': 10.0,
            'sigma_lan': 0.4, 'low_sigma_lan': 0.0, 'high_sigma_lan': 1.0,
            'lmbda': -1.0, 'low_lmbda': -10.0, 'high_lmbda': 4.0,
            }
    class final_vals():
        """ empty placeholder 
        """
        def __init__(self):
            pass
    fv = final_vals()

    for key,value in defaults.iteritems():
        if key in opt.keys():
            setattr(fv,key,opt[key])
        else:
            setattr(fv,key,value)
    
    # langaus
    lang,landau,gaus,mpv,sl,mg,sg = langaus(obs,low_obs=fv.low_obs,high_obs=fv.high_obs,
            mean=fv.mean, low_mean=fv.low_mean, high_mean=fv.high_mean,
            sigma=fv.sigma, low_sigma=fv.low_sigma, high_sigma=fv.high_sigma,
            sigma_lan=fv.sigma_lan, low_sigma_lan=fv.low_sigma_lan, high_sigma_lan=fv.high_sigma_lan)
    # Exponential
    lmbda = ROOT.RooRealVar("lambda","lambda exp",fv.lmbda,fv.low_lmbda,fv.high_lmbda)
    exp = ROOT.RooExponential('bkg','exponential bkg',obs,lmbda)
    
    # Plus extra variable
    signalfrac = ROOT.RooRealVar("signalfrac","Fraction of low charge clusters",0.5,0.,1.)
    
    # Adding them
    lg = ROOT.RooAddPdf("clusterToT","Cluster charge with low cluster charge",lang,exp,signalfrac)

    return lg,lang,exp,landau,gaus,mpv,sl,mg,sg,lmbda,signalfrac
