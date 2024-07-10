import os
import sys
import pandas as pd
import shutil

if __name__ == '__main__':
   fname = sys.argv[1]
   info = pd.read_excel(fname)
   # print(info.head())
   for idx, i in info.iterrows():
       src = '{}/iogroup{:d}_syncgroup{:d}_counter{:d}_threshold{}.png'.format(
           os.path.dirname(fname), i['io_group'], i['sync_group'], i['counter'], i['threshold'])
       dst = 'events/{}_{}'.format(os.path.dirname(src).split('/')[-1], os.path.basename(src))
       shutil.copyfile(src, dst)

