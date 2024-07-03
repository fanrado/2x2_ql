import numpy as np
import yaml


class geohelper:
    """
    A few assumptions:
        1. map from chip id to the array of pixel id must be a map between integer to 64-elemented array.
        2. ID of pixels is exactly the same as its index. 
    """
    def __init__(self, geo_path='layout-2.4.0.yaml'):
        self.chip_pix = None
        self.vlines = None
        self.hlines = None
        self.geo = None

        # load the single LArPix-v2a anode tile yaml file
        with open(geo_path) as fi:
            self.geo=yaml.full_load(fi)
            self.chip_pix=dict([(chip_id,pix) for chip_id,pix in self.geo['chips']])
            self.vlines=np.linspace(-1*(self.geo['width']/2), self.geo['width']/2, 11)
            self.hlines=np.linspace(-1*(self.geo['height']/2), self.geo['height']/2, 11)

            # these are dumb manipulations I have put together to tessalate the tiles - others likely use a different approach
            self.tile_dy = abs(max(self.vlines))+abs(min(self.vlines))

            self.tile_dx = abs(max(self.hlines))+abs(min(self.hlines))

            # this swap on tiles 7 & 8 are exclusive to Module-1 Bern data alone; this has been fixed for 2x2 operation
            self.displacement={1:(-0.5,1.5), 2:(0.5,1.5), 3:(-0.5,0.5), 4:(0.5,0.5), 5:(-0.5,-0.5), 6:(0.5,-0.5), 7:(0.5,-1.5), 8:(-0.5,-1.5)}

        if not self.geo:
            raise NotImplemented("{} not found. Geometry helper cannot work.".format(geo_path))

    def find_xy(self, tile_id, chip_id, channel_id):
        xc=0; yc=0
        if tile_id in [1,3,5,8]:
            xc = self.geo['pixels'][self.chip_pix[chip_id][channel_id]][1]
            yc = self.geo['pixels'][self.chip_pix[chip_id][channel_id]][2]*-1
        if tile_id in [2,4,6,7]:
            xc = self.geo['pixels'][self.chip_pix[chip_id][channel_id]][1]*-1
            yc = self.geo['pixels'][self.chip_pix[chip_id][channel_id]][2]
        xc += self.tile_dx * self.displacement[tile_id][0]
        yc += self.tile_dy * self.displacement[tile_id][1]
        return xc, yc
    

    ### The combination of IO group, IO channel, and chip ID specify a unique ASIC in the system
    ### IO channels are assigned given the network configuration. This field corresponds to the PACMAN channel upon which data is read in/out from the tile
    ### IO channel assigned to the asic may change, but the physical tile ID is static; multiple IO channels map to the same tile ID
    @staticmethod
    def io_channel_to_tile(io_channel):
        return np.int32(np.floor((io_channel-1-((io_channel-1)%4))/4+1))

    def find_tileid(self, x, y):
        """x, y: (x, y) of ASIC.
        Depends on global variables, tile_dx, tile_dy, and displacement
        return tile id of x, y
        """
        tileid = None
        for k, v in self.displacement.items():
            if (x - self.tile_dx * v[0] > -self.tile_dx/2. and x - self.tile_dx * v[0] < self.tile_dx/2) and (
                y - self.tile_dy * v[1] > -self.tile_dy/2. and y - self.tile_dy * v[1] < self.tile_dy/2):
                return k
        return tileid
    
    def __xy_sign(self, tileid):
        """signs of xy
        """
        if tileid in [1, 3, 5, 8]:
            return (1, -1)
        if tileid in [2, 4, 6, 7]:
            return (-1, 1)
    
    def find_pixel(self, x, y, tileid, tol=0.5*4.434):
        """Find pixel in a tile
        tileid: tile ID to determine sign of (x, y)
        tol: tolerance of accuracy, half of pitch size 4.34 mm
        return pixel index
        """
        if not tileid in [i for i in range(1, 9)]:
            raise NotImplemented("tile ID must be from 1 to 8")
        xsign, ysign = self.__xy_sign(tileid)
        x = xsign * x
        y = ysign * y
        pxl_xy = np.array([[e[1], e[2]] for e in self.geo["pixels"]])
        # substract
        pxl_xy = pxl_xy - np.array([x, y])
        res = np.abs(pxl_xy) < tol
        indices = np.all(res, axis=1)
        if indices.sum() > 1:
            raise ValueError("Multiple associations appear. Check the tolerance, pitch size, and input (x, y)")
        if indices.sum() == 0:
            raise ValueError("Not find any association. Check the tolerance, pitch size, and input (x, y)")
        return self.geo['pixels'][indices.nonzero()[0][0]]
                
    def find_ids(self, x, y):
        """
        return tile id, chip id, channel id
        """
        tileid = None
        chipid = None
        channelid = None
        tileid = self.find_tileid(x, y)
        x = x - self.tile_dx * self.displacement[tileid][0]
        y = y - self.tile_dx * self.displacement[tileid][1]
        pxlidx = self.find_pixel(x, y, tileid)
        names = ['chipid', 'pixelid']
        formats = ['i4', '(64,)f8']
        chipid_type = dict(names = names, formats = formats)
        chipids = np.fromiter(self.chip_pix.items(), dtype=chipid_type)
        ids = (np.abs(chipids['pixelid'] - pxlidx[0])<1E-6).nonzero()
        if ids[0].shape == (1, ):
            chipid = chipids['chipid'][ids[0][0]]
        else:
            raise ValueError("Find multiple or no correspondence by pixel index {}".format(pxlidx))
        if ids[1].shape == (1, ):
            channelid = ids[1][0]
        else:
            raise ValueError("Find multiple or no correspondence by pixel index {}".format(pxlidx))
        # print(ids[0])
        return (tileid, chipid, channelid)
    
if __name__ == '__main__':
    myhelper = geohelper()
    print("test tileid {}, chip_id {}, channel_id {}".format(8, 102, 3))
    x, y = myhelper.find_xy(8, 102, 3)
    print("x, y: {}, {}".format(x, y))
    tileid = myhelper.find_tileid(x, y)
    print("x, y: {}, {}, tileid: {}".format(x, y, tileid))

    print("Test pixel index {}".format(3202), myhelper.geo["pixels"][3202])
    x = myhelper.geo["pixels"][3202][1]
    y = myhelper.geo["pixels"][3202][2]
    print("Module 3, (+, -) on (x, y): {} {}, pixel idx".format(x, y), myhelper.find_pixel(x, -y, 3))
    print("Module 3, (+, -) on (x, y): {} {}, pixel idx".format(x+2, y), myhelper.find_pixel(x+2, -y, 3))
    print("Module 7, (-, +) on (x, y): {} {}, pixel idx".format(x, y), myhelper.find_pixel(-x, y, 7))