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

def prep(filename, firstheader, l):
    data = []
    for line in open(filename):
        a = [v for v in line.strip().split(",")]
        if (len(a)==l) and a[0]!=firstheader:
            try:
                data.append([float(v) for v in a])
            except ValueError:
                b=1
    return data

def logr(filename, header, l):
    ftp.retrbinary("RETR "+filename, open("temp/"+filename,'wb').write)
    print("RETR "+filename)
    data = prep("temp/"+filename,header,l)
    os.remove("temp/"+filename)
    return data

# We set up some helper variables before we begin.
trnbr = 0
filelist = ["O+_FD.csv"]
FTP_HOST = "data.asc-csa.gc.ca"
FTP_USER = "anonymous"
FTP_PASS = ""
results = []
base = '/users/OpenData_DonneesOuvertes/pub/WINDII-data-archive/Data/'
clock = process_time()

# We iterate over each summary file
for file in filelist:
    print("Working for "+file+".")
    # We load in the summary file, which takes a while
    database = pd.read_csv(file)
    ftp = FTP(FTP_HOST)
    ftp.login()
    ftp.cwd(base)
    filename = file.split(".")[0].split("_")[0]
    filetype = file.split(".")[0].split("_")[1]

    # We do some additional set-up here to make sure everything can be run automatically without our input.
    success = 0
    failure = 0


    ftp.cwd(base+filename+"/Level2/")
    mtypes = ftp.nlst()

    # We iterate over the number of trials.
    for i in range(0, TRIALS):
        # We catch some exceptions because there are artifacts on the FTP server where even if the data file exists, it is completely empty.
        # When this happens, the success rate is lowered.
        if filetype=="CD":
            d = ["CD"]
            header = "SZA"
            l = 4
            altindex = 1
            basecol = 3
        elif filetype=="FD":
            d = ["FD1", "FD2"]
            header = "Latitude"
            l = 6
            altindex = 3
            basecol = 5
        elif filetype=="FO":
            d = ["FO1", "FO2"]
            header = "Latitude"
            l = 6
            altindex = 3
            basecol = 5

        trnbr += 1
        randmtype = random.choice(mtypes)
        randftype = random.choice(d)

        if randmtype == "Temperature":
            dataindex = [basecol+2, basecol+3]
        elif randmtype == "Wind":
            dataindex = [basecol, basecol+1]
            if filetype=="CD":
                l=6
        elif randmtype == "VolumeEmissionRate":
            dataindex = [basecol+4, basecol+5]

        ftp.cwd(base+filename+"/Level2/"+randmtype+"/"+randftype+"/")
        ext = ""
        while ext !="csv":
            randfile = random.choice(ftp.nlst())
            ext = randfile.split(".")[1]

        data = logr(randfile, header, l)
        rdata = random.choice(data)
        temp = randfile.split(".")[0].split("-")
        date = temp[3]+"-"+temp[4]+"-"+temp[5]

        tdf =  getIndexes(database, date, "Date")
        adf = getIndexes(database, rdata[altindex], "Altitude (km)")
        common = list(set(tdf).intersection(adf))
        filtered = database.iloc[common].values
        att = 0

        for x in filtered:
            if filetype == "CD":
                if x[0]==date and x[1]==rdata[0] and x[2]==rdata[1] and x[dataindex[0]]==rdata[2] and x[dataindex[1]]==rdata[3]:
                    att += 1
            elif filetype == "FD" or filetype=="FO":
                if x[0]==date and x[1]==rdata[0] and x[2]==rdata[1] and x[3]==rdata[2] and x[4]==rdata[3] and x[dataindex[0]]==rdata[4] and x[dataindex[1]]==rdata[5]:
                    att += 1

        if att != 0:
            success += 1
            print("Success on trial #"+str(i+1)+"/"+str(TRIALS)+" for "+file+".")
        else:
            failure += 1
            print("Failure on trial #"+str(i+1)+"/"+str(TRIALS)+" for "+file+".")

    # When we are done iterating for each trial, we log our work done for the file.
    print("Finished working for "+file+" with a final success rate of "+str(round(success/TRIALS,4)*100)+"% after " + str(process_time()-clock)+" seconds.")
    results.append(round(success/TRIALS,4)*100)
    ftp.quit()

# Finally, when we are done working on all files, we log the final results.
print("Final results for all "+str(len(filelist))+" files:")
for i in range(0,len(filelist)):
    print(str(results[i])+"% success rate for "+filelist[i]+".")
print("Done after "+str(process_time()-clock)+" seconds of runtime. This run ran a total of "+ str(trnbr)+" trials with an average of"+str(round(trnbr/(process_time()-clock),2))+" trials per second.")
