path = "/home/dupeljan/Projects/santinels/tests"
band_name = 'LC08_L1TP_175028_20190712_20190719_01_T1/LC08_L1TP_175028_20190712_20190719_01_T1_B10.TIF'
out_image_name = 'python croped tiff.TIF'
shp_file_name = 'rostov.shp'

import rasterio
import rasterio.mask
import os
import pyproj
from fiona.crs import from_epsg

from pyproj import Proj, transform
import fiona
from fiona.crs import from_epsg

def clip(shp_name,band_name,dst_name):
	shapefile =  fiona.open(shp_name, "r") 
	features = [feature["geometry"] for feature in shapefile]

	src = rasterio.open(band_name)
	out_image, out_transform = rasterio.mask.mask(src,features,crop=True)
	out_meta = src.meta.copy()

	out_meta.update({"driver": "GTiff",
  	           "height": out_image.shape[1],
                 "width": out_image.shape[2],
                 "transform": out_transform})
	with rasterio.open(dst_name, "w", **out_meta) as dest:
		dest.write(out_image)

def main():
	j = lambda file_name: os.path.join(path,file_name)
	clip(map(j,[shp_file_name,band_name,out_image_name]))

if __name__ == '__main__':
	main()