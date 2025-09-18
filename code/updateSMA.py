import numpy
import subprocess
import shlex
from bs4 import BeautifulSoup
import requests


tmpfile = "sma.tmp"
outfile = "SMA_calibrators.cat"
url = "http://sma1.sma.hawaii.edu/callist/callist.html"

response = requests.get(url)

html = BeautifulSoup(response.text, 'html.parser')

flux_html = html.find_all('table', class_="cals")

trs_parser = BeautifulSoup(flux_html.__str__(), 'html.parser')

trs = trs_parser.find_all('tr')

source_dic = {}

for itrs in trs:
    tds = itrs.find_all('td')
    if len (tds) == 0:
        continue
    common_o_flux = tds[0].text.strip()
    jname = tds[1].text.strip()
    
    if common_o_flux.find("3c274") >= 0 or jname.find("3c274")>=0:
        print ("Found source 3c274 in the list. Removing it")
        continue
    
    if common_o_flux == "--":
        sname = jname
        key = jname
        flux = tds[-2].text
        ra = tds[2].text.strip()
        dec = tds[3].text.strip()
        sflux, eflux = flux.split("±")
        source_dic[key] = {'name':sname, 'ra':ra, 'dec':dec, 'f1mm':float(sflux), 'e1mm':float(eflux)}
    elif common_o_flux.find("850") > -1:
        flux = tds[-1].text
        sflux, eflux = flux.split("±")
        source_dic[key]["f850um"] = float(sflux)
        source_dic[key]["e850um"] = float(eflux)
    else:
        sname = common_o_flux
        key = common_o_flux
        flux = tds[-2].text
        sflux, eflux = flux.split("±")
        ra = tds[2].text.strip()
        dec = tds[3].text.strip()
        source_dic[key] = {'name':sname, 'ra':ra, 'dec':dec, 'f1mm':float(sflux), 'e1mm':float(eflux)}

vfac = numpy.log(1.1/0.85)
vfac2 = (3.0/1.1)

for ikey in source_dic:
    if not "f850um" in source_dic[ikey].keys():
        alpha = 0.
        source_dic[ikey]['f3mm'] = source_dic[ikey]['f1mm']
        source_dic[ikey]['f850um'] = 0
    else:
        a = numpy.log(source_dic[ikey]['f1mm']/source_dic[ikey]['f850um'])/vfac
        source_dic[ikey]["a"] = a
        if a > 1:
            a=1
        source_dic[ikey]['f3mm'] = source_dic[ikey]['f1mm']*vfac2**a

    
ofile = open(outfile, "wt")
header = "NAME\tRA\tDEC\tRA_REF\tDEC_REF\tEPOCH\tFLUX3mm\tFLUX1mm\tFLUX850um\tRaProperMotionCor\tDecProperMotionCor\tVlsr\n"
lineTemp = "{name}\t{ra}\t{dec}\t{ra}\t{dec}\t2000\t{f3mm:.2f}\t{f1mm}\t{f850um}\t0\t0\t0\n"
ofile.write(header)
for ikey in source_dic:
    ofile.write(lineTemp.format(**source_dic[ikey]))
ofile.close()
    

