# import libraries
import geopandas as gpd
import os
import pathlib
import json


meta_tags = [
    {"name": "viewport", "content": "width=device-width, initial-scale=1.0"}
]

#My constants
title = 'CAP-378 | Earth Observation'
header_title = "Visualização de dados do GOES-16"
header_description = """Dashboard para a visualização  de informações das descargas elétricas detectadas pelo GLM nos 
últimos minutos. O GLM (Geostationary Lightning Mapper) é um instrumento para detecção de raios intranuvem e nuvem 
solo, e esta a bordo do satélite geoestacionário GOES-16 (Geostationary Operational Enviromental Satellite)"""
logo = 'logo.png'

#Mapbox
FILE_PATH = str(pathlib.Path(__file__).parent.resolve())
credentials = {}
with open(os.path.join(FILE_PATH, 'credentials.txt'), 'r') as f:
    credentials['mapbox'] = f.readlines()[0]

#Get states
shp_brazil = gpd.read_file('.data/shapefiles/brazil.shp')
states = [dict(id=i, name=row['NOMEUF2'], acron=row['SIGLAUF3'], area=row['area'],
               center=(row['geometry'].centroid.x, row['geometry'].centroid.y), geom=row['geometry'])
          for i, row in shp_brazil.iterrows()]

DIR=".data/339"