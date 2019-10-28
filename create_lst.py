output_path = '/home/dupeljan/Projects/santinels/tests'
bands_path = '/home/dupeljan/Projects/santinels/tests/LC08_L1TP_175028_20190712_20190719_01_T1'


import os
from glob import glob
from pprint import pprint

import numpy as np
from osgeo import gdal
from osgeo import ogr
import os, sys, struct
# qgis.core import *
from numpy import zeros
from numpy import logical_and
import traceback

class compute_lst:
	def __init__(self, bands_path,output_path):
		self.all_landsat_post_bands = glob(os.path.join(bands_path,'*.tif'))
		self.all_landsat_post_bands.extend( glob(os.path.join(bands_path,'*.TIF')))
		self.metadata = glob(os.path.join(bands_path,'*MTL.txt'))[0]
		self.termal_band_num = 10
		self.red_band_num = 4
		self.nir_band_num = 5
		self.file_type = 'GTiff'
		self.sensor_type = 'Landsat TIRS'
		self.unit = 'Celsius'
		#pprint(self.all_landsat_post_bands)
		self.output_path = output_path
		self.radiance_filename = 'radiance.TIF'
		self.brightnes_filename = 'brightnes.TIF'
		self.NDVI_filename = 'NDVI.TIF'
		self.LSE_filename = 'LSE.TIF'
		self.LST_filename = 'LST.TIF'

	
	def get_band(self,number):
		for band in self.all_landsat_post_bands:
			if band.find('B' + str(number) + '.') != -1:
				return band
		return ''

	def readMetadataFile(self, metadataPath, sensorType, gain):
		try:
			metadata = open(metadataPath, 'r')
			output = {} #Dict
			for metadataLine in metadata.readlines():
				if ("=") in metadataLine:
					line = metadataLine.split("=") 
					output[line[0].strip()] = line[1].strip() 
			
			#Change the variables to be read from the metadata file according to the sensor selected
			if (sensorType == 'Landsat 8'):
				K1_Band10 = float(output['K1_CONSTANT_BAND_10'])
				K2_Band10 = float(output['K2_CONSTANT_BAND_10'])
				K1_Band11 = float(output['K1_CONSTANT_BAND_11'])
				K2_Band11 = float(output['K2_CONSTANT_BAND_11'])
				RadAddBand10  = float(output['RADIANCE_ADD_BAND_10'])
				RadAddBand11  = float(output['RADIANCE_ADD_BAND_11'])
				RadMultFactorBand10 = float(output['RADIANCE_MULT_BAND_10'])
				RadMultFactorBand11 = float(output['RADIANCE_MULT_BAND_11'])
				#Return all the required variables
				return {'K1_Band10':K1_Band10, 'K2_Band10':K2_Band10, 'K1_Band11':K1_Band11, 'K2_Band11':K2_Band11,\
						'RadAddBand10':RadAddBand10, 'RadAddBand11':RadAddBand11, 'RadMultFactorBand10':RadMultFactorBand10,\
						'RadMultFactorBand11':RadMultFactorBand11}
				
			elif (sensorType == 'Landsat 7'):
				if (gain == 'High'): #If the image was taken in a high gain
					QCALMAX = float(output['QUANTIZE_CAL_MAX_BAND_6_VCID_2'])
					QCALMIN = float(output['QUANTIZE_CAL_MIN_BAND_6_VCID_2'])
					LMAX = float(output['RADIANCE_MAXIMUM_BAND_6_VCID_2'])
					LMIN = float(output['RADIANCE_MINIMUM_BAND_6_VCID_2'])
					#Return all the required variables
					return {'QCALMAX':QCALMAX, 'QCALMIN':QCALMIN, 'LMAX':LMAX, 'LMIN':LMIN}
				
				elif (gain == 'Low'): #If the image was taken in a low gain
					QCALMAX = float(output['QUANTIZE_CAL_MAX_BAND_6_VCID_1'])
					QCALMIN = float(output['QUANTIZE_CAL_MIN_BAND_6_VCID_1'])
					LMAX = float(output['RADIANCE_MAXIMUM_BAND_6_VCID_1'])
					LMIN = float(output['RADIANCE_MINIMUM_BAND_6_VCID_1'])
					#Return all the required variables
					return {'QCALMAX':QCALMAX, 'QCALMIN':QCALMIN, 'LMAX':LMAX, 'LMIN':LMIN}
				
			elif (sensorType == 'Landsat 5'):
					QCALMAX = float(output['QUANTIZE_CAL_MAX_BAND_6'])
					QCALMIN = float(output['QUANTIZE_CAL_MIN_BAND_6'])
					LMAX = float(output['RADIANCE_MAXIMUM_BAND_6'])
					LMIN = float(output['RADIANCE_MINIMUM_BAND_6'])
					#Return all the required variables
					return {'QCALMAX':QCALMAX, 'QCALMIN':QCALMIN, 'LMAX':LMAX, 'LMIN':LMIN}
			
			#Close the metadata file 
			metadata.close
		except RuntimeError:
			#self.error.emit(e, traceback.format_exc())
			print("Error occure while readMetadataFile execution")

	def calcTIRSRadiance(self, outputPath, calibFactor=0.0):
		try:
			#The code below opens the datasets
			dsThermalBand = gdal.Open(self.get_band(self.termal_band_num), gdal.GA_ReadOnly)
			#self.progress.emit(20)
		except IOError:
			#self.error.emit(e, traceback.format_exc())
			print("Exception")
		try:
			#Capture the Red and the NIR bands
			thermalBand = dsThermalBand.GetRasterBand(1)
				
			# get numbers of rows and columns in the Red and NIR bands
			cols = dsThermalBand.RasterXSize
			rows = dsThermalBand.RasterYSize
			#Read the metadata from the metadata file
			metaVariables       = self.readMetadataFile(self.metadata, 'Landsat 8', '')
			RadMultFactorBand10 = float(metaVariables['RadMultFactorBand10'])
			RadAddBand10        = float(metaVariables['RadAddBand10'])
			RadMultFactorBand11 = float(metaVariables['RadMultFactorBand11'])
			RadAddBand11        = float(metaVariables['RadAddBand11'])           
			# create the output image
			driver = gdal.GetDriverByName(self.file_type)
			radianceDS = driver.Create(outputPath, cols, rows, 1, gdal.GDT_Float32)
			radianceDS.SetGeoTransform(dsThermalBand.GetGeoTransform())
			radianceDS.SetProjection(dsThermalBand.GetProjection())
			radianceBand = radianceDS.GetRasterBand(1)
			#self.progress.emit(40)
			
			#Read the block sizes of the thermal band being processed
			blockSizes = radianceBand.GetBlockSize()
			xBlockSize = blockSizes[0]
			yBlockSize = blockSizes[1]
					
			# loop through rows of blocks
			for i in range(0, rows, yBlockSize):
				if i + yBlockSize < rows:
					numRows = yBlockSize
				else:
					numRows = rows - i
				
				# now loop through the blocks in the row
				for j in range(0, cols, xBlockSize):
					if j + xBlockSize < cols:
						numCols = xBlockSize
					else:
						numCols = cols - j
						
					if (self.termal_band_num == 10):
						#If the band selected is TIRS band 11
						thermalBandData = thermalBand.ReadAsArray(j, i, numCols, numRows).astype('f')
						# do the calculation
						radiance = np.multiply(thermalBandData, RadMultFactorBand10)
						radiance = np.add(radiance, RadAddBand10)
						radiance = np.subtract(radiance, float(calibFactor))
						# write the data
						radianceDS.GetRasterBand(1).WriteArray(radiance,j,i)
					else:
						#If the band selected is TIRS band 11
						thermalBandData = thermalBand.ReadAsArray(j, i, numCols, numRows).astype('f')
						# do the calculation
						#mask = np.greater(thermalBandData, 0)
						radiance = np.multiply(thermalBandData, RadMultFactorBand11)
						radiance = np.add(radiance, RadAddBand11)
						radiance = np.subtract(radiance, float(calibFactor))
						# write the data
						radianceDS.GetRasterBand(1).WriteArray(radiance,j,i)
						#radianceDS.WriteArray(radiance, j, i)
						
			#self.progress.emit(90)
			# set the histogram
			radianceDS.GetRasterBand(1).SetNoDataValue(-99)
			histogram = radianceDS.GetRasterBand(1).GetDefaultHistogram()
			radianceDS.GetRasterBand(1).SetDefaultHistogram(histogram[0], histogram[1], histogram[3])

			radianceDS    = None
			dsThermalBand = None
				
		except RuntimeError:
			print("Exception")

	def calcBrightnessTemp(self, radiance, outputPath):
		try:
			#The code below opens the datasets
			dsRadianceBand = gdal.Open(radiance, gdal.GA_ReadOnly)
			#self.progress.emit(20)
		except IOError:
			#self.error.emit(e, traceback.format_exc())
			print('Exception')
		try:
			radianceBand = dsRadianceBand.GetRasterBand(1)
				
			# get numbers of rows and columns in the Red and NIR bands
			cols = dsRadianceBand.RasterXSize
			rows = dsRadianceBand.RasterYSize
			if (self.sensor_type == 'Landsat TIRS'):
				if (self.termal_band_num == 10):
					K1 = 774.89
					K2 = 1321.08
				elif (self.termal_band_num ==11):
					K1 = 480.89
					K2 = 1201.14
			elif (self.sensor_type == 'Landsat ETM+'):
				K1 = 660.09
				K2 = 1282.71
			elif (self.sensor_type == 'Landsat TM'):
				K1 = 607.76
				K2 = 1260.56
			elif (self.sensor_type == 'ASTER'):
				if (int(bandNo) == 10):
					K1 = 3047.47
					K2 = 1736.18
				elif (int(bandNo) == 11):
					K1 = 2480.93
					K2 = 1666.21
				elif (int(bandNo) == 12):
					K1 = 1930.80
					K2 = 1584.72
				elif (int(bandNo) == 13):
					K1 = 865.65
					K2 = 1349.82
				elif (int(bandNo) == 14):
					K1 = 649.60
					K2 = 1274.49
				
			# Create the output image
			driver = gdal.GetDriverByName(self.file_type)
			brightnessDS = driver.Create(outputPath, cols, rows, 1, gdal.GDT_Float32)
			brightnessDS.SetGeoTransform(dsRadianceBand.GetGeoTransform())
			brightnessDS.SetProjection(dsRadianceBand.GetProjection())
			brightnessBand = brightnessDS.GetRasterBand(1)
			#self.progress.emit(40)
			#Read the block sizes of the thermal band being processed
			blockSizes = brightnessBand.GetBlockSize()
			xBlockSize = blockSizes[0]
			yBlockSize = blockSizes[1]
					
			# loop through rows of blocks
			for i in range(0, rows, yBlockSize):
				if i + yBlockSize < rows:
					numRows = yBlockSize
				else:
					numRows = rows - i
				
				# now loop through the blocks in the row
				for j in range(0, cols, xBlockSize):
					if j + xBlockSize < cols:
						numCols = xBlockSize
					else:
						numCols = cols - j
						
					radianceBandData = radianceBand.ReadAsArray(j, i, numCols, numRows).astype('f')
					# do the calculation
					bt_upper = K2
					bt_lower = np.divide(K1, radianceBandData)
					bt_lower = np.add(bt_lower, 1)
					bt_lower = np.log(bt_lower)
					bt = np.divide(bt_upper, bt_lower)

					# write the data
					brightnessDS.GetRasterBand(1).WriteArray(bt,j,i)

			#self.progress.emit(90)          
			# set the histogram
			brightnessDS.GetRasterBand(1).SetNoDataValue(-99)
			histogram = brightnessDS.GetRasterBand(1).GetDefaultHistogram()
			brightnessDS.GetRasterBand(1).SetDefaultHistogram(histogram[0], histogram[1], histogram[3])

			brightnessDS    = None
			dsRadianceBand  = None
			
				
		except RuntimeError:
			print('Exception')

	def calcNDVI(self, outputPath):
		try:
			#The code below opens the datasets
			dsRedBand = gdal.Open(self.get_band(self.red_band_num), gdal.GA_ReadOnly)
			dsNIRBand = gdal.Open(self.get_band(self.nir_band_num), gdal.GA_ReadOnly)
			#self.progress.emit(20)
		except IOError:
			#self.error.emit(e, traceback.format_exc())
			print('Exception')
		try:
			#Capture the Red and the NIR bands
			redBand = dsRedBand.GetRasterBand(1)
			NIRBand = dsNIRBand.GetRasterBand(1)

			# get numbers of rows and columns in the Red and NIR bands
			colsRed = dsRedBand.RasterXSize
			rowsRed = dsRedBand.RasterYSize

			# create the output image
			driver = gdal.GetDriverByName(self.file_type)
			ndviDS = driver.Create(outputPath, colsRed, rowsRed, 1, gdal.GDT_Float32)
			ndviDS.SetGeoTransform(dsRedBand.GetGeoTransform())
			ndviDS.SetProjection(dsRedBand.GetProjection())
			ndviBand = ndviDS.GetRasterBand(1)
			#self.progress.emit(40)
				
			# loop through rows of blocks
			blockSize = 64
			for i in range(0, rowsRed, blockSize):
				if i + blockSize < rowsRed:
					numRows = blockSize
				else:
					numRows = rowsRed - i

				# now loop through the blocks in the row
				for j in range(0, colsRed, blockSize):
					if j + blockSize < colsRed:
						numCols = blockSize
					else:
						numCols = colsRed - j
					# get the data
					redBandData = redBand.ReadAsArray(j, i, numCols, numRows).astype('f')
					NIRBandData = NIRBand.ReadAsArray(j, i, numCols, numRows).astype('f')
					# do the calculation
					mask = np.greater(redBandData + NIRBandData, 0)
					ndvi = np.choose(mask, (-99, (NIRBandData - redBandData) / (NIRBandData + redBandData)))
					# write the data
					ndviDS.GetRasterBand(1).WriteArray(ndvi, j, i)
			
			#self.progress.emit(90)
			# set the histogram
			ndviDS.GetRasterBand(1).SetNoDataValue(-99)
			histogram = ndviDS.GetRasterBand(1).GetDefaultHistogram()
			ndviDS.GetRasterBand(1).SetDefaultHistogram(histogram[0], histogram[1], histogram[3])

			ndviDS   = None
			redBand  = None
			NIRBand  = None
					
		except RuntimeError:
			#self.error.emit(e, traceback.format_exc())
			print('Exception')
			
	def zhangLSEalgorithm(self, ndviRaster, outputPath):
		try:
			#The code below opens the datasets
			dsNdviBand = gdal.Open(ndviRaster, gdal.GA_ReadOnly)
			#self.progress.emit(20)
		except IOError:
			#self.error.emit(e, traceback.format_exc())
			print('Exception')
			
		try:
			
			#Capture the Red and the NIR bands
			ndviBand = dsNdviBand.GetRasterBand(1)
					
			# get number of rows and columns in the Red and NIR bands
			cols = dsNdviBand.RasterXSize
			rows = dsNdviBand.RasterYSize
				
			# create the output image
			driver = gdal.GetDriverByName(self.file_type)
			lseDS = driver.Create(outputPath, cols, rows, 1, gdal.GDT_Float32)
			lseDS.SetGeoTransform(dsNdviBand.GetGeoTransform())
			lseDS.SetProjection(dsNdviBand.GetProjection())
			radianceBand = lseDS.GetRasterBand(1)
			
			#self.progress.emit(40)
			#Read the block sizes of the thermal band being processed
			blockSizes = radianceBand.GetBlockSize()
			xBlockSize = blockSizes[0]
			yBlockSize = blockSizes[1]
						
			# loop through rows of blocks
			for i in range(0, rows, yBlockSize):
				if i + yBlockSize < rows:
					numRows = yBlockSize
				else:
					numRows = rows - i
					
				# now loop through the blocks in the row
				for j in range(0, cols, xBlockSize):
					if j + xBlockSize < cols:
						numCols = xBlockSize
					else:
						numCols = cols - j
					# get the data
					ndviData  = ndviBand.ReadAsArray(j, i, numCols, numRows).astype('f')
					#Do the calculation here
					conditionList = [np.logical_and(ndviData < -0.185, ndviData >= -1), np.logical_and(ndviData >= -0.185, ndviData <= 0.157), np.logical_and(ndviData >= 0.157, ndviData <= 0.727), np.logical_and(ndviData > 0.727, ndviData <= 1)]
					mixedPixels   = np.log(ndviData)
					mixedPixels   = np.multiply(mixedPixels, 0.047)
					mixedPixels   = np.add(mixedPixels, 1.009)
					choiceList    = [0.995, 0.985, mixedPixels, 0.990]
					lse           = np.select(conditionList, choiceList)
					
					# write the data
					lseDS.GetRasterBand(1).WriteArray(lse, j, i)
			
			#self.progress.emit(90)
			# set the histogram
			lseDS.GetRasterBand(1).SetNoDataValue(-99)
			histogram = lseDS.GetRasterBand(1).GetDefaultHistogram()
			lseDS.GetRasterBand(1).SetDefaultHistogram(histogram[0], histogram[1], histogram[3])
	
			lseDS      = None
			dsNdviBand = None
		except RuntimeError:
			#self.error.emit(e, traceback.format_exc())
			print('Exception')

	def planckEquation(self, bt, lse, outputPath):
		bandNo= self.termal_band_num
		try:
			#The code below opens the datasets
			dsBT  = gdal.Open(bt, gdal.GA_ReadOnly)
			dsLSE = gdal.Open(lse, gdal.GA_ReadOnly)
			#self.progress.emit(20)
		except IOError:
			#self.error.emit(e, traceback.format_exc())
			print('Exception')
		try:
			#Set the wavelengths of the emitted radiances according to the sensor selected
			if (self.sensor_type == 'Landsat TIRS'):
				if (int(bandNo) == 10):
					wl = 11.395
				elif (int(bandNo) == 11):
					wl = 12.005
			elif (self.sensor_type == 'Landsat ETM+'):
				wl = 11.45
			elif (self.sensor_type == 'Landsat TM'):
				wl = 11.45
			elif (self.sensor_type == 'ASTER'):
				if (int(bandNo) == 10):
					wl = 8.291
				elif (int(bandNo) == 11):
					wl = 8.634
				elif (int(bandNo) == 12):
					wl = 9.075
				elif (int(bandNo) == 13):
					wl = 10.657
				elif (int(bandNo) == 14):
					wl = 11.318
			#Capture the LSE and the Brightness Temperature bands
			btBand = dsBT.GetRasterBand(1)
			lseBand = dsLSE.GetRasterBand(1)
					
			# get numbers of rows and columns in the Red and NIR bands
			colsBT = dsBT.RasterXSize
			rowsBT = dsBT.RasterYSize
				
			colsLSE = dsLSE.RasterXSize
			rowsLSE = dsLSE.RasterYSize
				
			# create the output image
			driver = gdal.GetDriverByName(self.file_type)
			lstDS = driver.Create(outputPath, colsBT, rowsBT, 1, gdal.GDT_Float32)
			lstDS.SetGeoTransform(dsBT.GetGeoTransform())
			lstDS.SetProjection(dsBT.GetProjection())
			lstBand = lstDS.GetRasterBand(1)
			#self.progress.emit(40)
					
			# loop through rows of blocks
			blockSize = 64
			for i in range(0, rowsBT, blockSize):
				if i + blockSize < rowsBT:
					numRows = blockSize
				else:
					numRows = rowsBT - i
				
				# now loop through the blocks in the row
				for j in range(0, colsBT, blockSize):
					if j + blockSize < colsBT:
						numCols = blockSize
					else:
						numCols = colsBT - j
						
					# get the data
					lseData = lseBand.ReadAsArray(j, i, numCols, numRows).astype('f')
					btData  = btBand.ReadAsArray(j, i, numCols, numRows).astype('f')
				
					# do the calculation
					cond_list   = [lseData > 0, lseData <= 0]
					choice_list = [np.log(lseData), 0]
					log_lse     = np.select(cond_list, choice_list)
					lst_upper   = btData
					lst_lower   = np.divide(btData, 14380)
					lst_lower   = np.multiply(lst_lower, wl)
					lst_lower   = np.multiply(lst_lower, log_lse)
					lst_lower   = np.add(lst_lower, 1)
					
					#Convert the temperature according to the unit selected
					if (self.unit == 'Kelvin'):
						lst = np.divide(lst_upper, lst_lower)
					elif (self.unit == 'Celsius'):
						#Celsius = Kelvin - 273.15
						lst = np.divide(lst_upper, lst_lower)
						lst = np.subtract(lst, 273.15)
					else:
						#Fahrenheit = ((kelvin - 273.15) x 1.8) + 32
						lst = np.divide(lst_upper, lst_lower)
						lst = np.subtract(lst, 273.15)
						lst = np.multiply(lst, 1.8)
						lst = np.add(lst, 32)
					# write the data
					lstDS.GetRasterBand(1).WriteArray(lst, j, i)
					
			#self.progress.emit(90)
			# set the histogram
			lstDS.GetRasterBand(1).SetNoDataValue(-99)
			histogram = lstDS.GetRasterBand(1).GetDefaultHistogram()
			lstDS.GetRasterBand(1).SetDefaultHistogram(histogram[0], histogram[1], histogram[3])
				
			lstDS    = None
			lseBand  = None
			btBand   = None
			
				
		except RuntimeError:
			#self.error.emit(e, traceback.format_exc())
			print('Exception')

	def calcLST(self):
		radiance_path = os.path.join(self.output_path,self.radiance_filename)
		brightnes_path = os.path.join(self.output_path,self.brightnes_filename)
		NDVI_path = os.path.join(self.output_path,self.NDVI_filename)
		LSE_path = os.path.join(self.output_path,self.LSE_filename)
		LST_path = os.path.join(self.output_path,self.LST_filename)
		print('Calculate radiance')
		self.calcTIRSRadiance(radiance_path) 
		print('Calculate brightnes')
		self.calcBrightnessTemp(radiance_path,brightnes_path)
		print('Calculate NDVI')
		self.calcNDVI(NDVI_path)
		print('Calculate Land Surface emicity')
		self.zhangLSEalgorithm(NDVI_path,LSE_path)
		print('Calculate Land Surface Temperature')
		self.planckEquation(bt= brightnes_path, lse= LSE_path,outputPath= LST_path)
		print('Success')
				
def main():
	lst = compute_lst(bands_path,output_path)
	lst.calcLST()
	

if __name__ == '__main__':
	main() 
