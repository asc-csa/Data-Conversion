from urllib.parse import quote
from ftplib import FTP
import csv
import pandas as pd
import numpy as np
import os
import random
from time import process_time

'''
The goal of this script is to do an automated verification of the validity of the summary files produced by my other script.
To do so, we run a large number of trials where a random point is selected on the FTP server and we verify that this point exists and is exactly the same in our summary file.
The number of trials run per file is determined by the "TRIALS" constant just below.
'''
TRIALS = 1000

def getIndexes(dfObj, value, col):
    ''' Get index positions of value in dataframe i.e. dfObj.'''
    listOfPos = list()
    # Get bool dataframe with True at positions where the given value exists
    result = dfObj.isin([value])
    # Get list of columns that contains the value
    seriesObj = result.any()
    rows = list(result[col][result[col] == True].index)
    for row in rows:
        listOfPos.append(row)
    # Return a list of tuples indicating the positions of value in the dataframe
    return listOfPos


# We set up some helper variables before we begin.
trnbr = 0
filelist = ["Aerosol Summary.csv", "BrO Summary.csv", "NO2 Summary.csv", "O3 Summary.csv", "OH Summary.csv"]
geofields = ["Longitude.csv", "Latitude.csv", "Altitude.csv", "Time.csv"]
FTP_HOST = "data.asc-csa.gc.ca"
FTP_USER = "anonymous"
FTP_PASS = ""
results = []
base = '/users/OpenData_DonneesOuvertes/pub/OSIRIS/Data_format CSV/Level2/daily/'
clock = process_time()

# We iterate over each summary file
for file in filelist:
    print("Working for "+file+".")
    # We load in the summary file, which takes a while
    database = pd.read_csv(file)
    ftp = FTP(FTP_HOST)
    ftp.login()
    ftp.cwd(base)
    filename = file.split(" ")[0]

    # We do some additional set-up here to make sure everything can be run automatically without our input.
    success = 0
    failure = 0
    if filename=="Aerosol":
        f = "OSIRIS-Odin L2-"+filename+"-Limb-MART v5-07"
        d = ["AerosolExtinction.csv"]
    elif filename=="O3":
        f = "OSIRIS-Odin L2-"+filename+"-Limb-MART v5-07"
        d = ["O3NumberDensity.csv"]
    elif filename=="BrO":
        f = "OSIRIS-Odin L2-BrO-Limb-Zonal-DOAS-OE v5-00"
        d = ["BrO.csv"]
    elif filename=="NO2":
        f = "OSIRIS-Odin L2-NO2-Limb-Chalmers-DOAS-OE v03-00"
        d = ["NO2NumberDensity.csv"]
    elif filename=="OH":
        f = "OSIRIS-Odin L2-OH-Limb v01-00"
        d = ["OHPrompt.csv", "OHResonance.csv"]

    # We get the full list of all the months containing data
    monthlist = ftp.nlst()

    # We iterate over the number of trials.
    for i in range(0, TRIALS):
        # We catch some exceptions because there are artifacts on the FTP server where even if the data file exists, it is completely empty.
        # When this happens, the success rate is lowered.
        try:
            trnbr += 1
            con = True
            nlist = []

            # We look for a folder that contains data for the summary file we are currently working on.
            # Essentially, a random month is chosen and then we verify if there is data for the same gas as the summary file we are currently working with, if not we select a different month until it does.
            while con:
                m = random.choice(monthlist)
                ftp.cwd(base+m)
                flist = ftp.nlst()
                for fl in flist:
                    temp = fl.split("_")
                    if temp[0]+" "+temp[1]+" "+temp[2]==f:
                        nlist.append(fl)
                if len(nlist)!=0:
                    con = False

            # We have that nlist is the list of files from the random month folder that are of the same type than the summary file we currently work with. We randomly select one file from that list.
            folder = random.choice(nlist)

            # We then download all the necessary files from that data folder.
            ftp.cwd(base+m+"/"+folder+"/Geolocation Fields/")
            for g in geofields:
                ftp.retrbinary("RETR "+g, open("temp/"+g,'wb').write)
            ftp.cwd(base+m+"/"+folder+"/Data Fields/")
            for data in d:
                ftp.retrbinary("RETR "+ data, open("temp/"+data,'wb').write)

            # We load these temporary files
            time = np.genfromtxt('temp/Time.csv', delimiter=',')
            alt = np.genfromtxt('temp/Altitude.csv', delimiter=',')
            lat = np.genfromtxt('temp/Latitude.csv', delimiter=',')
            lon = np.genfromtxt('temp/Longitude.csv', delimiter=',')
            dat = []
            for data in d:
                dat.append(np.genfromtxt('temp/'+data, delimiter=','))

            # In the data, every point can be described using 2 'keys'. These two keys are the index of the time point as well as the index of the altitude point.
            # The time key is shared with latitude and longitude as well (meaning the index of latitude/longitude points correspond to the time index.)
            # We select a random time and a random altitude from that file.
            rtime = random.choice(time)
            ralt = random.choice(alt)

            # We run through our summary file and we identify all rows that have this time value and we identify all rows that have this altitude value
            tdf =  getIndexes(database, rtime, "Time (TAI 1993)")
            adf = getIndexes(database, ralt, " Altitude (km)")

            # We then identify the common rows between those two list and filter the database based on that so that we get a database containing only points that have
            # the same time and altitude as was randomly chosen.
            common = list(set(tdf).intersection(adf))
            filtered = database.iloc[common].values

            # We then go through every row to see if that is true. There are multiple points with the same key pairs, and so we iterate through those to see if one of them
            # corresponds to the data we randomly picked.
            att = 0
            for x in filtered:
                # We get the key pairs
                k = list(time).index(rtime)
                j = list(alt).index(ralt)

                # We check to see if for each row all the geolocation fields match
                if  x[0]==time[k] and x[1]==alt[j] and x[2]==lat[k] and x[3]==lon[k]:
                    # We then check if all the data fields match. If so, we increase the att constant.
                    if len(dat)==2:
                        if x[4]==dat[0][k][j] and x[5]==dat[1][k][j]:
                            att += 1
                    elif len(dat)==1:
                        if x[4]==dat[0][k][j]:
                            att += 1

            # We do some cleanup to remove the temporary files.
            for g in geofields+d:
                os.remove("temp/"+g)

            # We check if the att constant was changed. If it was, it means that we found a point where all the fields matched to the randomly selected point from the FTP.
            # Everytime we succeed, we increase the success parameter.
            if att != 0:
                success += 1
                print("Success on trial #"+str(i+1)+"/"+str(TRIALS)+" for "+file+".")
            else:
                failure += 1
                print("Failure on trial #"+str(i+1)+"/"+str(TRIALS)+" for "+file+".")
        except:
            print("Skipped trial #"+str(i+1)+" due to error.")

    # When we are done iterating for each trial, we log our work done for the file.
    print("Finished working for "+file+" with a final success rate of "+str(round(success/TRIALS,4)*100)+"% after " + str(process_time()-clock)+" seconds.")
    results.append(round(success/TRIALS,4)*100)
    ftp.quit()

# Finally, when we are done working on all files, we log the final results.
print("Final results for all "+str(len(filelist))+" files:")
for i in range(0,len(filelist)):
    print(str(results[i])+"% success rate for "+filelist[i]+".")
print("Done after "+str(process_time()-clock)+" seconds of runtime. This run ran a total of "+ str(trnbr)+" trials with an average of"+str(round(trnbr/(process_time()-clock),2))+" trials per second.")
