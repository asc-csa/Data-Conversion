from urllib.parse import quote
from ftplib import FTP
import csv
import pandas as pd
import numpy as np
import os

'''
This python script was written to summarize the OSIRIS dataset.
It summarizes each number density file for the 5 data collections and pairs each number density point to the respective time, altitude, longitude and latitude.
Some manual changes in this file need to be done to switch between O3, NO2, BrO, etc.
Specifically, in line 50, 63, 70, 77 and 109.
'''

FTP_HOST = "data.asc-csa.gc.ca"
FTP_USER = "anonymous"
FTP_PASS = ""

base = '/users/OpenData_DonneesOuvertes/pub/OSIRIS/Data_format CSV/Level2/daily/'

class Point():
    def __init__(self):
        self.time = 0
        self.alt = 0
        self.lat = 0
        self.lon = 0
        self.ndens = 0
        self.ndens2 = 0

class Data():
    def __init__(self):
        self.pointlist = []


ftp = FTP(FTP_HOST)

ftp.login()
ftp.cwd(base)

allData = Data()

monthlist = ftp.nlst()

for month in monthlist:
    # Here we iterate through every month's data
    ftp.cwd(base+month)
    #For progression purposes, we print the month we are going through
    print("Month: "+month)
    for name in ftp.nlst():
        # Here we check each folder and if it is the correct type of folder
        if name.split("_")[1]=="L2-OH-Limb":
            try:
                #Here we print the day:
                print("Day: "+name.split("_")[3].split("m")[1])
                #Once we have the correct folder, we download all the necessary geolocation data
                ftp.cwd(base+month+"/"+name+"/Geolocation Fields/")
                ftp.retrbinary("RETR Time.csv", open("temp/Time.csv",'wb').write)
                ftp.retrbinary("RETR Altitude.csv", open("temp/Altitude.csv",'wb').write)
                ftp.retrbinary("RETR Latitude.csv", open("temp/Latitude.csv",'wb').write)
                ftp.retrbinary("RETR Longitude.csv", open("temp/Longitude.csv",'wb').write)

                #We then download the actual data
                ftp.cwd(base+month+"/"+name+"/Data Fields/")
                ftp.retrbinary("RETR OHPrompt.csv", open("temp/OHPrompt.csv",'wb').write)
                ftp.retrbinary("RETR OHResonance.csv", open("temp/OHResonance.csv",'wb').write)

                #We save everything into arrays
                time = np.genfromtxt('temp/Time.csv', delimiter=',')
                alt = np.genfromtxt('temp/Altitude.csv', delimiter=',')
                lat = np.genfromtxt('temp/Latitude.csv', delimiter=',')
                lon = np.genfromtxt('temp/Longitude.csv', delimiter=',')
                nbrdensity = np.genfromtxt('temp/OHPrompt.csv', delimiter=',')
                nbrdensity2 = np.genfromtxt('temp/OHResonance.csv', delimiter=',')

                #We now do not need the downloaded files, so we delete all of them
                os.remove("temp/Time.csv")
                os.remove("temp/Altitude.csv")
                os.remove("temp/Longitude.csv")
                os.remove("temp/Latitude.csv")
                os.remove("temp/OHPrompt.csv")
                os.remove("temp/OHResonance.csv")

                #We pair all the data points with the actual time, latitude, longitude, altitude and insert it in a Point object
                try:
                    for i in range(0,len(nbrdensity)):
                        for j in range(0,len(nbrdensity[i])):
                            point = Point()
                            point.alt = alt[j]
                            point.lat = lat[i]
                            point.lon = lon[i]
                            point.time = time[i]
                            point.ndens = nbrdensity[i][j]
                            point.ndens2 = nbrdensity2[i][j]

                            #We finish by inserting this point in our Data object
                            allData.pointlist.append(point)
                except TypeError:
                    for i in range(0, len(nbrdensity)):
                        point = Point()
                        point.alt = alt[i]
                        point.lat = lat
                        point.lon = lon
                        point.time = time
                        point.ndens = nbrdensity[i]
                        point.ndens2 = nbrdensity2[i]
                        allData.pointlist.append(point)
            except:
                print("Error - folder does not exist, skipped.")
ftp.quit()

#Now that we have all the necessary data stored in our Data object, we write it to a csv:
print("Writing to file... This may take a while")
with open('summary.csv','w',newline='') as csvfile:
    write = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
    write.writerow(['Time (TAI 1993)', ' Altitude (km)', 'Latitude (degree)', 'Longitude (degree)', 'OH Prompt (cm^-3)', 'OH Resonance (cm^-3)'])
    for pt in allData.pointlist:
        write.writerow([pt.time, pt.alt, pt.lat, pt.lon, pt.ndens, pt.ndens2])
print("Done!")
