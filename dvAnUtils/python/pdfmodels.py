#!/usr/bin/env python
""":mod:`pdfmodels` -- ROOT.RooAbsPdf wrappers to be used by samplingprob class
===============================================================================

.. module:: pdfmodels
   :platform: Unix
      :synopsis: ROOT.RooAbsPdf wrappers to be used by the samplingprob class
    .. moduleauthor:: Jordi Duarte-Campderros <jorge.duarte.campderros@cern.ch>
"""

# ------------------ AVAILABLE MODELS ---------------------------
def negative_binomial_pdf(obs):
    """Build a negative binomial ROOT.RooRealPdf 

    Parameters
    ----------
    obs: ROOT.RooRealVar
        The observable associated to the PDF

    Returns
    -------
    (nbd,r_IP,e_IP)

    nbd: ROOT.RooGenericPdf
        The negative binomial pdf
    r_IP: ROOT.RooRealVar
        The rate of failures observable
    e_IP: ROOT.RooRealVar
        The success efficiency

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

    r_IP = ROOT.RooRealVar("r_IP","number of no-reconstructed particles",0,100)
    e_IP = ROOT.RooRealVar("e_IP","track reconstruction efficiency of particles from IP",0,1)
    nbd = ROOT.RooGenericPdf("nt_IP","Negative Binomial",
         "ROOT::Math::negative_binomial_pdf("+obs.GetName()+",(1.0-e_IP),r_IP)",
         ROOT.RooArgList(obs,e_IP,r_IP))

    return nbd,r_IP,e_IP

def negative_binomial_sum_pdf(obs):
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

    r_IP_sig = ROOT.RooRealVar("r_IP_sig","number of no-reconstructed particles",0,100)
    e_IP_sig = ROOT.RooRealVar("e_IP_sig","track reconstruction efficiency of particles from IP",0,1)
    nbdbkg = ROOT.RooGenericPdf("nt_IP_DV","Negative Binomial",
         "ROOT::Math::negative_binomial_pdf("+obsname+",(1.0-e_IP_sig),r_IP_sig)",ROOT.RooArgList(obs,e_IP_sig,r_IP_sig))
    
    r_DV = ROOT.RooRealVar("r_DV","number of no-reconstructed particles",0,100)
    e_DV = ROOT.RooRealVar("e_DV","track reconstruction efficiency of particles from DV",0,1)
    nbdDV = ROOT.RooGenericPdf("nt_DV","Negative Binomial",
         "ROOT::Math::negative_binomial_pdf("+obsname+",(1.0-e_DV),r_DV)",ROOT.RooArgList(obs,e_DV,r_DV))
    signalfrac = ROOT.RooRealVar("signalfrac","DV-fraction in the RoIs signal",0.5,0.,1.)

    nbd = ROOT.RooAddPdf("signalRoI","Signal RoIS with two populations",
            nbdDV,nbdbkg,signalfrac)

    return nbd,nbdDV,nbdbkg,r_DV,e_DV,r_IP_sig,e_IP_sig,signalfrac
