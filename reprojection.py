path = "/home/dupeljan/Projects/santinels/LC08_L1TP_175028_20190712_20190719_01_T1"
band_name = 'LC08_L1TP_175028_20190712_20190719_01_T1_B10.TIF'
out_image_name = band_name.replace(band_name[-1:-4],'reproj' + band_name[-1:-4])

import numpy as np
import rasterio
from rasterio.warp import calculate_default_transform, Resampling
from rasterio.warp import reproject as rasterio_reproject
import os 


def reproject(band_name,dst_name):
    dst_crs = 'EPSG:4326'
    with rasterio.open(band_name) as src:
        transform, width, height = calculate_default_transform(
            src.crs, dst_crs, src.width, src.height, *src.bounds)
        kwargs = src.meta.copy()
        kwargs.update({
            'crs': dst_crs,
            'transform': transform,
            'width': width,
            'height': height
        })

        with rasterio.open(dst_name, 'w', **kwargs) as dst:
            for i in range(1, src.count + 1):
                rasterio_reproject(
                    source=rasterio.band(src, i),
                    destination=rasterio.band(dst, i),
                    src_transform=src.transform,
                    src_crs=src.crs,
                    dst_transform=transform,
                    dst_crs=dst_crs,
                    resampling=Resampling.nearest)
def main():
    j = lambda file_name: os.path.join(path,file_name)
    reproject(map(j,[band_name,out_image_name]))

if __name__ == '__main__':
    main()