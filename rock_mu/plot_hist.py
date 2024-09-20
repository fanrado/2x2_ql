import ROOT
from ROOT import TCanvas

ROOT.gStyle.SetOptStat(0)

f = ROOT.TFile('hists.root')
hdx = f.Get('hdx')
hyz = f.Get('hyz')
hyz_perp = f.Get('hyz_perp')

hdx_trk0 = f.Get('hdx_trk0')
hyz_trk0 = f.Get('hyz_trk0')
hyz_perp_trk0 = f.Get('hyz_perp_trk0')

def plot(c, h, **kwargs):
    c.cd()
    h.Draw("E")
    xtitle = kwargs["xtitle"]
    h.GetXaxis().SetTitle(xtitle)
    
    skewness = h.GetSkewness()
    mean = h.GetMean()
    stddev = h.GetStdDev()
    
    tex = ROOT.TLatex()
    tex.SetTextFont(42)
    tex.DrawLatexNDC(0.65, 0.85, "Mean {:0.3f}".format(mean))
    tex.DrawLatexNDC(0.65, 0.79, "StdDev {:0.3f}".format(stddev))
    if kwargs.get("skewness", None):
        tex.DrawLatexNDC(0.65, 0.73, "Skewness {:0.3f}".format(skewness))
        
    if kwargs.get('label', None):
        tex.DrawLatexNDC(0.2, 0.73, kwargs.get('label'))
    
    c.Print(kwargs['png'])

cdx = TCanvas('cdx', 'cdx', 800, 600)
cyz_perp = TCanvas('cyz_perp', 'cyz_perp', 800, 600)
cyz = TCanvas('cyz', 'cyz', 800, 600)

c = TCanvas("c", 'c', 800, 600)

plot(cdx, hdx, xtitle='dx w.r.t. predicted track x [cm]', png='cdx.png', skewness=True)

plot(cyz, hyz, xtitle='scaled projection along track direction on yz plane', png='cyz.png')

plot(cyz_perp, hyz_perp, xtitle='perpendicular deviation to track direction on yz plane [cm]', png='cyz_perp.png', skewness=True)

plot(c, hdx_trk0, xtitle='dx w.r.t. predicted track x [cm]', png='cdx_trk0.png', skewness=True, label='trk0')
plot(c, hyz_trk0, xtitle='scaled projection along track direction on yz plane', png='cyz_trk0.png', label='trk0')
plot(c, hyz_perp_trk0, xtitle='perpendicular deviation to track direction on yz plane [cm]', png='cyz_perp_trk0.png', skewness=True, label='trk0')

