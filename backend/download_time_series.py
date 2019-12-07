from datetime import datetime as dt
import os
import numpy as np
import pandas as pd
import subprocess as sp
import pathlib
import geopandas as gpd
from netCDF4 import Dataset
from shapely.geometry import Point
from remap import remap
HERE = str(pathlib.Path(__file__).parent.resolve())

def load_states():
    queries_states = [
        'SIGLAUF3 == "SP"',
#        'SIGLAUF3 == "MG"',
#        'SIGLAUF3 == "RJ"',
#        'SIGLAUF3 == "PA"',
#        'SIGLAUF3 == "TO"',
#        'SIGLAUF3 == "RR"',
#        'SIGLAUF3 == "BA"',
#        'SIGLAUF3 == "PI"',
#        'SIGLAUF3 == "CE"', 
#        'SIGLAUF3 == "RS"',
#        'SIGLAUF3 == "PR"',
#        'SIGLAUF3 == "SC"',
#        'SIGLAUF3 == "MT"',
#        'SIGLAUF3 == "GO"',
#        'SIGLAUF3 == "MS"'
    ]
    gdf = gpd.read_file(os.path.join(HERE, 'shapefiles/estadosl_2007.shp'))
    gdfs = [gdf.query(query) for query in queries_states]
    return pd.concat(gdfs)

def create_dataframe_abi2(path_abi, time):
    files = [os.path.join(path_abi, file) for file in os.listdir(path_abi)]
    df = gpd.read_file(os.path.join(HERE, 'shapefiles/estadosl_2007.shp'))
    
    print(files[0])
    data = dict()
    data['start_scan'] = []
    data['end_scan'] = []
    data['year'] = []
    data['julian_day'] = []
    data['hour'] = []
    data['minute'] = []
    data['state'] = []
    data['min'] = []
    data['mean'] = []
    data['std'] = []
    data['max'] = []
    data['timestamp'] = []
    timestamp = time['t']
    
    for file in files:
        if not file.endswith('.nc'):
            continue
        filename = file.split('/')[-1]

        start_scan = filename[27:41]
        end_scan = filename[43:57]
        y = start_scan[:4]
        jd = start_scan[4:7]
        h = start_scan[7:9]
        m = start_scan[9:11]
        
        for _, state in df.iterrows():
            
            print('Geting values from %s...'%state['NOMEUF2'])
            bbox = state['geometry'].bounds            
            grid = remap(file, bbox, 1, 'NETCDF').ReadAsArray()
            data['min'].append(np.min(grid))
            data['mean'].append(np.mean(grid))
            data['max'].append(np.max(grid))
            data['std'].append(np.std(grid))
            data['state'].append(state['NOMEUF2'])
            data['start_scan'].append(start_scan)
            data['end_scan'].append(end_scan)
            data['year'].append(y)
            data['julian_day'].append(jd)
            data['hour'].append(h)
            data['minute'].append(m)
            data['timestamp'].append(timestamp)
            
    output_csv = '/home/adriano/earth-observation/.data/csv/abi'#path_abi.replace('nc', 'csv')
    csv_filename = '%s__'%time['t']
    csv_filename += '%s_s%s%s%s%s' % ('ABI-L2-CMIPF', time['y'], time['d'], 
                                     time['h'], time['m'][0])
    csv_filename += '_e%s%s%s%s.csv' % (time['y'], time['d'], time['h'], 
                                        time['m'][-1])
    
    if not os.path.exists(output_csv):
        os.makedirs(output_csv)
    df = pd.DataFrame(data)
    filename = os.path.join(output_csv, csv_filename)
    df.to_csv(filename, index=False)
    
    print('CSV ABI file saved in ', filename)
    
    
    
    
def create_dataframe_abi(path_abi, time):   
    print('Creating ABI dataframe...')
    files = [os.path.join(path_abi, file) for file in os.listdir(path_abi)]
    df = load_states()
    
    print(files[0])
    data = dict()
    data['start_scan'] = []
    data['end_scan'] = []
    data['year'] = []
    data['julian_day'] = []
    data['hour'] = []
    data['minute'] = []
    data['lon'] = []
    data['lat'] = []
    data['state'] = []
    data['value'] = []
    data['ind_x'] = []
    data['ind_y'] = []
    data['rows'] = []
    data['cols'] = []
    data['timestamp'] = []
    timestamp = time['t']
    
    for file in files:
        filename = file.split('/')[-1]

        start_scan = filename[27:41]
        end_scan = filename[43:57]
        y = start_scan[:4]
        jd = start_scan[4:7]
        h = start_scan[7:9]
        m = start_scan[9:11]
        
        for _, state in df.iterrows():
            print('Geting values from %s...'%state['NOMEUF2'])
            bbox = state['geometry'].bounds            
            grid = remap(file, bbox, 1, 'NETCDF').ReadAsArray()
            lons = np.linspace(bbox[0], bbox[2], grid.shape[1])
            lats = np.linspace(bbox[1], bbox[3], grid.shape[0])
            rows = grid.shape[0]
            cols = grid.shape[1]
            for x in range(rows):
                for y in range(cols):
                    data['rows'].append(rows)
                    data['cols'].append(cols)
                    data['ind_x'].append(x)
                    data['ind_y'].append(y)
                    data['lon'].append(lons[y])
                    data['lat'].append(lats[x])
                    data['value'].append(grid[x][y])
                    data['state'].append(state['NOMEUF2'])
                    data['start_scan'].append(start_scan)
                    data['end_scan'].append(end_scan)
                    data['year'].append(y)
                    data['julian_day'].append(jd)
                    data['hour'].append(h)
                    data['minute'].append(m)
                    data['timestamp'].append(timestamp)
            
    output_csv = path_abi.replace('nc', 'csv')
    csv_filename = '%s__'%time['t']
    csv_filename += '%s_s%s%s%s%s' % ('ABI-L2-CMIPF', time['y'], time['d'], 
                                     time['h'], time['m'][0])
    csv_filename += '_e%s%s%s%s.csv' % (time['y'], time['d'], time['h'], 
                                        time['m'][-1])
    
    if not os.path.exists(output_csv):
        os.makedirs(output_csv)
    df = pd.DataFrame(data)
    filename = os.path.join(output_csv, csv_filename)
    df.to_csv(filename, index=False)
    

def create_dataframe_glm(path_glm, time):   
    print('Creating GLM dataframe...')
    files = [os.path.join(path_glm, file) for file in os.listdir(path_glm)]
    df = gpd.read_file(os.path.join(HERE, 'shapefiles/estadosl_2007.shp'))
    
    data = dict()
    data['start_scan'] = []
    data['end_scan'] = []
    data['year'] = []
    data['julian_day'] = []
    data['hour'] = []
    data['minute'] = []
    data['flash_lon'] = []
    data['flash_lat'] = []
    data['geometry'] = []
    data['state'] = []
    data['timestamp'] = []
    timestamp = time['t']
    
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
            data['timestamp'].append(timestamp)
            state = 'OUTSIDE'
            for _, row in df.iterrows():
                if row['geometry'].contains(point):
                    state = row['NOMEUF2']
                    
            data['state'].append(state)
            
    output_csv = path_glm.replace('nc', 'csv')
    output_csv = '/home/adriano/earth-observation/.data/csv/glm'
    csv_filename = '%s__'%time['t']
    csv_filename += '%s_s%s%s%s%s' % ('GLM-L2-LCFA', time['y'], time['d'], 
                                     time['h'], time['m'][0])
    csv_filename += '_e%s%s%s%s.csv' % (time['y'], time['d'], time['h'], 
                                        time['m'][-1])
    
    if not os.path.exists(output_csv):
        os.makedirs(output_csv)
    df = pd.DataFrame(data)
#    output_csv = '/home/adriano/earth-observation/.data/csv/glm/'
    filename = os.path.join(output_csv, csv_filename)
    df.to_csv(filename, index=False)
    print('CSV GLM file saved in ', filename)
    
    

def download_abi(time):
    query = make_query(time['y'], time['d'], time['h'], 'ABI-L2-CMIPF')
    path = query.split(' ')[-1]    
    filenames = get_files(query, time)
    filenames = list(filter(lambda x: 'M6C13' in x, filenames))
    download_out = 'store/nc/%s/%s-%s'%(path, time['m'][0], time['m'][-1])
    download_out = download_out.replace('//', '/')
    if not os.path.exists(download_out):
        os.makedirs(download_out)
    
    for filename in filenames:
        print('Downloading %s%s...'%(path, filename))
        query = 'aws s3 cp s3://%s%s %s'%(path, filename, download_out)
        out = sp.Popen([query], shell=True, stdout=sp.PIPE)
        _ = out.communicate()[0].decode('utf-8')
    print('All files ABI downloaded!')
    print('%s day of %s from %s:%s - %s:%s'%(time['d'], time['y'],
            time['h'], time['m'][0], 
            time['h'], time['m'][-1]))
    
    return download_out
    
    
def download_glm(time):
    query = make_query(time['y'], time['d'], time['h'], 'GLM-L2-LCFA')
    path = query.split(' ')[-1]    
    filenames = get_files(query, time)
    download_out = 'store/nc/%s/%s-%s'%(path, time['m'][0], time['m'][-1])
    download_out = download_out.replace('//', '/')
    if not os.path.exists(download_out):
        os.makedirs(download_out)
    
    for filename in filenames:
        print('Downloading %s%s...'%(path, filename))
        query = 'aws s3 cp s3://%s%s %s'%(path, filename, download_out)
        out = sp.Popen([query], shell=True, stdout=sp.PIPE)
        _ = out.communicate()[0].decode('utf-8')
    print('All files GLM downloaded!')
    print('%s day of %s from %s:%s - %s:%s'%(time['d'], time['y'],
            time['h'], time['m'][0], 
            time['h'], time['m'][-1]))
    return download_out

    
def get_files(query, time):
    def contains(filename, filters):
        if not filename.endswith('.nc'):
            return False

        for f in filters:
            if f in filename:
                return True

        return False

    out = sp.Popen([query], shell=True, stdout=sp.PIPE)
    out = out.communicate()[0].decode('utf-8')
    files = out.split()
    
    filters = ['_s%s%s%s%s' % (time['y'], time['d'], time['h'], m) 
                for m in time['m']]
    filenames = sorted(
            list(filter(lambda file: contains(file, filters), files)))
    
    return filenames


def make_query(year, day, hour, sensor='GLM-L2-LCFA'):
    query = "aws s3 ls noaa-goes16/%s/%s/%s/%s/"%(sensor, year, day, hour)
    return query
  
    
def get_time():
    def julian_day(year, month, day):
        return str(dt.strptime('%s-%s-%s'%(year, month, day), '%Y-%m-%d')
                   .timetuple().tm_yday).zfill(3)
        
    now = dt.utcnow()
    year = now.year
    day = julian_day(now.year, now.month, now.day)
    hour = now.hour
    minute = now.minute
    
    day, hour, minute = int(day), int(hour), int(minute)
    if minute%10 == 0 and minute > 0:
        minute = list(range(minute-10, minute+1))
        return dict(d='%s'%str(day).zfill(3), h='%s'%str(hour).zfill(2), 
                    m=[str(x).zfill(2) for x in minute])
    if minute < 10:
        minute = list(map(lambda x: str(x).zfill(2), range(50, 60)))
        hour -= 1
    elif minute < 20:
        minute = list(map(lambda x: str(x).zfill(2), range(0, 11)))
    elif minute < 30:
        minute = list(map(lambda x: str(x).zfill(2), range(10, 21)))
    elif minute < 40:
        minute = list(map(lambda x: str(x).zfill(2), range(20, 31)))
    elif minute < 50:
        minute = list(map(lambda x: str(x).zfill(2), range(30, 41)))
    elif minute < 60:
        minute = list(map(lambda x: str(x).zfill(2), range(40, 51)))

    if hour < 0:
        day -= 1
        hour = 23
    
    return dict(d='%s'%str(day).zfill(3), h='%s'%str(hour).zfill(2), m=minute, y=2019, t=int(dt.timestamp(now)))
    

if __name__ == "__main__":
    time = get_time()
    print(time)
    path_glm = download_glm(time)
    path_abi = download_abi(time)
#    path_glm = 'store/nc/noaa-goes16/GLM-L2-LCFA/2019/335/21/20-30'
#    path_abi = 'store/nc/noaa-goes16/ABI-L2-CMIPF/2019/335/21/20-30'
    create_dataframe_glm(path_glm, time)
#    path_abi = '/home/adriano/earth-observation/store/nc/noaa-goes16/ABI-L2-CMIPF/2019/338/22/30-40/'
    create_dataframe_abi2(path_abi, time)
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    