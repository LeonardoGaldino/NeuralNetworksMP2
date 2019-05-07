'''
	Dupla: 
		1. Leonardo Chaves Galdino de Moraes (lcgm)
		2. Rafael Luiz da Silva Machado Albuquerque (rlsma)
'''

from os import listdir
from sys import argv

from sompy.sompy import SOM, SOMFactory
from sompy.neighborhood import BubbleNeighborhood, GaussianNeighborhood
from sompy.normalization import VarianceNormalizator
from sompy.visualization.hitmap import HitMapView
from sompy.visualization.umatrix import UMatrixView
from sompy.visualization.bmuhits import BmuHitsView
from sompy.visualization.mapview import View2D

import csv
import numpy as np
import functools
import gmplot
from bs4 import BeautifulSoup



GLOBALS = {
	# Google Maps API key
	'GM_KEY': '<INSERT_YOUR_API_KEY>',
}

# Comparison function to consume files in ascending order (year-month)
def files_sort_cmp(a,b):
	a = a.split('.')[0]
	b = b.split('.')[0]
	a_year = int(a.split(',')[-1])
	a_month = int(a.split(',')[0].split('-')[-1])
	b_year = int(b.split(',')[-1])
	b_month = int(b.split(',')[0].split('-')[-1])
	if a_year < b_year:
		return -1
	elif a_year > b_year:
		return 1
	if a_month < b_month:
		return -1
	elif a_month > b_month:
		return 1
	return 0

# Sort function to consume files in ascending order (year-month)
def sort_files(files_name):
	files_name.sort(files_sort_cmp)
	return files_name

def get_fields(row):
	''' 
		lat: 1
		lng: 2
		temp avg: 4
		max temp: 7
		min temp: 9
		precip: 14
	'''
	try:
		return [
			float(row[1]), float(row[2]), float(row[4]), 
			float(row[7]), float(row[9]), float(row[14])
			]
	except:
		return []


def load_data():
	data = []
	data_files_name = sort_files(listdir('data'))
	prefix = 'data/'
	for data_file_name in data_files_name:
		with open(prefix+data_file_name, 'rb') as data_file:
			blank_lines_count = 0
			data_started = False
			parsed_csv = csv.reader(data_file, delimiter=',')
			for row in parsed_csv:
				if data_started:
					temp = get_fields(row)
					if len(temp) != 0:
						data.append(temp)
				elif len(row) == 0:
					blank_lines_count += 1
				elif blank_lines_count == 2:
					data_started = True

	return data

def generate_map(out_file_name, pins, pin_prefix):
	gmap = gmplot.GoogleMapPlotter(54.2, -124.875224, 6)

	j = 0
	for pin in pins:
		pin_name = ("%s %s" % (pin_prefix, str(j)))
		gmap.marker(pin[0], pin[1],'red', title=pin_name)
		j += 1

	gmap.draw(out_file_name)

	def insertapikey(fname, apikey):
		"""put the google api key in a html file"""
		def putkey(htmltxt, apikey, apistring=None):
		    """put the apikey in the htmltxt and return soup"""
		    if not apistring:
		        apistring = "https://maps.googleapis.com/maps/api/js?key=%s&callback=initMap"
		    soup = BeautifulSoup(htmltxt, 'html.parser')
		    body = soup.body
		    src = apistring % (apikey, )
		    tscript = soup.new_tag("script", src=src, async="defer")
		    body.insert(-1, tscript)
		    return soup
		htmltxt = open(fname, 'r').read()
		soup = putkey(htmltxt, apikey)
		newtxt = soup.prettify()
		open(fname, 'w').write(newtxt)

	insertapikey(out_file_name, GLOBALS['GM_KEY'])

def main(grid_layout, neighborhood, grid_size, init_method):
	data = np.array(load_data())
	print('Dataset has ' + str(len(data)) + ' rows.')
	
	stations_latlng = np.unique(data[:, 0:2], axis=0)
	print(len(stations_latlng))

	generate_map('stations.html', stations_latlng, 'Station')

	names = [
			'Latitude', 
			'Longitude', 
			'Monthly Median temperature',
			'Monthly Max. temperature',
			'Monthly Min. temperature',
			'Monthly total precipitation'
			]
	if(grid_size == (-1, -1)):
		model = SOMFactory().build(
						data, normalization = 'var',
					 	initialization=init_method, lattice=grid_layout, 
					 	neighborhood=neighborhood, component_names=names
					 )
	else:
		model = SOMFactory().build(
					data, mapsize=grid_size, normalization = 'var',
				 	initialization=init_method, lattice=grid_layout, 
				 	neighborhood=neighborhood, component_names=names
				 )

	model.train(
				n_job=1,
	          	shared_memory=False,
	    	  	verbose='info',
	          	train_len_factor=1
	          	)

	max_k = 20 # for k-means in elbow method
	_, clusters, _ = model.cluster(max_k)

	centroids_lat_lng = [[centroid[0], centroid[1]] for centroid in clusters.cluster_centers_]

	generate_map('centroids.html', centroids_lat_lng, 'Centroid')

	comp_plane_hm = View2D(20, 20, 'Component plane heatmap')
	comp_plane_hm.show(som=model, col_sz=4, desnormalize=True)

	umat = UMatrixView(20, 20, 'U-Matrix')
	umat.show(som=model)

	clust_res = HitMapView(20, 20, 'Clustering result')
	clust_res.show(som=model)

if __name__ == '__main__':
	if len(argv) != 6:
		print('You shoud provide 5 parameters: grid-layout, neighborhood-func, grid-rows, grid-cols, initialization-method')
	else:
		main(argv[1], argv[2], (int(argv[3]), int(argv[4])), argv[5])