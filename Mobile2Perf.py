#!/usr/bin/python

# Mobile2Performa.py
###
# Converts Accu-Chek Mobile data into Performa XML format
# Input: filename containing AC Mobile data
# Output: on stdout, generates a "fake" Performa XML file

import sys

from datetime import *

import csv
import math

device_sn = 'UI12345678'

def squarelist(the_list):
	return [element**2 for element in the_list]

def main(args):
	print args
	print len(args)
	try:
		(fn, start_date, stop_date) = check_args(args)
	except TypeError:
		return 1

	(today_str, recent_str, now_str, time_recent_str) = init_dates(date.today(), datetime.now())
	prop = generate_xml_prop()

	output = convert_data(today_str, recent_str, now_str, time_recent_str, fn, start_date, stop_date)
	print prop
	for d in output:
		print d
	return

def check_args(args):
	if (len(args) != 3):
		print "Usage: Mobile2Perf.py <CSV_file_name> <start_date> <stop_date>"
		return


	start_date_str = args[1]
	stop_date_str = args[2]
	fn = args[0]

	try:
		start_date = datetime.strptime(start_date_str, "%d/%m/%Y")
		stop_date = datetime.strptime(stop_date_str, "%d/%m/%Y")
		open(fn)
	except ValueError:
		print "Please provide dates with dd/mm/yyyy format"
		return
	except IOError:
		print "Please provide a valid file name, got", fn
		return

	if start_date > stop_date:
		c = stop_date
		stop_date = start_date
		start_date = c

	return (fn, start_date, stop_date)

def init_dates(when_day, when_time):
	today = when_day
	today_str = when_day.isoformat()
	recent_str = today_str
	
	now = when_time
	now_str = when_time.strftime("%H:%M")
	time_recent_str = now_str

	return (today_str, recent_str, now_str, time_recent_str)


def generate_xml_prop():
	xml_prop = '<?xml version="1.0" encoding="ISO-8859-1" ?>\n'
	xml_prop += '<?xml-stylesheet type="text/xsl" href="ACSPIXMT.xsl" ?>\n'
	xml_prop += '\n'
	xml_prop += '<!DOCTYPE IMPORT [\n'
	xml_prop += '  <!ELEMENT IMPORT (ACSPIX, DEVICE+, RECENTREC, BGDATA, STATISTIC, CHECK)>\n'
	xml_prop += '  <!ELEMENT ACSPIX     EMPTY>\n'
	xml_prop += '    <!ATTLIST ACSPIX\n'
	xml_prop += '      Type     CDATA #REQUIRED\n'
	xml_prop += '      SN       CDATA #REQUIRED\n'
	xml_prop += '      Ver      CDATA #REQUIRED\n'
	xml_prop += '    >\n'
	xml_prop += '  <!ELEMENT DEVICE    EMPTY>\n'
	xml_prop += '    <!ATTLIST DEVICE\n'
	xml_prop += '      Name     CDATA #REQUIRED\n'
	xml_prop += '      SN       CDATA #REQUIRED\n'
	xml_prop += '      Dt       CDATA #REQUIRED\n'
	xml_prop += '      Tm       CDATA #REQUIRED\n'
	xml_prop += '      BGUnit   CDATA #REQUIRED\n'
	xml_prop += '      TrgLo    CDATA #IMPLIED\n'
	xml_prop += '      TrgHi    CDATA #IMPLIED\n'
	xml_prop += '      Hypo     CDATA #IMPLIED\n'
	xml_prop += '      TmBins   CDATA #IMPLIED\n'
	xml_prop += '    >\n'
	xml_prop += '  <!ELEMENT RECENTREC    EMPTY>\n'
	xml_prop += '    <!ATTLIST RECENTREC\n'
	xml_prop += '      Dt       CDATA #REQUIRED\n'
	xml_prop += '      Tm       CDATA #REQUIRED\n'
	xml_prop += '    >\n'
	xml_prop += '  <!ELEMENT BG       (#PCDATA)>\n'
	xml_prop += '    <!ATTLIST BG\n'
	xml_prop += '      Val      CDATA #REQUIRED\n'
	xml_prop += '      Dt       CDATA #IMPLIED\n'
	xml_prop += '      Tm       CDATA #IMPLIED\n'
	xml_prop += '      Flg      CDATA #IMPLIED\n'
	xml_prop += '      Ctrl     CDATA #IMPLIED\n'
	xml_prop += '      Carb     CDATA #IMPLIED\n'
	xml_prop += '      Ins1     CDATA #IMPLIED\n'
	xml_prop += '      Ins2     CDATA #IMPLIED\n'
	xml_prop += '      Ins3     CDATA #IMPLIED\n'
	xml_prop += '      Evt      CDATA #IMPLIED\n'
	xml_prop += '      D        CDATA #IMPLIED\n'
	xml_prop += '    >\n'
	xml_prop += '  <!ELEMENT BGDATA   (BG*)>\n'
	xml_prop += '\n'
	xml_prop += '  <!ELEMENT ST_TIMERANGE (#PCDATA)>\n'
	xml_prop += '    <!ATTLIST ST_TIMERANGE\n'
	xml_prop += '      Weeks    CDATA #REQUIRED\n'
	xml_prop += '      Dt       CDATA #REQUIRED\n'
	xml_prop += '    >\n'
	xml_prop += '\n'
	xml_prop += '  <!ELEMENT ST_EVALRESULTS (#PCDATA)>\n'
	xml_prop += '    <!ATTLIST ST_EVALRESULTS\n'
	xml_prop += '      Val      CDATA #REQUIRED\n'
	xml_prop += '    >\n'
	xml_prop += '\n'
	xml_prop += '  <!ELEMENT ST_TSTFREQ1 (#PCDATA)>\n'
	xml_prop += '    <!ATTLIST ST_TSTFREQ1\n'
	xml_prop += '      Val      CDATA #REQUIRED\n'
	xml_prop += '    >\n'
	xml_prop += '\n'
	xml_prop += '  <!ELEMENT ST_TSTFREQ2 (#PCDATA)>\n'
	xml_prop += '    <!ATTLIST ST_TSTFREQ2\n'
	xml_prop += '      Val      CDATA #REQUIRED\n'
	xml_prop += '    >\n'
	xml_prop += '\n'
	xml_prop += '  <!ELEMENT ST_MBG (#PCDATA)>\n'
	xml_prop += '    <!ATTLIST ST_MBG\n'
	xml_prop += '      Val      CDATA #REQUIRED\n'
	xml_prop += '    >\n'
	xml_prop += '\n'
	xml_prop += '  <!ELEMENT ST_SD (#PCDATA)>\n'
	xml_prop += '    <!ATTLIST ST_SD\n'
	xml_prop += '      Val      CDATA #REQUIRED\n'
	xml_prop += '    >\n'
	xml_prop += '\n'
	xml_prop += '  <!ELEMENT ST_HBGI (#PCDATA)>\n'
	xml_prop += '    <!ATTLIST ST_HBGI\n'
	xml_prop += '      Val      CDATA #REQUIRED\n'
	xml_prop += '    >\n'
	xml_prop += '\n'
	xml_prop += '  <!ELEMENT ST_LBGI (#PCDATA)>\n'
	xml_prop += '    <!ATTLIST ST_LBGI\n'
	xml_prop += '      Val      CDATA #REQUIRED\n'
	xml_prop += '    >\n'
	xml_prop += '\n'
	xml_prop += '  <!ELEMENT ST_ADRR (#PCDATA)>\n'
	xml_prop += '    <!ATTLIST ST_ADRR\n'
	xml_prop += '      Val      CDATA #REQUIRED\n'
	xml_prop += '    >\n'
	xml_prop += '\n'
	xml_prop += '  <!ELEMENT STATISTIC (ST_TIMERANGE, ST_EVALRESULTS, ST_TSTFREQ1, ST_TSTFREQ2, ST_MBG, ST_SD, ST_HBGI, ST_LBGI, (ST_ADRR)*)>\n'
	xml_prop += '\n'
	xml_prop += '  <!ELEMENT CHECK    EMPTY>\n'
	xml_prop += '    <!ATTLIST CHECK\n'
	xml_prop += '      CRC      CDATA #REQUIRED\n'
	xml_prop += '    >\n'
	xml_prop += ']>\n'
	xml_prop += '\n'

	return xml_prop

def convert_data(today_str, recent_str, now_str, time_recent_str, fn, start_date, stop_date):
	trunk = '<BGDATA>\n'

	i=0
	bg_data = []
	with open(fn, 'rb') as f:
		try:
			reader = csv.reader(f, delimiter=';')
			for i in range(3):
				reader.next()

			for row in reader:

				try:
					row_date = datetime.strptime(row[0], "%d.%m.%Y")

				except ValueError:
					continue

				if row_date < start_date:
					continue 

				if row_date > stop_date:
					continue 

				trunk += '<BG Val=\"'
				trunk += row[2]
				trunk += '\" Dt=\"'
				trunk += row_date.strftime("%Y-%m-%d")
				trunk += '\" Tm=\"'
				trunk += row[1]
				trunk += '\" D=\"1\"/>\n'
				bg_data.append(int(row[2]))

				if row[3] == "mg/dl":
					unit = 'mg/dL'
				else:
					unit = 'mmol/L'

				# Control test => avoid
				if row[9] == 'X':
					continue

				# Temp warning => avoid
				if row[4] == 'X':
					continue

		finally:
			f.close()


	try:
		avg = sum(bg_data) / len(bg_data)
		var = sum(squarelist(bg_data)) / len(bg_data) - ( avg ** 2 )
	except ZeroDivisionError:
		print "No data found between", start_date.strftime("%d/%m/%Y"), "and", stop_date.strftime("%d/%m/%Y")
		return 1


	header = '<IMPORT>\n<ACSPIX Type=\"2106\" SN=\"'
	header += device_sn
	header += '\" Ver=\"3.01.03\"/>\n<DEVICE  Name=\"Performa\" SN=\"01226392\" Dt=\"'
	header += today_str
	header += '\" Tm=\"'
	header += now_str
	header += '\" BGUnit=\"'
	header += unit # mg/dL
	header += '\"/>\n<RECENTREC Dt=\"'
	header += recent_str
	header += '\" Tm=\"'
	header += time_recent_str
	header += '\"/>\n\n'


	footer = '</BGDATA>\n'
	footer += '<STATISTIC>\n'
	footer += '<ST_TIMERANGE Weeks=\"12\" Dt=\"'
	footer += recent_str
	footer += '\"/>\n'
	footer += '<ST_EVALRESULTS Val=\"'
	footer += str(len(bg_data))
	footer += '\"/>\n'
	footer += '<ST_TSTFREQ1 Val=\"\"/>\n'
	footer += '<ST_TSTFREQ2 Val=\"\"/>\n'
	footer += '<ST_MBG Val=\"'
	footer += str( avg )
	footer += '\"/>\n'
	footer += '<ST_SD Val=\"'
	footer += str(  math.ceil( math.sqrt(var) )  )
	footer += '\"/>\n'
	footer += '<ST_HBGI Val=\"\"/>\n'
	footer += '<ST_LBGI Val=\"\"/>\n'
	footer += '</STATISTIC>\n'
	footer += '<CHECK CRC=\"'
	#635B ...
	footer += '\"/>\n'
	footer += '</IMPORT>\n'
	
	return (header, trunk, footer)

if __name__ == '__main__':
	main(sys.argv)
