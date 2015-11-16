#!/usr/bin/env python
""":mod:`pdfmodels` -- ROOT.RooAbsPdf wrappers to be used by samplingprob class
===============================================================================

.. module:: pdfmodels
   :platform: Unix
      :synopsis: ROOT.RooAbsPdf wrappers to be used by the samplingprob class
    .. moduleauthor:: Jordi Duarte-Campderros <jorge.duarte.campderros@cern.ch>
"""

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
    import ROOT
    from PyAnUtils.pyanfunctions import ExtraOpt
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
    import ROOT
    from PyAnUtils.pyanfunctions import ExtraOpt
    
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
    import ROOT
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
    import ROOT
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

