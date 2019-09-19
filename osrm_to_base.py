# кодирование строки в base64 - https://tech.yandex.ru/maps/doc/archive/jsapi/1.x/dg/tasks/how-to-add-polyline-docpage/#encoding-polyline-points


import osrm #https://github.com/ustroetz/python-osrm
from osrm import Point, simple_route
import csv
import operator
import json
import time

MyConfig = osrm.RequestConfig("localhost:9999/v1/biking", basic_auth=("user", "pass"))
MyConfig.profile = "biking"
osrm.RequestConfig.host = "router.project-osrm.org"

#запись данных в массив stations из staions_spb.csv 
index = 0
stations = {}
new_stations = []
with open('stations_spb.csv', 'r', encoding="utf8") as stations_spb:
	reader = csv.reader(stations_spb, dialect=csv.excel_tab)
	for row in reader:
		if index > 0:
			#print(stations[index])
			new_stations.append(row)
		index += 1

new_stations.sort()
print(new_stations)

#вывод значения hint по 2 точкам
i = 0
j = 0
result_routes_list = {}
routes_list = {}
to_station_list = {}
station_list = {}
for row in new_stations:
	for row in new_stations:
		if j > i:
			
			p1 = Point(latitude=float(new_stations[i][2]), longitude=float(new_stations[i][3]))
			p2 = Point(latitude=float(new_stations[j][2]), longitude=float(new_stations[j][3]))
			while True:
				try:
					result = osrm.simple_route(p1, p2, geometry='geojson')
					break
				except:
					time.sleep(0.5)
					continue
				
			# time.sleep(0.3)
			route = []
			route_first = result['routes'][0]['geometry']['coordinates']
			for elemet in route_first:
				point = [elemet[1], elemet[0]]
				route.append(point)

			# print(route)
			#### перекодирование
			k = 0
			sum_string = "" # в ней хранятся биты от всех точек
			result_string = "" # хранится перекодированная строка
			string = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_="
			excess = ""

			for element in route:
				if k >= 1:
					multi1 = int(route[k][0]*1000000 - route[k-1][0]*1000000)
					multi2 = int(route[k][1]*1000000 - route[k-1][1]*1000000)
				else:
					multi1 = int(route[k][0]*1000000)
					multi2 = int(route[k][1]*1000000)
				if multi1 < 0:
					bi1 = format(multi1, 'b')[1:].zfill(32)
					bi1 = bi1.replace("0","2").replace("1","0").replace("2","1")
					bi1 = int(bi1, 2)
					bi1 += 1
					bi1 = format(bi1, 'b')
				else:
					bi1 = format(multi1, 'b').zfill(32)
				if multi2 < 0:
					bi2 = format(multi2, 'b')[1:].zfill(32)
					bi2 = bi2.replace("0","2").replace("1","0").replace("2","1")
					bi2 = int(bi2, 2)
					bi2 += 1
					bi2 = format(bi2, 'b')
				else:
					bi2 = format(multi2, 'b').zfill(32)
				bi1 = bi1[24:] + bi1[16:24] + bi1[8:16] + bi1[0:8]
				bi2 = bi2[24:] + bi2[16:24] + bi2[8:16] + bi2[0:8]
				sum_string += bi1
				sum_string += bi2
				k += 1
			
			# перекодирование по 6 бит 
			while True:
				if len(sum_string) == 2:
					sum_string += '0000'
					dec = int(sum_string[:6], 2)
					result_string += string[dec]
					result_string += "=="
					break
				elif len(sum_string) == 4:
					sum_string += '00'
					dec = int(sum_string[:6], 2)
					result_string += string[dec]
					result_string += "="
					break
				elif len(sum_string) == 0:
					break
				else:
					dec = int(sum_string[:6], 2)
					result_string += string[dec]
					sum_string = sum_string[6:]
			print('route от '+new_stations[i][0]+' до '+new_stations[j][0]+': '+ str(result_string))
			station_list = {new_stations[j][0]:str(result_string)}
			to_station_list.update(station_list)
		j += 1
	routes_list[new_stations[i][0]] = to_station_list
	to_station_list = {}
	result_routes_list.update(routes_list)
	j = 0	
	i += 1
with open ('routes.json', 'w') as f:
	json.dump(result_routes_list, f)