import os
from netCDF4 import Dataset
import pandas as pd
from shapely.geometry import Point


def get_allfiles(path):
    files = sorted([os.path.join(path, file) for file in os.listdir(path)])
    return files


def save_data_glm(path, filename, output):
    files = sorted([os.path.join(path, file) for file in os.listdir(path)])
    # filename = '%s.csv' %(path.replace('/', '-').upper())
    data = {}
    data['start_scan'] = []
    data['end_scan'] = []
    data['year'] = []
    data['julian_day'] = []
    data['hour'] = []
    data['minute'] = []
    data['flash_lon'] = []
    data['flash_lat'] = []
    data['geometry'] = []

    for file in files:
        nc = Dataset(file, 'r')
        file = file.split('/')[-1]

        start_scan = file[20:34]
        end_scan = file[36:50]
        y = start_scan[:4]
        jd = start_scan[4:7]
        h = start_scan[7:9]
        m = start_scan[9:11]

        lons, lats = nc.variables['flash_lon'], nc.variables['flash_lat']

        for lon, lat in zip(lons, lats):
            point = Point(lon, lat)

            data['start_scan'].append(start_scan)
            data['end_scan'].append(end_scan)
            data['year'].append(y)
            data['julian_day'].append(jd)
            data['hour'].append(h)
            data['minute'].append(m)
            data['flash_lon'].append(lon)
            data['flash_lat'].append(lat)
            data['geometry'].append(point)

    if not os.path.exists(output):
        os.makedirs(output)
    df = pd.DataFrame(data)
    df.to_csv('%s'%(os.path.join(output, filename)), index=False)


if __name__ == "__main__":
    path = 'noaa-goes16/GLM-L2-LCFA/2019/323/15'



