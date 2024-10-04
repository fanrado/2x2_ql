import ROOT
import sys
import os

NMAX = 5000
try:
    fname = sys.argv[1]
except IndexError:
    fname = 'packet-0050017-2024_07_08_15_43_39_CDT_hists.root'

fname_prefix = fname.split('/')[-1].split('.root')[0]
f = ROOT.TFile(fname)
hyz_perp_vs_yz = f.Get('hyz_perp_vs_yz')
hyz = f.Get('hyz')
hyz_perp = f.Get('hyz_perp')
hdx = f.Get('hdx')

def plot_hist(c, h, **kwargs):
    c.cd()
    h.Draw("E")
    xtitle = kwargs["xtitle"]
    h.GetXaxis().SetTitle(xtitle)

    skewness = h.GetSkewness()
    kurtosis = h.GetKurtosis()
    mean = h.GetMean()
    stddev = h.GetStdDev()

    tex = ROOT.TLatex()
    tex.SetTextFont(42)
    tex.DrawLatexNDC(0.65, 0.85, "Mean {:0.3f}".format(mean))
    tex.DrawLatexNDC(0.65, 0.79, "StdDev {:0.3f}".format(stddev))
    if kwargs.get("skewness", None):
        tex.DrawLatexNDC(0.65, 0.73, "Skewness {:0.3f}".format(skewness))
        tex.DrawLatexNDC(0.65, 0.67, "Kurtosis {:0.3f}".format(kurtosis))
    if kwargs.get('label', None):
        tex.DrawLatexNDC(0.2, 0.73, kwargs.get('label'))

def plot_prof(h, plot=False, odir='.'):
    if h.Integral() < 5:
        return 1E9
    ROOT.gStyle.SetOptStat(0)
    ROOT.gStyle.SetOptFit(111)
    hprofs = h.ProfileX("{}_profilex_s".format(h.GetName()), 1, -1, "s");
    hprof = h.ProfileX("{}_profilex".format(h.GetName()), 1, -1, "");
    c = ROOT.TCanvas("c", "c", 800*2, 600*2)
    c.Divide(2, 2)
    c.cd(1)
    h.Draw("COLZ")
    c.cd(2)
    # f = ROOT.TF1("f", "[0]", 0, 0.5)
    f = ROOT.TF1("f", "[0]", -0.5, 0.5)
    # result = hprof.Fit(f, "QS")
    result = hprof.Fit(f, "QSR", "", -0.5, 0.5)
    hprof.Draw()
    c.cd(3)
    hprofs.Draw()
    try:
        chi2_norm = result.Chi2() / result.Ndf()
    except:
        chi2_norm = 1E9
    return chi2_norm

def plot_all(h2d, hyz, hyz_perp, hdx, odir, label):
    ROOT.gStyle.SetOptStat(0)
    ROOT.gStyle.SetOptFit(111)
    hprofs = h2d.ProfileX("{}_profilex_s".format(h2d.GetName()), 1, -1, "s");
    hprof = h2d.ProfileX("{}_profilex".format(h2d.GetName()), 1, -1, "");
    c = ROOT.TCanvas("c", "c", 800*2, 600*3)
    c.Divide(2, 3)
    c.cd(1)
    h2d.Draw("COLZ")
    c.cd(2)
    # f = ROOT.TF1("f", "[0]", 0, 1)
    f = ROOT.TF1("f", "[0]", -0.5, 0.5)
    # hprof.Fit(f, "Q")
    hprof.Fit(f, "QR", "", -0.5, 0.5)
    hprof.Draw()
    c.cd(3)
    hprofs.Draw()

    pad = c.cd(4)
    plot_hist(pad, hyz, xtitle='scaled projection along track direction on yz plane', label=label)
    pad = c.cd(5)
    plot_hist(pad, hyz_perp, xtitle='perpendicular deviation to track direction on yz plane [cm]', skewness=True, label=label)
    pad = c.cd(6)
    plot_hist(pad, hdx, xtitle='dx w.r.t. predicted track x [cm]', skewness=True, label=label)

    c.Print('{}/{}_{}.png'.format(odir, fname_prefix, h2d.GetName()))

hyz_perp_vs_yz_pass = ROOT.TH2D("hyz_perp_vs_yz_pass", "",
                                hyz_perp_vs_yz.GetNbinsX(), hyz_perp_vs_yz.GetXaxis().GetBinLowEdge(1), hyz_perp_vs_yz.GetXaxis().GetBinLowEdge(hyz_perp_vs_yz.GetNbinsX()+1),
                                hyz_perp_vs_yz.GetNbinsY(), hyz_perp_vs_yz.GetYaxis().GetBinLowEdge(1), hyz_perp_vs_yz.GetYaxis().GetBinLowEdge(hyz_perp_vs_yz.GetNbinsX()+1)
                                )
hyz_perp_pass = hyz_perp.Clone("hyz_perp_pass")
hyz_pass = hyz.Clone("hyz_pass")
hdx_pass = hdx.Clone("hdx_pass")
hyz_perp_pass.Reset("ICESM")
hyz_pass.Reset("ICESM")
hdx_pass.Reset("ICESM")

def create_dir(d):
    if not os.path.exists(d):
        os.makedirs(d)

def main():
    hskew_dx = ROOT.TH1F("hskew_dx", "dx;skewness;", 80, -4, 4)
    hskewall_dx = ROOT.TH1F("hskewall_dx", "dx;skewness;", 80, -4, 4)
    hskew_yz_perp = ROOT.TH1F("hskew_yz_perp", "yz_perp;skewness;", 80, -4, 4)
    hskewall_yz_perp = ROOT.TH1F("hskewall_yz_perp", "yz_perp;skewness;", 80, -4, 4)
    passed = 0
    total = 0
    eff = ROOT.TH1F("numbers", "", 2, 0, 2)
    for i in range(NMAX):
        hyz_perp_vs_yz_itrk = f.Get('hyz_perp_vs_yz_trk{}'.format(i))
        hyz_perp_itrk = f.Get('hyz_perp_trk{}'.format(i))
        hyz_itrk = f.Get('hyz_trk{}'.format(i))
        hdx_itrk = f.Get('hdx_trk{}'.format(i))
        if isinstance(hyz_perp_vs_yz_itrk, ROOT.TH2):
            total = total+1
            try:
                chi2_norm = plot_prof(hyz_perp_vs_yz_itrk)
            except ZeroDivisionError:
                chi2_norm = 1E9
            odir = '.'
            if chi2_norm < 5:
                passed = passed+1
                hyz_perp_vs_yz_pass.Add(hyz_perp_vs_yz_itrk)
                hyz_perp_pass.Add(hyz_perp_itrk)
                hyz_pass.Add(hyz_itrk)
                hdx_pass.Add(hdx_itrk)
                odir = '{}/passed'.format(fname_prefix)
                hskew_dx.Fill(hdx_itrk.GetSkewness())
                hskew_yz_perp.Fill(hyz_perp_itrk.GetSkewness())
            else:
                odir = '{}/failed'.format(fname_prefix)
            create_dir(odir)
            plot_all(h2d=hyz_perp_vs_yz_itrk, hyz=hyz_itrk, hyz_perp=hyz_perp_itrk, hdx=hdx_itrk, odir=odir, label='trk{}'.format(i))
            hskewall_dx.Fill(hdx_itrk.GetSkewness())
            hskewall_yz_perp.Fill(hyz_perp_itrk.GetSkewness())

        else:
            continue
        if total == NMAX:
            print("Saturated")
    print("Passed", passed)
    print("Total", total)
    print("Efficiency", passed/total)
    plot_all(h2d=hyz_perp_vs_yz_pass, hyz=hyz_pass, hyz_perp=hyz_perp_pass, hdx=hdx_pass, odir=fname_prefix, label='pass')
    plot_all(h2d=hyz_perp_vs_yz, hyz=hyz, hyz_perp=hyz_perp, hdx=hdx, odir=fname_prefix, label='all')

    eff.SetBinContent(1, total)
    eff.SetBinContent(2, passed)
    eff.GetXaxis().SetBinLabel(1, "total")
    eff.GetXaxis().SetBinLabel(2, "passed")

    c = ROOT.TCanvas("c", "", 800, 600)
    for h in [hskew_dx, hskewall_dx, hskew_yz_perp, hskewall_yz_perp]:
        c.Clear()
        plot_hist(c, h, xtitle='skewness')
        c.Print('{}/{}.png'.format(fname_prefix, h.GetName()))

    fout = ROOT.TFile('{}_summary.root'.format(fname_prefix), 'recreate')
    hskew_dx.Write()
    hskew_yz_perp.Write()
    hskewall_dx.Write()
    hskewall_yz_perp.Write()
    hyz_perp_vs_yz_pass.Write()
    hyz_perp_vs_yz.Write()
    hyz_perp_pass.Write()
    hyz_perp.Write()
    hyz_pass.Write()
    hyz.Write()
    hdx_pass.Write()
    hdx.Write()
    eff.Write("numbers")

if __name__ == '__main__':
    main()
