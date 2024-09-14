import numpy as np
from scipy.interpolate import pchip_interpolate

def load_fr_ctr(fr_file):
    fr = np.load(fr_file)
    fr_ctr = fr[0:5,0:5]
    print('shape of center region', fr_ctr.shape)
    #print('First element after merging', np.sum(fr_ctr[:, :, 0]))
    #print('First element after merging', np.sum(fr_ctr, axis=(0,1))[0])
    fr_ctr_pxl = 4 *  np.sum(fr_ctr, axis=(0,1)) # four quadrants
    fr_ctr_pxl = fr_ctr_pxl / np.sum(fr_ctr_pxl) # normalized per tick

    print('integration of first 700 ticks', np.sum(fr_ctr_pxl[0:700]))
    print('drop first 700 ticks and renormalize')
    fr_ctr_pxl = fr_ctr_pxl[700:]

    fr_ctr_pxl = fr_ctr_pxl / np.sum(fr_ctr_pxl)

    return fr_ctr_pxl

def q_gaus(q, r, sigma):
    x = np.linspace(-r/2., r/2., r)
    x_norm = x/sigma
    y = np.exp(-x_norm**2/2) / np.sqrt(2*np.pi*sigma**2)
    y = y * (x[1]-x[0])
    
    if isinstance(q, np.ndarray):
        qv = np.array([v * y for v in q])
    else:
        qv = q*y
    return qv

def fr_record(q, pos, unit_fr, npoints=10_000):
    '''
    q: np.ndarray, (N, ), a sequence of charges at z (or t_i = z_i for i in range(N))
    pos: integer, the closet z to anode; closet t to anode
    unit_fr: np.ndarray, (M, ), a sequence of field response for charge at z (or t)

    field response is seen when npoints - position < M
    '''

    fr = np.zeros(npoints)

    r = len(unit_fr)
    n = len(q)
    for j in range(npoints):
        if r > n:
            if pos > npoints - r and pos - n < npoints - r:
                k = pos + r - npoints
                fr[j] = np.sum(q[-k:] * unit_fr[0:k])
            elif pos - n >= npoints - r and pos < npoints:
                l = r - npoints + pos - n
                fr[j] = np.sum(q * unit_fr[l:l+n])
            elif pos >= npoints and pos - n < npoints:
                k = npoints - pos + n
                fr[j] = np.sum(q[:k] * unit_fr[-k:])
        else:
            if pos > npoints - r and pos - n < npoints - r:
                k = pos + r - npoints
                fr[j] = np.sum(q[-k:] * unit_fr[0:k])
            elif pos >= npoints and pos - n < npoints - r:
                l = n - pos + npoints - r
                fr[j] = np.sum(q[l:l+r] * unit_fr)
            elif pos - n >= npoints - r and pos - n < npoints:
                k = npoints - pos + n
                fr[j] = np.sum(q[:k] * unit_fr[-k:])
        pos += 1

    return fr

def readout(fr, thres, delay):
    t = []
    out = []
    
    triggered = False
    i = 0
    for j, _ in enumerate(fr):
        if  not triggered and np.sum(fr[i:j+1]) > thres:
            t.append(j)
            out.append(np.sum(fr[i:j+delay]))
            triggered = True
            i = j+delay+1
            # print(triggered, j, j+delay, np.sum(fr[i:j+1]), np.sum(fr[j:j+delay]))
        if triggered and j>=i:
            triggered = False

    return np.array([t, out])

def smooth_wf(wf, thres, roi, delay, npoints=10_000, extrapolate=False):
    wf_new = np.zeros(npoints)
    dts = np.append(wf[0][0], np.diff(wf[0]))
    seri = []
    for i in range(len(wf[0])):
        if i == 0:
            if wf[0][0] > roi:
                t0 = wf[0][0]-roi
            else:
                t0 = 0
            t1 = wf[0][0]
        else:
            dt = wf[0][i] - wf[0][i-1]
            print(dt)
            t0 = wf[0][i] - dt + delay
            t1 = wf[0][i]
        t0 = np.int_(t0+0.002)
        t1 = np.int_(t1+0.002)
        t2 = np.int_(t1+delay+0.002)
        seri.append([t0, t1, thres])
        seri.append([t1, t2, wf[1][i]-thres])
    seri_array = np.array(seri)
    print(wf[0])
    print(seri)

    acc_wf = np.add.accumulate(seri_array[:,2])
    acc_wf = np.append([0], acc_wf)
    acc_wf = np.append(acc_wf, [acc_wf[-1]])
    ticks = seri_array[:,0]
    ticks = np.append(ticks, seri_array[-1,1])
    ticks = np.append(ticks, seri_array[-1,1]+roi)
    
    for i in range(len(seri)):
        #
        t0, t1, v1 = seri[i]
        b1 = v1/(t1-t0)
        if not extrapolate:
            wf_new[t0:t1] = b1
    if extrapolate:
        # raise NotImplementedError("try not extrapolate")
        xs = np.arange(ticks[0], ticks[-1]+1, 1) if ticks[-1] < npoints else np.arange(ticks[0], npoints+1, 1)
        acc_wf_ext = pchip_interpolate(ticks, acc_wf, xs)
        wf_new[np.int_(ticks[0]) : np.int_(ticks[-1])] = np.diff(acc_wf_ext)
    return wf_new