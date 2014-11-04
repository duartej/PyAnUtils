#!/usr/bin/env python
# FIXME: Missing documentation
NBINS=500


def drawgraph(gdict,dname,xtitle):
	"""
	"""
	import ROOT
	from PyAnUtils.plotstyles import squaredStyle
    # Avoiding the canvas creation in X
	ROOT.gROOT.SetBatch(1)

	TOLERANCE = 1e-6
	
	ROOT.gStyle.SetLegendBorderSize(0)
	lstyle = squaredStyle()
	lstyle.cd()
	ROOT.gROOT.ForceStyle()
	ROOT.gStyle.SetOptStat(0)

	ymax = max(map(lambda x: 1.01*x.GetYaxis().GetBinUpEdge(x.GetYaxis().GetLast()),
		gdict.values()))
	ymin = 0.0
	xmax = max(map(lambda x: x.GetXaxis().GetBinUpEdge(x.GetXaxis().GetLast()),
		gdict.values()))
	xmin = -xmax
	if xtitle == 'theta':
		xmin = 0.0
	
	c = ROOT.TCanvas()
	hframe = c.DrawFrame(xmin,ymin,xmax,ymax)
	hframe.SetYTitle("Material Length [X_{0}]")
	hframe.SetXTitle("#"+xtitle)
    
	legend = ROOT.TLegend(0.45,0.85,0.75,0.9)
	legend.SetBorderSize(0)
	legend.SetTextSize(0.03)
	legend.SetFillColor(10)
	legend.SetTextFont(112)

	hframe.Draw()
	for simtype,f in gdict.iteritems():
		if simtype == 'fastsim':
			f.SetLineColor(39)
		else:
			f.SetLineColor(1)
		f.Draw("LSAME")
		f.SetFillColor(f.GetLineColor())
		legend.AddEntry(f,simtype,"FL")
	legend.Draw()
	c.SaveAs(dname+"_"+xtitle+".png")

	# Differences (Full-fast)
	# Full 
	npointsfullsim = gdict['fullsim'].GetN()
	xfullsim = gdict['fullsim'].GetX()
	yfullsim = gdict['fullsim'].GetY()
	# Fast
	npointsfastsim = gdict['fastsim'].GetN()
	xfastsim = gdict['fastsim'].GetX()
	yfastsim = gdict['fastsim'].GetY()
	#if npointsfastsim != npointsfullsim:
	#	raise RuntimeError("Number of fast-sim points differ of full-sim")

	diffg = gdict['fastsim'].Clone('diff_'+xtitle+'_'+dname)
	diffg.Set(0)
	diffg.SetLineColor(1)

	# Assuming different number of points
	k = 0
	j_k = 0
	for i in xrange(npointsfullsim):
		_xfull = xfullsim[i]
		_yfull = yfullsim[i]
		for j in xrange(j_k,npointsfastsim):
			_xfast = xfastsim[j]
			_yfast = yfastsim[j]
			if abs(_xfull-_xfast) > TOLERANCE:
				continue
			else:
				diffg.SetPoint(k,_xfull,(_yfull-_yfast))
				k += 1
	
	_dummy = diffg.Draw("A")
	hframediff = diffg.GetHistogram()
	hframediff.SetYTitle("Material Lenght(fullsim-fastsim) [X_{0}]")
	hframediff.SetXTitle("#"+xtitle)
	hframediff.SetLineColor(0)

	hframediff.Draw()
	diffg.Draw("LSAME")

	c.SaveAs(dname+"_"+xtitle+"_diff.png")


def graphtohist(graph,binning=1000):
	"""
	"""
	from ROOT import Double,TH1F
	# Extract limits to build the histo
	xmin = graph.GetXaxis().GetBinLowEdge(graph.GetXaxis().GetFirst())
	xmax = graph.GetXaxis().GetBinUpEdge(graph.GetXaxis().GetLast())
	h = TH1F(graph.GetName()+'_histo','',binning,xmin,xmax)
	xbins = [ h.GetXaxis().GetBinLowEdge(i) for i in xrange(1,h.GetNbinsX()+2) ]
	yval = Double(0.0)
	xval = Double(0.0)
	# dict to count how many entries are pushed in the same bin, in order to
	# make an average later
	hdict = {}
	for i in xrange(graph.GetN()):
		point = graph.GetPoint(i,xval,yval)
		_hbin = h.Fill(xval,yval)
		try:
			hdict[_hbin] +=1 
		except KeyError:
			hdict[_hbin] = 1
	# Let's average the bins with more than one entry
	for b,nentries in hdict.iteritems():
		valaux = h.GetBinContent(b)
		h.SetBinContent(b,valaux/nentries)
	
	return h


def drawstacked(indet,cadet,msdet,xvar):
	"""
	"""
	import ROOT
	hindet = graphtohist(indet,100)
	cadet  = graphtohist(cadet,100)
	msdet  = graphtohist(msdet,100)

	hstack = ROOT.THStack('hs','hstack')
	hstack.Add(cadet)
	hstack.Add(msdet)
	c =ROOT.TCanvas()
	hstack.Draw("HIST")
	c.SaveAs('test_'+xvar+'.png')

def reordergraph(f):
	"""
	"""
	nentries = f.GetN()
	xbuffer = f.GetX()
	x = [xbuffer[i] for i in xrange(nentries)]
	ybuffer = f.GetY()
	y = [ybuffer[i] for i in xrange(nentries)]
	xy = zip(x,y)
	f.Set(0)
	k1 = 0 
	for phi,x0 in sorted(xy):
		f.SetPoint(k1,phi,x0)
		k1+=1

def filldict(geoid,phi,theta,x0,fdict):
	from math import pi,log,tan
	eta = -log(tan(theta/2.0))
	fdict[(eta,geoid)] = (x0,phi,theta)
	
def main(ffullname,ffastname):
	"""
	"""
	import ROOT
	from array import array
	
	ffull  = ROOT.TFile.Open(ffullname)
	ffast  = ROOT.TFile.Open(ffastname)
	# Files and trees associated to full and fast
	cfiles = { 'fullsim': ffull, 'fastsim': ffast }	
	ctrees = dict(map(lambda (t,x): (t,x.Get("particles")),cfiles.iteritems()))
	#
	hd = dict(map(lambda t: (t,{}),ctrees.keys()))
	
	# Getting quantities of interest and setting the branch
	x0_a   = array('f',[0.0])
	phi_a  = array('f',[0.0])
	theta_a= array('f',[0.0])
	geoID_a= array('i',[0])
	# looping for the fast and full simulation
	for simtype,t in ctrees.iteritems():
	    # Number of entries in each bin
	    t.SetBranchAddress("X0",x0_a)
	    t.SetBranchAddress("pph",phi_a)
	    t.SetBranchAddress("pth",theta_a)
	    t.SetBranchAddress('geoID',geoID_a)
	    _entries = t.GetEntries()
	    for i in xrange(_entries):
			_dummy = t.GetEntry(i)
			_x0 = x0_a[0]
			_phi= phi_a[0]
			_theta=theta_a[0]
			filldict(geoID_a[0],phi_a[0],theta_a[0],_x0,hd[simtype])
			
	# Converting acquired info to TGraph in order to draw for each
	# topological (angular) variable 
	for xvariable in ['eta','phi','theta']:
		# Inner Detector
		tid = dict(map(lambda x: (x,ROOT.TGraph()), cfiles.keys()))
		for n,f in tid.iteritems():
			f.SetName('id_'+xvariable+'_'+n)
			f.SetMarkerStyle(20)
			f.SetLineWidth(1)
		# Calorimeters
		cad = dict(map(lambda x: (x,ROOT.TGraph()), cfiles.keys()))
		for n,f in cad.iteritems():
			f.SetName('ca_'+xvariable+'_'+n)
			f.SetMarkerStyle(20)
			f.SetLineWidth(1)
		# Muon Spectrometer
		msd = dict(map(lambda x: (x,ROOT.TGraph()), cfiles.keys()))
		for n,f in msd.iteritems():
			f.SetName('ms_'+xvariable+'_'+n)
			f.SetMarkerStyle(20)
			f.SetLineWidth(1)
		
		# Fill the TGraph's
		for simtype,etax0dict in hd.iteritems():
			k = {1:0, 3:0, 4:0}
			for (eta,geoID),(x0,phi,theta) in sorted(etax0dict.iteritems()):
				if geoID == 1:
					activef = tid[simtype]
				elif geoID == 3:
					activef = cad[simtype]
				elif geoID == 4:
					activef = msd[simtype]
				else:
					continue
				# actually fill (with the current angular variable)
				xvar = eval(xvariable)
				activef.SetPoint(k[geoID],xvar,x0)
				k[geoID] += 1
		# Re-ordering in the phi case
		if xvariable == "phi":
			for simtype,f in tid.iteritems():
				reordergraph(f)
			for simtype,f in cad.iteritems():
				reordergraph(f)
			for simtype,f in msd.iteritems():
				reordergraph(f)
		#print "Evaluated points for the each subdetector:"
		# Drawing for each subdetector
		for detname,grdict in [('innerdetector',tid), ('calorimeter',cad),('muonspectrometer',msd)]:
			drawgraph(grdict,detname,xvariable)
		# Draw a stacked graph with all the detectors: 
		# FIXME: TESTING... To be decided if it's included or not
		drawstacked(tid['fullsim'],cad['fullsim'],msd['fullsim'],xvariable)

	ffull.Close()
	ffast.Close()

if __name__ == '__main__':
	import os
	from optparse import OptionParser,OptionGroup
	
	cwd = os.getcwd()
	parser = OptionParser()
	parser.set_defaults(fullsim=os.path.join(cwd,'ISFG4SimKernel.root'),\
			fastsim=os.path.join(cwd,'ISFFatras.root'))

	parser.add_option( '--full', action='store', type='string', dest='fullsim',\
			help="Full (Geant4) simulation root file [ISFG4SimKernel.root]")
	parser.add_option( '--fast', action='store', type='string', dest='fastsim',\
			help="Fast simulation root file [ISFFatras.root]")

	(opt, args)=parser.parse_args()	
	# See main function
	main(opt.fullsim,opt.fastsim)
