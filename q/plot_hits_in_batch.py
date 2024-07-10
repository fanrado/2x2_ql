import numpy as np
import h5py

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import sys
import os

from geohelper import geohelper

def prepare_data(file2306, itpc=1):
    if itpc not in [1, 2]:
        raise ValueError("io group (itpc) must be 1 or 2")
    ### all Bern module data has been uploaded to NERSC - a NERSC account is not needed to access
    ### see this link for click-downloadable files: https://portal.nersc.gov/project/dune/data/Module1/TPC12/dataRuns/packetData/
    # file2306='packet_2022_02_10_22_58_34_CET.h5'
    ftimestamp=file2306.split("/")[-1].split('2022_02_10_')[-1].split("_CET")[0]
    print("Start {}".format(ftimestamp))
    f=h5py.File(file2306,'r')
    io_group_mask=f['packets']['io_group']==1 # selects packets from a specific TPC
    packets=f['packets'][io_group_mask]
    sync_mask=((packets['packet_type']==6)&(packets['trigger_type']==83)) # selects SYNC packets that are externally generated
    print(sync_mask.shape)
    sync_idcs=np.argwhere(sync_mask).flatten()
    message_groups = np.split(packets, sync_idcs) # partition the packet dataset by sync packet index
    print(len(message_groups),' packet groups partitioned by sync packets')
    return message_groups

def plot_all_events(message_groups, threshold=500, folder='temp', itpc=1):
    if itpc not in [1, 2]:
        raise ValueError("io group (itpc) must be 1 or 2")
    plt.close('all')
    plt.ioff()
    helper = geohelper()
    fig3d = plt.figure('event display & ADC sum', figsize=(8, 8))
    ax3d = fig3d.add_subplot(111, projection='3d')
    for sync_group in range(len(message_groups)):
        mg = message_groups[sync_group]
        data_mask=((mg['packet_type']==0)&(mg['valid_parity']==1)&(mg['timestamp']<1e7)) # filter on data packets with valid parity with sync-consistent timestamp
        data_packets=mg[data_mask]
        # print(len(data_packets),' data packets between syncs')

        # histogram the timestamp packet field
        # roughly 200 microseconds binning assuming ticks up to value 1e7 in datastream between syncs
        counts, xbins = np.histogram(data_packets['timestamp'], bins=500)
        bin_width=xbins[1]-xbins[0]

        physics_bins=[] # save to list bin index for bins exceeding threshold
        for i in range(len(counts)):
            if counts[i]>threshold: physics_bins.append(i)

        # print(len(physics_bins),' candidate events')
        for counter in range(len(physics_bins)):
            t0 = physics_bins[counter]*bin_width
            t1 = physics_bins[counter]*bin_width+bin_width

            if len(physics_bins)==1: return # due to correlated-sync noise, we will always have significant pickup near 0 timestamp

            event_mask = (data_packets['timestamp']>=physics_bins[counter]*bin_width)&(data_packets['timestamp']<physics_bins[counter]*bin_width+bin_width) # filter packets on histgrammed bin of interest
            hits = data_packets[event_mask]
            io_channel = hits['io_channel']
            tile_id = np.array([helper.io_channel_to_tile(ioc) for ioc in io_channel])
            chip_id = hits['chip_id']
            channel_id = hits['channel_id']
            timestamp = hits['timestamp']
            dataword = hits['dataword'] # ADC value

            try:
            # correlate hardware ID to geometry information to find (x,y) position of hits
                xys = np.fromiter((helper.find_xy(tile, chip, channel) for tile, chip, channel in zip(tile_id, chip_id, channel_id)),
                              dtype=np.dtype((np.float64, 2)))
                x = xys[:,0]
                y = xys[:,1]
            except:
                print("Bad geometry mapping, sync_group {} counter {}".format(sync_group, counter))
                continue
            # print(len(dataword),' hits in event')

            ############
            ax3d.clear()
            ax3d.set_title('io_group {} sync_group {} counter {} threshold {}'.format(itpc, sync_group, counter, threshold))
            ax3d.scatter(timestamp, x, y, s=1)
            ax3d.set_xlabel("Timestamp [0.1 us]")
            ax3d.set_ylabel("x []", labelpad=10)
            ax3d.set_zlabel("y []")
            fig3d.savefig('{}/iogroup{}_syncgroup{:d}_counter{:d}_threshold{threshold}.png'.format(folder, itpc, sync_group, counter, threshold=threshold))

if __name__ == '__main__':
    ### all Bern module data has been uploaded to NERSC - a NERSC account is not needed to access
    ### see this link for click-downloadable files: https://portal.nersc.gov/project/dune/data/Module1/TPC12/dataRuns/packetData/
    itpc = 1
    if len(sys.argv) == 1:
        file2306 = 'packet_2022_02_10_22_58_34_CET.h5'
    else:
        file2306 = sys.argv[1]
        if len(sys.argv) == 3:
            itpc = np.uint8(sys.argv[2])
    mg = prepare_data(file2306, itpc)
    folder = file2306.split('/')[-1].split('.')[0]
    if os.path.exists(folder):
        print("Folder {} exists".format(folder))
    else:
        os.mkdir(folder)
        print("Made directory {}".format(folder))
    print("Output are saved under {}".format(folder))
    plot_all_events(mg, 500, folder, itpc)
