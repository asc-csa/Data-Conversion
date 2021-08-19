from urllib.parse import quote
from ftplib import FTP, error_perm
import csv
import pandas as pd
import numpy as np
import os
from datetime import datetime

'''
MAKE SURE TO ENTIRELY READ THIS BEFORE RUNNING.

This dataset was too difficult to generalize entirely, so each file needs to be generated manually.
For each filter (O1S, O1D, O+, etc.), there can be at most 2 types (FD or FO, and CD). The created file is a summary of one type for one filter.
Ex O1S has both types FD and CD. O1S will have two summary files: O1S_FD and O1S_CD.
Filters contains at most three of 'Wind', 'Temperature' and 'VolumeEmissionRate'. There are data fields.
Based on wanted type and which data fields are present, you must edit the parameters section below to suit the filter you are running.
'''

########### PARAMETERS
# Here is a list of filters (i.e. O1S, O2, O+, etc.) Generally, I ran one filter at a time.
filters = ['O1S']
# The possible data flags are 'W' (Wind), 'T' (Temperature), 'V' (VolumeEmissionRate).
# Each flag must be added to the list if they exist in the folder of the FTP of the filter you are running
dataflags = ['W', 'T', 'V']
# If you want to run the summary for the CD type, set the following as true.
cd = False
######################

# Preprocessing
types = ['FD1', 'FD2']
tag = "FD"
h = "Latitude"
if cd:
    h = "SZA"
    types = ['CD']
    tag = 'CD'

# Defining some helper functions. This one is used to read data from a file
def prep(filename, firstheader):
    data = []

    # We open the file and iterate through lines
    for line in open(filename):
        # Differentiate the elements in a line
        a = [v for v in line.strip().split(",")]
        if (len(a)==6 or len(a)==4) and a[0]!=firstheader:
            # When the data is correct length and is not a header, we assume the line is only floats and append it in our data
            try:
                data.append([float(v) for v in a])
            except ValueError:
                b=1
    return data

# This one is used to manage the temporary files to facilitate the process of downloading a file from the FTP.
def logr(filename, header):
    # We download the wanted file
    ftp.retrbinary("RETR "+filename, open("temp/"+filename,'wb').write)
    print("RETR "+filename)
    # We obtain the data from it
    data = prep("temp/"+filename,header)
    # We remove the temporary file
    os.remove("temp/"+filename)
    return data

# We will be using a point object that will allow us to keep track of everything easier
class Point():
    def __init__(self):
        self.date = ""
        self.sza = "N/A"
        self.alt = "N/A"
        self.zwind = "N/A"
        self.szw = "N/A"
        self.temp = "N/A"
        self.st = "N/A"
        self.ver = "N/A"
        self.sv = "N/A"
        self.type = "N/A"
        self.lon = "N/A"
        self.lat = "N/A"
        self.look = "N/A"
        self.wind = "N/A"
        self.sw = "N/A"

FTP_HOST = "data.asc-csa.gc.ca"
FTP_USER = "anonymous"
FTP_PASS = ""

base = '/users/OpenData_DonneesOuvertes/pub/WINDII-data-archive/Data/'
# We log into the FTP
ftp = FTP(FTP_HOST)
ftp.login()
ftp.cwd(base)

# We iterate through each filters if necessary
for filter in filters:
    # We start by "scanning" through all of our possible data fields (wind, temperature, volume emission rate).

    # Wind data field
    flistwd1, flisttd1, flistvd1 = [], [], []
    if 'W' in dataflags:
        ftp.cwd(base+filter+'/Level2/Wind/'+types[0])
        flistwd1 = ftp.nlst()
    # Temperature data field
    if 'T' in dataflags:
        ftp.cwd(base+filter+'/Level2/Temperature/'+types[0])
        flisttd1 = ftp.nlst()
    # Volume Emission Rate data field
    if 'V' in dataflags:
        ftp.cwd(base+filter+'/Level2/VolumeEmissionRate/'+types[0])
        flistvd1 = ftp.nlst()
    # Sum
    flistd1 = flistvd1+flisttd1+flistwd1

    flistwd2, flisttd2, flistvd2 = [], [], []
    # If the type is not CD, the filter will have a second type associated to the first that may contain data for additional dates.
    if not cd:
        # Wind data field
        if 'W' in dataflags:
            ftp.cwd(base+filter+'/Level2/Wind/'+types[1])
            flistwd2 = ftp.nlst()
        # Temperature data field
        if 'T' in dataflags:
            ftp.cwd(base+filter+'/Level2/Temperature/'+types[1])
            flisttd2 = ftp.nlst()
        # Volume Emission Rate data field
        if 'V' in dataflags:
            ftp.cwd(base+filter+'/Level2/VolumeEmissionRate/'+types[1])
            flistvd2 = ftp.nlst()
    # Sum
    flistd2 = flistvd2+flisttd2+flistwd2

    # We iterate through all of our files to find all possible dates
    date1 = []
    for f in flistd1:
        temp = f.split(".")[0].split("-")
        if len(temp)!=6:
            print(f+" is a file that was ignored.")
        else:
            date1.append(temp[3]+"-"+temp[4]+"-"+temp[5])

    # We also iterate through the second type, if the first type isnt CD
    date2 = []
    if not cd:
        for f in flistd2:
            temp = f.split(".")[0].split("-")
            if len(temp)!=6:
                print(f+" is a file that was ignored.")
            else:
                date2.append(temp[3]+"-"+temp[4]+"-"+temp[5])

    # We add the two together and remove all duplicates. We then sort, which gives us a list of all possible dates that contain data.
    dates = date1+date2
    dates = list(set(dates))
    dates.sort(key = lambda date: datetime.strptime(date,'%d-%b-%Y'))
    tot = len(dates)

    # id is going to be a progress tracker
    id = 0


    # We begin doing actual work.
    print("Working for filter: "+filter)

    # We start writing a new file.
    with open(filter+"_"+tag+".csv",'w', newline='') as csvfile:
        write = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        # We write the header first:
        if not cd:
            write.writerow(['Date', 'Latitude (degree)', 'Longitude (degree)', 'Look', 'Altitude (km)', 'Wind (m/s)', 'Sigma_W', 'Temperature (K)', 'Sigma_T', 'Volume Emission Rate', 'Sigma_E', "Type"])
        else:
            write.writerow(['Date', 'SZA', 'Altitude (km)', 'Zonal Wind (m/s)', 'Sigma_ZW', 'Temperature (K)', 'Sigma_T', 'Volume Emission Rate', 'Sigma_E', "Type"])

        # We iterate through each possible dates in chronological order
        for date in dates:
            # Our id tag is going to measure progress and db is the list of points currently read.
            id += 1
            db = []

            # Sometimes, some data fields are completely missing so we must expect the error case where the folder does not exist.
            if 'W' in dataflags:
                try:
                    ftp.cwd(base+filter+'/Level2/Wind/'+types[0]+'/')
                    # We load our data for that field
                    data = logr(types[0]+'-'+filter.lower()+"-Wind-"+date+".csv", h)
                    # We create points for this data. These points will be edited further down the line to add all additional data that matches.
                    for line in data:
                        pt = Point()
                        pt.date = date
                        # We add the following info to our point for each line:
                        if not cd:
                            pt.lat, pt.lon, pt.look, pt.alt, pt.wind, pt.sw, pt.type = [line[0], line[1], line[2], line[3], line[4], line[5], types[0]]
                        else:
                            pt.sza, pt.alt, pt.zwind, pt.szw, pt.type = [line[0], line[1], line[2], line[3], types[0]]
                        db.append(pt)
                    del data
                except error_perm:
                    print("Skipped "+date+" for wind")

            # We do the same for all 3 data fields.
            if 'T' in dataflags:
                try:
                    ftp.cwd(base+filter+'/Level2/Temperature/'+types[0]+'/')
                    tfile = types[0]+'-'+filter.lower()+"-Temperature-"+date+".csv"
                    # We load our data
                    data = logr(tfile,h)
                    # If we have already added points, we simply edit them to add the relevant data.
                    if len(db) !=0:
                        if len(db)==len(data):
                            for i in range(0,len(db)):
                                db[i].temp, db[i].st = [data[i][2], data[i][3]]
                        else:
                            for i in range(0,min(len(db),len(data))):
                                db[i].temp, db[i].st = [data[i][2], data[i][3]]
                    else:
                    # If not, we create the point with the information we have
                        for line in data:
                            pt = Point()
                            pt.date = date
                            # If the type is FD/FO:
                            if not cd:
                                pt.lat, pt.lon, pt.look, pt.alt, pt.temp, pt.st, pt.type = [line[0], line[1], line[2], line[3], line[4], line[5], types[0]]
                            else:
                                pt.sza, pt.alt, pt.temp, pt.st, pt.type = [line[0], line[1], line[2], line[3], types[0]]
                            db.append(pt)
                    del data
                except error_perm:
                    print("Skipped "+date+" for temperature")

            # Now for our last field:
            if 'V' in dataflags:
                try:
                    ftp.cwd(base+filter+'/Level2/VolumeEmissionRate/'+types[0]+'/')
                    tfile = types[0]+'-'+filter.lower()+"-VolumeEmissionRate-"+date+".csv"
                    # We load the data
                    data = logr(tfile, h)
                    # If we have already added points, we simply edit them to add the relevant data.
                    if len(db) !=0:
                        if len(db)==len(data):
                            for i in range(0,len(db)):
                                db[i].ver, db[i].sv = [data[i][2], data[i][3]]
                        else:
                            for i in range(0,min(len(db),len(data))):
                                db[i].ver, db[i].sv = [data[i][2], data[i][3]]
                    else:
                    # If not, we create the point with the information we have
                        for line in data:
                            pt = Point()
                            pt.date = date
                            if not cd:
                                pt.lat, pt.lon, pt.look, pt.alt, pt.ver, pt.sv, pt.type = [line[0], line[1], line[2], line[3], line[4], line[5], types[0]]
                            else:
                                pt.sza, pt.alt, pt.ver, pt.sv, pt.type = [line[0], line[1], line[2], line[3], types[0]]
                            db.append(pt)
                    del data
                except error_perm:
                    print("Skipped "+date+" for volume emission rate")

            # If the first type is not CD, then there will be a second type, we must check if there is data for those fields in the second type
            # for the same date and we add it to our database.
            if not cd:
                # Sometimes, some data fields are completely missing so we must expect the error case where the folder does not exist.
                if 'W' in dataflags:
                    try:
                        ftp.cwd(base+filter+'/Level2/Wind/'+types[1]+'/')
                        # We load our data for that field
                        data = logr(types[1]+'-'+filter.lower()+"-Wind-"+date+".csv", h)
                        # We create points for this data. These points will be edited further down the line to add all additional data that matches.
                        for line in data:
                            pt = Point()
                            pt.date = date
                            # We add the following info to our point for each line, if the type is FD/FO:
                            if not cd:
                                pt.lat, pt.lon, pt.look, pt.alt, pt.wind, pt.sw, pt.type = [line[0], line[1], line[2], line[3], line[4], line[5], types[1]]
                            else:
                                pt.sza, pt.alt, pt.zwind, pt.szw, pt.type = [line[0], line[1], line[2], line[3], types[1]]
                            db.append(pt)
                        del data
                    except error_perm:
                        print("Skipped "+date+" for wind")

                # We do the same for all 3 data fields.
                if 'T' in dataflags:
                    try:
                        ftp.cwd(base+filter+'/Level2/Temperature/'+types[1]+'/')
                        tfile = types[1]+'-'+filter.lower()+"-Temperature-"+date+".csv"
                        # We load our data
                        data = logr(tfile,h)
                        # If we have already added points, we simply edit them to add the relevant data.
                        if len(db) !=0:
                            if len(db)==len(data):
                                for i in range(0,len(db)):
                                    db[i].temp, db[i].st = [data[i][2], data[i][3]]
                            else:
                                for i in range(0,min(len(db),len(data))):
                                    db[i].temp, db[i].st = [data[i][2], data[i][3]]
                        else:
                        # If not, we create the point with the information we have
                            for line in data:
                                pt = Point()
                                pt.date = date
                                # If the type is FD/FO:
                                if not cd:
                                    pt.lat, pt.lon, pt.look, pt.alt, pt.temp, pt.st, pt.type = [line[0], line[1], line[2], line[3], line[4], line[5], types[1]]
                                else:
                                    pt.sza, pt.alt, pt.temp, pt.st, pt.type = [line[0], line[1], line[2], line[3], types[1]]
                                db.append(pt)
                        del data
                    except error_perm:
                        print("Skipped "+date+" for temperature")

                # Now for our last field:
                if 'V' in dataflags:
                    try:
                        ftp.cwd(base+filter+'/Level2/VolumeEmissionRate/'+types[1]+'/')
                        tfile = types[1]+'-'+filter.lower()+"-VolumeEmissionRate-"+date+".csv"
                        # We load the data
                        data = logr(tfile, h)
                        # If we have already added points, we simply edit them to add the relevant data.
                        if len(db) !=0:
                            if len(db)==len(data):
                                for i in range(0,len(db)):
                                    db[i].ver, db[i].sv = [data[i][2], data[i][3]]
                            else:
                                for i in range(0,min(len(db),len(data))):
                                    db[i].ver, db[i].sv = [data[i][2], data[i][3]]
                        else:
                        # If not, we create the point with the information we have
                            for line in data:
                                pt = Point()
                                pt.date = date
                                # If the type is FD/FO:
                                if not cd:
                                    pt.lat, pt.lon, pt.look, pt.alt, pt.ver, pt.sv, pt.type = [line[0], line[1], line[2], line[3], line[4], line[5], types[1]]
                                else:
                                    pt.sza, pt.alt, pt.ver, pt.sv, pt.type = [line[0], line[1], line[2], line[3], types[1]]
                                db.append(pt)
                        del data
                    except error_perm:
                        print("Skipped "+date+" for volume emission rate")

            # Once we have finished reading all data fields for one date, we write them under our earlier heading.
            for pt in db:
                if not cd:
                    write.writerow([pt.date, pt.lon, pt.lat, pt.look, pt.alt, pt.wind, pt.sw, pt.temp, pt.st, pt.ver, pt.sv, pt.type])
                else:
                    write.writerow([pt.date, pt.sza, pt.alt, pt.zwind, pt.szw, pt.temp, pt.st, pt.ver, pt.sv, pt.type])

            # We log the progress
            print("############################################################# PROGRESS: "+str(round(id/tot*100,2))+"%")
            del db
        ftp.quit()
# The work is done.



'''
        ############## LEGACY CODE
        #
        # If the data is type FD/FO, it contains a second set of dates. We run the exact same thing as earlier
        # If the data is type CD, this next for loop must be entirely commented out.
        # Set 2
        for date in date2:
            id2 += 1
            db = []

            # Similarly, we run through all three of our data fields. In this part of the code, the type should always be FD/FO.
            try:
                ftp.cwd(base+filter+'/Level2/'+'Wind'+'/FD2/')
                data = logr("FD2-"+filter.lower()+"-Wind-"+date+".csv",'Latitude')
                for line in data:
                    pt = Point()
                    pt.date = date
                    pt.lat, pt.lon, pt.look, pt.alt, pt.wind, pt.sw, pt.type = [line[0], line[1], line[2], line[3], line[4], line[5], "FD2"]
                    db.append(pt)
                del data
            except error_perm:
                print("Skipped "+date+" for wind")

            try:
                ftp.cwd(base+filter+'/Level2/'+'Temperature'+'/FD2/')
                tfile = "FD2-"+filter.lower()+"-Temperature-"+date+".csv"
                data = logr(tfile,'Latitude')
                if len(db) !=0:
                    if len(db)==len(data):
                        for i in range(0,len(db)):
                            db[i].temp, db[i].st = [data[i][4], data[i][5]]
                    else:
                        for i in range(0,min(len(db),len(data))):
                            db[i].temp, db[i].st = [data[i][4], data[i][5]]
                else:
                    for line in data:
                        pt = Point()
                        pt.date = date
                        pt.lat, pt.lon, pt.look, pt.alt, pt.temp, pt.st, pt.type = [line[0], line[1], line[2], line[3], line[4], line[5], "FD2"]
                        db.append(pt)
                del data
            except error_perm:
                print("Skipped "+date+" for temperature")

            try:
                ftp.cwd(base+filter+'/Level2/'+'VolumeEmissionRate'+'/FD2/')
                tfile = "FD2-"+filter.lower()+"-VolumeEmissionRate-"+date+".csv"
                data = logr(tfile,'Latitude')
                if len(db) !=0:
                    if len(db)==len(data):
                        for i in range(0,len(db)):
                            db[i].ver, db[i].sv = [data[i][4], data[i][5]]
                    else:
                        for i in range(0,min(len(db),len(data))):
                            db[i].ver, db[i].sv = [data[i][4], data[i][5]]
                else:
                    for line in data:
                        pt = Point()
                        pt.date = date
                        pt.lat, pt.lon, pt.look, pt.alt, pt.ver, pt.sv, pt.type = [line[0], line[1], line[2], line[3], line[4], line[5], "FD2"]
                        db.append(pt)
                del data
            except error_perm:
                print("Skipped "+date+" for volume emission rate")

            # Once we have loaded all of our data, we write it.
            for pt in db:
                write.writerow([pt.date, pt.lat, pt.lon, pt.look, pt.alt, pt.wind, pt.sw, pt.temp, pt.st, pt.ver, pt.sv, pt.type])

            # We log the progress.
            print("############################################################# PROGRESS: "+str(round((len(date1)+id2)/tot*100,2))+"%")
            del db
    # We are done with this file.
'''
