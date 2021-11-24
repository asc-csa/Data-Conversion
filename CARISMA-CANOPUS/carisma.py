from ftplib import FTP
import re
import csv
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
            if a[0]!="# Date(dd/mm/yyyy)":
                if len(a)<5:
                    values = a[2].split("-")
                    if len(values) == 3:
                        temp = [a[0], a[1], values[0], values[1], values[2], a[3]]
                        a = temp
                    elif len(values) == 4:
                        temp = [a[0], a[1], "-"+values[1], values[2], values[3], a[3]]
                        a = temp
                    elif len(values) == 2:
                        if values[0].count(".") == 2:
                            split = values[0].split(".")
                            temp = [a[0], a[1], split[0]+"."+split[1][0:3], split[1][3:-1]+"."+split[2], values[1],a[3]]
                        else:
                            split = values[1].split(".")
                            temp = [a[0], a[1], values[0], split[0]+"."+split[1][0:3], split[1][3:-1]+"."+split[2],a[3]]
                        a = temp
                    else:
                        split = values[0].split(".")
                        temp = [a[0], a[1], split[0]+"."+split[1][0:3], split[1][3:-1]+"."+split[2][0:3],
                                split[2][3:-1]+"."+split[3], a[3]]
                        a = temp

                elif len(a) == 5:
                    if("-" in a[2]):
                        values = a[2].split("-")
                        if values[0] == '' and len(values) != 3:
                            break;
                        temp = []
                        if len(values) == 3:
                            temp = [a[0], a[1], "-" + values[1], values[2], a[3], a[4]]
                        elif len(values) == 2:
                            temp = [a[0], a[1], values[0], values[1], a[3],  a[4]]
                        a = temp
                    if("-" in a[3]):
                        values = a[3].split("-")
                        if values[0] == '' and len(values) != 3:
                            break
                        temp = []
                        if len(values) == 3:
                            temp = [a[0], a[1], a[2], "-"+values[1], values[2], a[4]]
                        elif len(values) == 2:
                            temp = [a[0], a[1], a[2], values[0], values[1], a[4]]
                        a = temp
                try:
                    float(a[2])
                    float(a[3])
                    float(a[4])
                    data.append(a)
                except:
                    print(a)
            else:
                # ... or the header.
                header = a
    return [data, header]

# This helper function manages downloading the data from the ftp and deleting it once we are done working with it.
def logr(filename):
    ftp.retrbinary("RETR "+filename, open("temp/"+filename,'wb').write)
    print("RETR "+filename)
    [data, header] = prep("temp/"+filename)
    os.remove("temp/"+filename)
    return [data, header]

FTP_HOST = "data.asc-csa.gc.ca"
FTP_USER = "anonymous"
FTP_PASS = ""

base = '/users/OpenData_DonneesOuvertes/pub/carisma_csv/'
target = 'mag/daily/'
ftp = FTP(FTP_HOST)

# Those are all the folders that contain data in the CANOPUS folder.
# flist = ["BACK","CONT","DAWS", "ESKI", "FCHU","FSIM", "FSMI", "GILL", "ISLL", "MCMU", "PINA", "RABB", "RANK", "TALO"]
flist = ["TALO"]
# The data ranges from 1986 to 2009
ylist = range(1986,2010)
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
            print(str(round(100*(year-1986)/(2010-1986), 2))+"% Progress.")
            ftp.cwd(base)
            ftp.cwd(base+target+str(year))
            type = ftp.nlst()
            print("Type: ",type)
            # If the folder exists in the year we are working in, we go in and read each file.
            if folder in type:
                ftp.cwd(base+target+str(year)+"/"+folder)
                files = ftp.nlst()
                # We iterate through each file.
                for file in files:
                    # print(file)
                    pattern = r'[0-9]'
                    filename = re.sub(pattern,"",file.split(".")[0])
                    # We get the data
                    [data, header] = logr(file)
                    # If we have not encountered the file of this specific type (ex. talo_rio or talo_norstar)
                    if filename not in encountered_files:
                        print(filename)
                        header[0] = "Date (yyyy/mm/dd)"
                        print(header)
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
