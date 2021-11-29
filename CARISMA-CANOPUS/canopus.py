from urllib.parse import quote
from ftplib import FTP
import csv
import pandas as pd
import numpy as np
import os
from time import process_time

# We have our helper functions
def prep(filename):
    data = []
    header = []
    for line in open(filename):
        a = [v for v in line.strip().split(",")]
        #If a row contains more than 2 columns, it is either...
        if (len(a)>2):
            if a[0]!="date(dd/mm/yy)":
                # ... data
                data.append(a)
            else:
                # ... or the header.
                header = a
    return [data, header]

# This helper function manages downloading the data from the ftp and deleting it once we are done working with it.
def logr(filename):
    ftp.retrbinary("RETR "+filename, open("temp/"+filename,'wb').write)
    #print("RETR "+filename)
    [data, header] = prep("temp/"+filename)
    os.remove("temp/"+filename)
    return [data, header]

FTP_HOST = "data.asc-csa.gc.ca"
FTP_USER = "anonymous"
FTP_PASS = ""

base = '/users/OpenData_DonneesOuvertes/pub/CANOPUS _CSV/'
ftp = FTP(FTP_HOST)

# Those are all the folders that contain data in the CANOPUS folder.
flist = ["FCHU", "FSIM", "FSMI", "GILL", "ISLL", "MCMU", "PINA", "RABB", "RANK", "TALO"]
# The data ranges from 1989 to 2007
ylist = range(1989,2008)
encountered_files = []

# We start the work.
print("Beginning process...")
bclock = process_time()
ftp.login()
for folder in flist:
    print("Working for "+folder+"...")
    clock = process_time()

    try:
        # We go through each year
        for year in ylist:
            # Log the progress
            print(str(round(100*(year-1989)/(2008-1989), 2))+"% Progress.")
            ftp.cwd(base)
            ftp.cwd(base+str(year))
            type = ftp.nlst()
            # If the folder exists in the year we are working in, we go in and read each file.
            if folder in type:
                ftp.cwd(base+str(year)+"/"+folder)
                files = ftp.nlst()
                # We iterate through each file.
                for file in files:
                    print(file)
                    filename = file.split("_")[0]+"_"+file.split("_")[1]
                    print(filename)
                    # We get the data
                    [data, header] = logr(file)
                    # If we have not encountered the file of this specific type (ex. talo_rio or talo_norstar)
                    if filename not in encountered_files:
                        # We create a new file and add the proper header at the top of the file
                        encountered_files.append(filename)
                        with open(filename+'.csv','a',newline='') as csvfile:
                            write = csv.writer(csvfile,delimiter=',')
                            write.writerow(header)
                    # If not, we simply add the data to the existing file.
                    with open(filename+'.csv','a', newline='') as csvfile:
                        write = csv.writer(csvfile,delimiter=',')
                        for row in data:
                            write.writerow(row)
    except KeyboardInterrupt:
        ftp.quit()
        print("Interrupted properly")
    print("Done working for "+folder+" after "+str(process_time()-clock)+"s.")
print("Fully done after "+str(process_time()-bclock)+"s.")
# We are done and we log all the times!
ftp.quit()
