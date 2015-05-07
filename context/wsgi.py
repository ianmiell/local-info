import bs4
import urllib2
import time


t_struct = time.localtime()
global_year = t_struct[0]
global_mon = t_struct[1]
global_day = t_struct[2]
global_hour = t_struct[3]
global_min = t_struct[4]
global_sec = t_struct[5]
global_wday = t_struct[6]
global_yday = t_struct[7]
global_isdst = t_struct[7]

def application(environ, start_response):
	status = '200 OK'
	output = ''
	data = []
	print data

	response_headers = [('Content-type', 'text/plain'),
	                    ('Content-Length', str(len(output)))]


	start_response(status, response_headers)

	get_buses(data)
	# Do this after the web waits
	time = int(time.time())
	return [output]

def get_buses(data):
	for url in ('http://m.countdown.tfl.gov.uk/arrivals/73906',):
		req = urllib2.Request(url)
		response = urllib2.urlopen(req)
		the_page = response.read()
		soup = bs4.BeautifulSoup(the_page)
		table = soup.find_all('table','results')
		for row in table:
			for tr in row.find_all('tr'):
				direction = tr.find('td','resDir')
				due = tr.find('td','resDue')
				route = tr.find('td','resRoute')
				if direction:
					direction = direction.string.strip()
					if due == 'due':
						due       = 30
					else:
						due       = due.string.strip().split()[0]
					route     = route.string.strip()
					t = int(time.time() + (int(due) * 60))
					data.append({'type':'BUS','route':route,'destination':direction,'leaving':str(t),'arriving':'','status':''})

def get_trains(data):
	for url in ('http://ojp.nationalrail.co.uk/service/ldbboard/dep/NDL',):
		req = urllib2.Request(url)
		response = urllib2.urlopen(req)
		the_page = response.read()
		soup = bs4.BeautifulSoup(the_page)
		div = soup.find_all('div','tbl-cont')
		for tr in div:
			for tr in tr.find_all('tr'):
				count = 1
				route = ''
				destination = ''
				status = ''
				t = ''
				arriving = ''
				for td in tr.find_all('td'):
					if td.string:
						s = td.string.strip()
						if count == 1:
							h = int(s.split(':')[0])
							m = int(s.split(':')[1])
							t = int(time.mktime((global_year,global_mon,global_day,h,m,global_sec,global_wday,global_yday,global_isdst)))
						elif count == 2:
							route = s
							destination = s
						elif count == 3:
							status = s
					else:
						s = str(td)
					count += 1
				if t != '':
					data.append({'type':'TRAIN','route':route,'destination':destination,'leaving':t,'arriving':'','status':status})

def print_data(data):
	for item in data:
		row = ''
		for field in item:
			if field == 'leaving':
				row += 'at: ' + time.ctime(float(item[field])) + ','
			else:
				row += field + ': ' + item[field] + ', '
		print row

def order_data(data,field='leaving'):
	times = []
	for item in data:
		times.append(item[field])
	times.sort()
	# remove dupes
	times = set(times)
	newdata = []
	# go through times, then go through data, if field matches value in times, append data item
	for t in times:
		for item in data:
			if item[field] == t:
				newdata.append(item)
	data = newdata

if __name__ == "__main__":
	data = []
	get_buses(data)
	get_trains(data)
	order_data(data)
	print_data(data)

