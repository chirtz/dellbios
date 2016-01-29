#!/usr/bin/env python
import os
import re
import sys
import urllib3
import yaml
import json
import datetime
from BeautifulSoup import BeautifulSoup

'''
Example bios_sconfig.yaml:

---
folder_map:
 optiplex:  OptiPlex
 latitude:  Latitude
 precision: Precision

file_conversion:
 -:
 _:
 EXE": exe
 OptiPlex:
 AIO: A

system_ids:
 - optiplex-980
 - latitude-e7440-ultrabook
'''

BIOS_BASE = "downloads.dell.com"
BIOS_URL = "/published/pages/%s.html"
DATE_FORMAT = "%d.%m.%Y"
BIOS_URL_REGEX = re.compile(r"^/(.*?)\.(EXE|exe)")
OUTPUT_JSON = True

def getBios(http_connection, system_id):
	response = http_connection.request("GET", BIOS_URL % system_id)
	soup = BeautifulSoup(response.data)
	links = soup.find("div", {"id": "Drivers-Category.BI-Type.BIOS"}).findAll("a", href=BIOS_URL_REGEX)
	bi = []
	for l in links:
		href = l["href"]
		bi.append((href[-7:-4], href, convert_filename(href[href.rfind("/")+1:])))		
	return bi
	
def convert_filename(fi):
	for k in file_map:
		val = file_map[k]
		if val is None:
			val = ""
		fi = re.sub(k, val, fi)
	return fi

def folder_for_sysid(folder_map, sysid):
	for m in folder_map:
		if sysid.startswith(m):
			return folder_map[m]
	return None

def fail(msg):
	print("Error: %s" % msg)
	sys.exit(1)

def output_json(folder, results):
	with open("%s/results.json" % folder, "w") as result_file:
		result_file.write(json.dumps(results))
		

def update(target_dir):
	results = []
	if target_dir.endswith("/"):
		target_dir = target_dir[:-1]
	num_sys_ids = len(system_ids)
	http = urllib3.HTTPConnectionPool(BIOS_BASE, timeout=urllib3.Timeout(read=2))
	
	for sysid in system_ids:
		try:
			b = getBios(http, sysid)[0]
		except:
			print("Error at %s" % sysid)
			continue
		folder = folder_for_sysid(folder_map, sysid)
		if folder is not None:
			file_name = "%s/%s/%s" % (target_dir, folder, b[2])
			fn = "%s/%s" % (folder, b[2])
			if not (os.path.exists(os.path.dirname(file_name))):
				os.mkdir(os.path.dirname(file_name))
			res = {}
			res["system_id"] = sysid
			res["current_bios"] = b[0]
			if os.path.isfile(file_name):
				last_changed = log[sysid] if sysid in log else ""
			else:
				bios_file = http.request("GET", b[1]).data
				output = open(file_name,'wb')
				output.write(bios_file)
				output.close()
				last_changed = datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")
				log[sysid] = last_changed 
			res["last_changed"] = last_changed
			res["file_name"] = fn
			results.append(res)
		else:
			fail("Folder for sys id %s does not exist in mapping" % sysid)

	

	results = sorted(results, key=lambda tup: tup["system_id"])
	if OUTPUT_JSON:
		output_json(target_dir, results)
	else:
		for line in results:
			print "%s, Version: %s, Status: %s" % (line["system_id"], line["current_bios"], line["last_changed"])



if __name__ == "__main__":
	if len(sys.argv) != 2:
		fail("wrong number of arguments. provide an output path")
	try:
		d = yaml.load(open("biosconfig.yaml", "r").read())
		folder_map = d["folder_map"]
		system_ids = d["system_ids"]
		file_map = d["file_conversion"]
	except:
		fail("biosconfig.yaml is missing or corrupt.")
	def load_log(): return yaml.load(open("bioslog.yaml", "rw").read())
	try:
		log = load_log()
	except:
		log = {}

	arg = sys.argv[1].strip()
	update(arg)
	with open("bioslog.yaml", "w") as logfile:
		logfile.write(yaml.dump(log))

