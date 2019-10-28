bands_dir_path = '/home/dupeljan/Projects/santinels/tests/LC08_L1TP_175028_20190712_20190719_01_T1'
output_path = '/home/dupeljan/Projects/santinels/tests/output'
shapefile_path = '/home/dupeljan/Projects/santinels/tests/Rostov.shp'

from clipping import clip
from reprojection import reproject
from glob import glob
import os
from pprint import pprint
from shutil import copyfile

def main():
	# Create directories for output
	reproject_dir_name = 'reproject'
	clip_dir_name = 'clip'
	directories = [os.path.join(output_path,reproject_dir_name)]
	directories += [os.path.join(output_path,clip_dir_name)]
	for dir_ in directories: 
		if not os.path.exists(dir_):
			os.makedirs(dir_)
	# Got bands and reproject to appropiate format
	all_landsat_post_bands = glob(os.path.join(bands_dir_path,'*.tif'))
	all_landsat_post_bands.extend( glob(os.path.join(bands_dir_path,'*.TIF')))
	'''
	for band in all_landsat_post_bands:
		print("Reproject " + os.path.basename(band))
		reproject(band, os.path.join(output_path,reproject_dir_name,os.path.basename(band)))
	print('Done reproject')
	'''
	#start clipping 
	all_landsat_post_bands = glob(os.path.join(output_path,reproject_dir_name,'*.tif'))
	all_landsat_post_bands.extend( glob(os.path.join(output_path,reproject_dir_name,'*.TIF')))
	for band in all_landsat_post_bands:
		print('Clip ' + os.path.basename(band))
		dst_path = os.path.join(output_path,clip_dir_name,os.path.basename(band))
		if os.path.isfile(dst_path):
			os.remove(dst_path)
		clip(shapefile_path,band,dst_path)

	print('Done clipping') 
	# Copy metadata
	metadata = glob(os.path.join(bands_dir_path,'*'))
	metadata = list( filter( lambda x: x not in all_landsat_post_bands, metadata ) )
	for i in metadata:
		copyfile(i,os.path.join(output_path,reproject_dir_name,os.path.basename(i)))
		copyfile(i,os.path.join(output_path,clip_dir_name, os.path.basename(i)))

if __name__ == '__main__':
	main()