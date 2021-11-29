from ftplib import FTP
import pandas as pd
import os
import re
import random
import numpy as np
from time import process_time
from sys import getsizeof
import psutil

'''
The goal of this script is to do an automated verification of the validity of the summary files produced by my other script.
To do so, we run a large number of trials where a random point is selected on the FTP server and we verify that this point exists and is exactly the same in our summary file.
The number of trials run per file is determined by the "TRIALS" constant just below.
'''
TRIALS = 8

PROCESS = psutil.Process(os.getpid())
MEGA = 10 ** 6
MEGA_STR = ' ' * MEGA

def print_memory_usage():
    """Prints current memory usage stats.
    See: https://stackoverflow.com/a/15495136

    :return: None
    """
    total, available, percent, used, free = psutil.virtual_memory()
    total, available, used, free = total / MEGA, available / MEGA, used / MEGA, free / MEGA
    proc = PROCESS.memory_info()[1] / MEGA
    print('process = %s total = %s available = %s used = %s free = %s percent = %s'
          % (proc, total, available, used, free, percent))

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

def prep(filename):
    data = []
    for line in open(filename):
        a = [v for v in line.strip().split(",")]
        # print(len(a))
        if (len(a)==6) and a[0]!="# Date(dd/mm/yyyy)":
            try:
                data.append([str(v) for v in a])
            except ValueError:
                b=1
    return data

def logr(filename):
    ftp.retrbinary("RETR "+filename, open("temp/"+filename,'wb').write)
    print("RETR "+filename)
    data = prep("temp/"+filename)
    os.remove("temp/"+filename)
    return data

# We set up some helper variables before we begin.
trnbr = 0
filelist = ["BACK","DAWS", "ESKI", "FSIM", "MCMU","PINA", "RANK", "TALO", "CONT","FCHU", "FSMI", "GILL", "ISLL", "RABB"]

FTP_HOST = "data.asc-csa.gc.ca"
FTP_USER = "anonymous"
FTP_PASS = ""
results = []
base = '/users/OpenData_DonneesOuvertes/pub/carisma_csv/mag/daily/'
clock = process_time()

# We iterate over each summary file
for file in filelist:
    print("Working for "+file+".")
    # We load in the summary file, which takes a while
    n = sum(1 for line in open(file+".csv"))
    print(n)
    s = 1000
    skip = sorted(random.sample(range(1, n + 1), n - s))
    database = pd.read_csv(file+".csv",
        dtype={"X": 'float', "Y": 'float', "Z": 'float',
               "F=. if the data is valid anything else the data is suspect.": "string"}, skiprows=skip)
    print("Done loading csv")
    ftp = FTP(FTP_HOST)
    ftp.login()
    ftp.cwd(base)

    # We do some additional set-up here to make sure everything can be run automatically without our input.
    success = 0
    failure = 0


    ftp.cwd(base)
    # We iterate over the number of trials.
    for i in range(0, TRIALS):
        # print_memory_usage()
        # We catch some exceptions because there are artifacts on the FTP server where even if the data file exists, it is completely empty.
        # When this happens, the success rate is lowered.
        trnbr += 1
        rdata = database.sample().values.tolist()[0]
        rdate = str(rdata[0])
        pattern = r'[0-9]'
        filename = re.sub(pattern, "", file.split(".")[0])
        print(base+str(rdate.split("/")[0])+"/"+filename)
        ftp.cwd(base+str(rdate.split("/")[0])+"/"+filename)
        data = logr(rdate.replace("/","")+file+".MAG.csv")
        file_dataframe = pd.DataFrame(data, columns=database.columns.tolist())
        adf = getIndexes(file_dataframe, rdata[1], "time(hh:mi:ss)")
        filtered = file_dataframe.iloc[adf].values
        att = 0

        for x in filtered:
            print(x)
            print(rdata)
            if x[0]==rdata[0] and x[1]==rdata[1] and float(x[2])==float(rdata[2]) and float(x[3])==float(rdata[3]) and float(x[4])==float(rdata[4]) and rdata[5]==rdata[5]:
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
print("Done after "+str(process_time()-clock)+" seconds of runtime. This run ran a total of "+ str(trnbr)+" trials with an average of "+str(round(trnbr/(process_time()-clock),2))+" trials per second.")
