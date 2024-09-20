import numpy as np

import plotly.graph_objects as go

import matplotlib.pyplot as plt
import mplhep as hep

from h5flow.data import dereference
import h5flow

from h5flow.data import dereference
import h5flow

import numpy as np

import os

if not os.path.exists("images"):
    os.mkdir("images")

def get_position(x, y, z):
    return np.column_stack([x, y, z])

def compute_pca(hits):
    pca = PCA(1)
    pca.fit(hits)
    pca.components_[0]
    print('pca', pca.components_[0])

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
    

#f_name = '/global/cfs/cdirs/dune/users/demaross/MiniRun4_files_with_rock/MiniRun4_1E19_RHC.flow.00341.FLOW.proto_nd_flow.h5'
f_name = 'packet-0050017-2024_07_10_09_08_04_CDT.FLOW.hdf5'
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


vec0, vec1 = compute_direction(tracks["theta_xz"], tracks["theta_yz"], start_point, end_point)

for itrk, t2h in enumerate(track2hits.data):
    if itrk > 3:
        break

    rock_muon_hits = np.array([tup for tup in t2h if not all(elem == 0 for elem in tup)], dtype = t2h.dtype)

    fig = go.Figure()
    PHits_traces = go.Scatter3d(
        #x= rock_muon_hits['x'].flatten(), y= rock_muon_hits['y'].flatten(), z= rock_muon_hits['z'].flatten(),
        x= rock_muon_hits['x'], y= rock_muon_hits['y'], z= rock_muon_hits['z'],

        marker_color= rock_muon_hits['Q'],
        mode='markers',
        marker_size=1,
        marker_symbol='square',
        # visible='legendonly',
        showlegend=True,
        opacity=0.7,
        name='prompt hits'
    )
    fig.add_traces(PHits_traces)
    
    # add a line
    print([tracks['x_start'][itrk], tracks['x_end'][itrk]])
    print([tracks['y_start'][itrk], tracks['y_end'][itrk]])
    print([tracks['z_start'][itrk], tracks['z_end'][itrk]])
    track = go.Scatter3d(x = [tracks['x_start'][itrk], tracks['x_end'][itrk]],
                       y = [tracks['y_start'][itrk], tracks['y_end'][itrk]],
                       z = [tracks['z_start'][itrk], tracks['z_end'][itrk]],
                        mode='lines', name='start to end')
    fig.add_traces(track)

    # fig.show()

    fig.write_image("images/{}_track{}.png".format(packet_prefix, itrk))