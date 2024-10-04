from plot_profile import plot_all
import ROOT
import sys

def main():
    try:
        fname = sys.argv[1]
    except IndexError:
        fname = 'summary.root'

    fname_prefix = fname.split('/')[-1].split('.root')[0]
    f = ROOT.TFile(fname)
    hyz_perp_vs_yz = f.Get('hyz_perp_vs_yz')
    hyz = f.Get('hyz')
    hyz_perp = f.Get('hyz_perp')
    hdx = f.Get('hdx')

    hyz_perp_vs_yz_pass = f.Get('hyz_perp_vs_yz_pass')
    hyz_pass = f.Get('hyz_pass')
    hyz_perp_pass = f.Get('hyz_perp_pass')
    hdx_pass = f.Get('hdx_pass')

    plot_all(h2d=hyz_perp_vs_yz_pass, hyz=hyz_pass, hyz_perp=hyz_perp_pass, hdx=hdx_pass, odir=fname_prefix, label='pass')
    plot_all(h2d=hyz_perp_vs_yz, hyz=hyz, hyz_perp=hyz_perp, hdx=hdx, odir=fname_prefix, label='all')

if __name__ == '__main__':
    main()
