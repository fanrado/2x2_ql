import numpy as np

import sys

import plotly.graph_objects as go

import matplotlib.pyplot as plt
import mplhep as hep

from h5flow.data import dereference
import h5flow

from h5flow.data import dereference
import h5flow

import numpy as np

import boost_histogram as bh

import uproot

import pickle

import os

if not os.path.exists("images"):
    os.mkdir("images")

def get_position(x, y, z):
    return np.column_stack([x, y, z])

def get_length(x0, x1):
    return np.linalg.norm(x1-x0, axis=1)

def compute_direction(theta_xz, theta_yz, start_point, end_point):
    '''
    theta_xz and theta_yz are in degrees
    return (theta_yz, theta_xz, theta_xy(inferred)), (dx, dy, dz)
    '''
    vec0 = np.cos(np.deg2rad(np.column_stack([theta_yz, theta_xz]))) # [1, 0, 0], [0, 1, 0]
    print(vec0.shape)
    # vec0 =1 - np.sum(vec0**2, axis=1)
    vec0 = np.column_stack([vec0, np.sqrt(1 - np.sum(vec0**2, axis=1))])


    vec1 = end_point - start_point
    vec1norm = np.linalg.norm(vec1, axis=1)
    vec1 = vec1/vec1norm[:,np.newaxis]

    xsign0 = np.sign(vec0[:,0])
    xsign1 = np.sign(vec1[:,0])
    ysign0 = np.sign(vec0[:,1])
    ysign1 = np.sign(vec1[:,1])

    zsign0 = np.sign(vec0[:,2])
    zsign1 = np.sign(vec1[:,2])

    vec0[:,2] = vec0[:,2] * zsign0 * zsign1 * xsign0 * xsign1

    vec0 = (xsign0 * xsign1)[:, np.newaxis] * vec0

    return vec0, vec1

def compute_xy_proj(unit_vec, pref, hits, iogroup):
    '''
    pref (x, y, z)
    unit_vec (vx, vy, vz)
    hits: np.ndarray (N, 3)
    x: drift
    y: vertical
    z: beam
    '''
    proj_vec = np.array([0, 1, 1])

    unit_vec_yz = unit_vec * proj_vec
    cos_yz = np.linalg.norm(unit_vec_yz)
    unit_vec_yz = unit_vec_yz/cos_yz
    unit_vecs_yz = np.array([i for i in unit_vec_yz] * hits.shape[0])

    pref_yz = pref * proj_vec
    hits_yz = hits * proj_vec
    displace_yz = hits_yz - pref_yz
    # cross_yz = np.linalg.cross(displace_yz, unit_vec_yz)

    cross_yz = np.cross(displace_yz, unit_vec_yz)
    dot_yz = np.dot(displace_yz, unit_vec_yz)

    unit_vec_x = np.array([1, 0, 0])
    cross_yz_val = np.dot(cross_yz, unit_vec_x)

    '''
    print('unit_vec', unit_vec)
    print('pref', pref)
    print('hits0', hits[0])
    print('hits1', hits[1])
    print('unit_vec_yz', unit_vec_yz)
    print('displace_yz0', displace_yz[0])
    print('displace_yz1', displace_yz[1])

    print('cross_yz.shape', cross_yz.shape)
    print('dot_yz.shape', dot_yz.shape)
    print('cross_yz[0]', cross_yz[0])
    print('cross_yz_norm[0]', cross_yz_norm[0])
    print('dot_yz[0]', dot_yz[0])
    print('cross_yz[1]', cross_yz[1])
    print('cross_yz_norm[1]', cross_yz_norm[1])
    print('dot_yz[1]', dot_yz[1])
    '''
    proj_x = dot_yz / cos_yz * unit_vec[0]
    dx = hits[:,0] - proj_x - pref[0]

    sign = np.where(iogroup % 2, np.ones(hits.shape[0]), -1*np.ones(hits.shape[0]))
    dx = dx * sign
    '''
    print('cos_yz', cos_yz)
    '''
    return cross_yz_val, dot_yz, dx

#f_name = '/global/cfs/cdirs/dune/users/demaross/MiniRun4_files_with_rock/MiniRun4_1E19_RHC.flow.00341.FLOW.proto_nd_flow.h5'
f_name = sys.argv[1]
packet_prefix = f_name.split('/')[-1].split('.')[0]
f = h5flow.data.H5FlowDataManager(f_name, 'r')

track2hits = dereference(
    f['/analysis/rock_muon_tracks/data']['rock_muon_id'],     # indices of A to load references for, shape: (n,)
    f['/analysis/rock_muon_tracks/ref/charge/calib_prompt_hits/ref'],  # references to use, shape: (L,)
    f['/charge/calib_prompt_hits/data'],
    ref_direction = (0,1)# dataset to load, shape: (M,)
    )

tracks = f['/analysis/rock_muon_tracks/data']

start_point = get_position(tracks['x_start'], tracks['y_start'], tracks['z_start'])
end_point = get_position(tracks['x_end'], tracks['y_end'], tracks['z_end'])

dist = get_length(start_point, end_point)

vec0, vec1 = compute_direction(tracks["theta_xz"], tracks["theta_yz"], start_point, end_point)

hyz_perp = bh.Histogram(bh.axis.Regular(50, -2.5, 2.5))
hdx = bh.Histogram(bh.axis.Regular(80, -4, 4))
# hyz = bh.Histogram(bh.axis.Regular(50, 0, 1))
hyz = bh.Histogram(bh.axis.Regular(50, -1, 1))

# hyz_perp_vs_yz = bh.Histogram(bh.axis.Regular(50, 0, 1), bh.axis.Regular(50, -2.5, 2.5))
hyz_perp_vs_yz = bh.Histogram(bh.axis.Regular(50, -1, 1), bh.axis.Regular(50, -2.5, 2.5))

hyz_perp_trk = {}
hdx_trk = {}
hyz_trk = {}
hyz_perp_vs_yz_trk = {}

for itrk, t2h in enumerate(track2hits.data):
    # if itrk > 3:
    #     break



    rock_muon_hits = np.array([tup for tup in t2h if not all(elem == 0 for elem in tup)], dtype = t2h.dtype)

    points = get_position(rock_muon_hits['x'], rock_muon_hits['y'], rock_muon_hits['z'])
    center_of_mass = np.mean(points, axis=0)
    iogroup = rock_muon_hits['io_group']

    # cross_yz, dot_yz, dx = compute_xy_proj(vec0[itrk], start_point[itrk], points, iogroup)
    cross_yz, dot_yz, dx = compute_xy_proj(vec0[itrk], center_of_mass, points, iogroup)

    dot_yz_norm = dot_yz / dist[itrk]

    if vec0[itrk][0] < 0.1:
    # if tracks['theta_yz'][itrk] < 5:
    # if tracks['theta_yz'][itrk] < 5:
        hyz_perp_trk[itrk] = bh.Histogram(bh.axis.Regular(50, -2.5, 2.5))
        hdx_trk[itrk] = bh.Histogram(bh.axis.Regular(80, -4, 4))
        # hyz_trk.append(bh.Histogram(bh.axis.Regular(50, 0, 1)))
        hyz_trk[itrk] = bh.Histogram(bh.axis.Regular(50, -1, 1))
        # hyz_perp_vs_yz_trk.append(bh.Histogram(bh.axis.Regular(50, 0, 1), bh.axis.Regular(50, -2.5, 2.5)))
        hyz_perp_vs_yz_trk[itrk] = bh.Histogram(bh.axis.Regular(50, -1, 1), bh.axis.Regular(50, -2.5, 2.5))

        hyz_perp.fill(cross_yz)
        hyz.fill(dot_yz_norm)
        hdx.fill(dx)

        hyz_perp_vs_yz.fill(dot_yz_norm, cross_yz)

        hyz_perp_trk[itrk].fill(cross_yz)
        hyz_trk[itrk].fill(dot_yz_norm)
        hdx_trk[itrk].fill(dx)

        hyz_perp_vs_yz_trk[itrk].fill(dot_yz_norm, cross_yz)

# with open("hists.pkl", "wb") as f:
#     pickle.dump(hyz_perp, f)

with uproot.recreate('{}_hists.root'.format(packet_prefix)) as froot:
    froot['hyz_perp'] = hyz_perp
    froot['hyz'] = hyz
    froot['hdx'] = hdx
    froot['hyz_perp_vs_yz'] = hyz_perp_vs_yz

    for i, h in hyz_perp_trk.items():
        # print('1', i)
        froot['hyz_perp_trk{}'.format(i)] = h
    for i, h in hyz_trk.items():
        # print('2', i)
        froot['hyz_trk{}'.format(i)] = h
    for i, h in hdx_trk.items():
        # print('3', i)
        froot['hdx_trk{}'.format(i)] = h
    for i, h in hyz_perp_vs_yz_trk.items():
        # print('3', i)
        froot['hyz_perp_vs_yz_trk{}'.format(i)] = h

    print("Found", len(hyz_perp_vs_yz_trk))
