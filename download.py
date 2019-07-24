'''
Program allows to search landsat8 scence for defined area
and download it from earth explorer website
'''
import os
username = os.environ['LANDSATXPLORE_USERNAME']
pswd = os.environ['LANDSATXPLORE_PASSWORD'] 

output_dir = "/home/dupeljan/Projects/santinels/maps"

#landsatxplore download -u "dupeljan" -p  -o "/home/dupeljan/Projects/santinels/maps" LT51960471995178MPS00
#left up corner
ll = {
	"longitude": 38.83829, 
	"latitude": 44.96209,
}
#right bottom corter
ur = {
	 "longitude": 39.15415, 
	 "latitude": 45.16191 
}

start_date= '2019-01-01' 
end_date= '2019-07-23'

max_results= 300
'''
sat-search search --bbox 38.87468 45.14835 39.17818 44.94265 -c "landsat-8-l1" --datetime "2019-01-01/2019-07-23" --print-md

'''  
'''
from satsearch import search
api.login(login,pswd)
responce = api.download(dataset,node,entityid)'''

'''
import mechanize

br = mechanize.Browser()
#br.set_all_readonly(False)    # allow everything to be written to
br.set_handle_robots(False)   # ignore robots
#br.set_handle_refresh(False)  # can sometimes hang without this

br.addheaders = [('User-agent', 'Chrome')]
url = "https://ers.cr.usgs.gov/login/"
response = br.open(url)
for form in br.forms():
	print(form.name)
br.form = list(br.forms())[0]
for control in br.form.controls:
	print (control)

br.form.find_control("username").value = login
br.form.find_control("password").value = pswd

response = br.submit()


'''
import requests
import json
from pprint import pprint
from landsatxplore.earthexplorer import EarthExplorer


class earthexpl_api_handler:
	def __init__(self):
		self.domain = "https://earthexplorer.usgs.gov/inventory/json/v/1.4.0/<request_code>?jsonRequest=<json_request_content>"
		self.datasets_filename = "datasets.txt"
		self.last_responce = None

	def get_responce(self,request_code,request_content):
		json_request_content = json.dumps(request_content)
		request = self.domain.replace("<request_code>",str(request_code)).replace("<json_request_content>",str(json_request_content))
		return requests.get(request).json()

	def login(self,username,password):
		request_code = "login"
		request_content = {
    		"username": username,
    		"password": password,
    		"catalogId": "EE"
		}
		response = self.get_responce(request_code,request_content)
		self.token = response['data']
		if self.token is not None:
			print("Login successful")
			self.login_succ = True
		else:
			print("ERROR", response['error'],sep='\n')
			self.login_succ = False

	def scene_search(self,ll,ur,startDate, endDate):
		if self.login_succ :
			request_code = "search"
			request_content = {
				"datasetName": "LANDSAT_8_C1",
		        "spatialFilter": {
		            "filterType": "mbr",
		            "lowerLeft": ll,
		            "upperRight": ur
		        },
	       		"temporalFilter": {
	            	"startDate": startDate,
	            	"endDate": endDate,
	        	},
				"maxResults": max_results,
				"apiKey": self.token
			}
			print("Start to search scenses:")
			print("lowerLeft coords", ll)
			print("upperRight coords", ur)
			response = self.get_responce(request_code,request_content)
			self.last_responce = response

	def dataset_search(self):
		if self.login_succ:
			request_code = "datasets"
			request_content = {
				"apiKey" : self.token
			}
			response = self.get_responce(request_code,request_content)
			pprint(response, open(self.datasets_filename,"w"))

	def get_latest_displayID(self,count=5):
		if self.last_responce is not None and self.login_succ:
			record_count = int(self.last_responce['data']['lastRecord'])
			result = []
			for i in range(min(count,record_count)):
				curr_record = self.last_responce['data']['results'][-1-i]
				result.append({"data" : curr_record['startTime'],
							   "displayId": curr_record['displayId'] })
			return result
		return []




def main():
	api = earthexpl_api_handler()
	api.login(username,pswd)
	api.scene_search(ll,ur,start_date,end_date)
	print("Searching result")
	latest_id = api.get_latest_displayID()
	for scene in latest_id:
		print(scene) 

	print("Try to dowload latest scence")

	ee = EarthExplorer(username,pswd)
	ee.download(scene_id=latest_id[0]['displayId'], output_dir=output_dir)
	ee.logout()


if __name__ == '__main__':
	main()