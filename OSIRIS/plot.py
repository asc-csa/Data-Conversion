import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats
'''
# We import the relevant packages and we set the font size for the plots
plt.rcParams.update({'font.size': 22})

# We list all the files we want to produce plots for and all the geofields we want to plot against.
filelist = ["Aerosol Summary.csv", "BrO Summary.csv", "NO2 Summary.csv", "O3 Summary.csv", "OH Summary.csv"]
geolist = ["Time (TAI 1993)", "Longitude (degree)", "Latitude (degree)", " Altitude (km)"]

# We iterate through these files
for file in filelist:

    # We load the summary file. Here we use pd.read_csv as it is much faster for bigger files than np.genfromtxt
    df = pd.read_csv(file)
    filename = file.split(" ")[0]

    # We set some helper variables. The contents of these values are not important, the only important thing is the length of the arrays.
    if filename=="Aerosol":
        d = ["AerosolExtinction.csv"]
    elif filename=="O3":
        d = ["O3NumberDensity.csv"]
    elif filename=="BrO":
        d = ["BrO.csv"]
    elif filename=="NO2":
        d = ["NO2NumberDensity.csv"]
    elif filename=="OH":
        d = ["OHPrompt.csv", "OHResonance.csv"]

    # The first 4 columns are geolocation fields columns (time, longitude, latitude, altitude) and so column with index 5 contains the data. We save the column header for later use.
    dat1 = df.columns.values[4]
    for geo in geofields:
        geoname = geo.split("(")[0].lower()
        # We take only the two columns of the data of interest. Usually, it is one geolocation field and one data field, and we want to plot the latter against the former.
        dattime = df[[geo, dat1]]

        # The data contains -9999.0 as a "NaN" value. We get rid of all rows containing that value
        dattime.drop(dattime.loc[dattime[dat1]==-9999.0].index, inplace=True)

        # For plotting purposes, we remove outliers that are more than 3 standard deviations away.
        dattime = dattime[(np.abs(stats.zscore(dattime)) < 3).all(axis=1)]

        # We create a plot of the two fields. When the geofield is altitude, we want to plot the data on the x axis and the altitude on the y axis.
        if geo==" Altitude (km)":
            dattime.plot(y=geo, x=dat1, kind='scatter', s=2.0, alpha=0.003, title=dat1.split("(")[0]+"as a function of "+geoname)
        else:
            dattime.plot(x=geo, y=dat1, kind='scatter', s=2.0, alpha=0.003, title=dat1.split("(")[0]+"as a function of "+geoname)

        # We turn the plot into a figure
        f = plt.gcf()
        # We make the figure big
        f.set_figwidth(20)
        f.set_figheight(15)
        # We save the figure
        f.savefig(filename+"_"+geoname+".png")

        # In the case of OH, there are two data fields, and so we repeat this process for the second data field.
        if len(d)!=1:
            # The second data field is in the 6th column of our dataframe
            dat2 = df.columns.values[5]
            # The rest is exactly the same as before
            dattime = df[[geo, dat2]]
            dattime.drop(dattime.loc[dattime[dat2]==-9999.0].index, inplace=True)
            dattime = dattime[(np.abs(stats.zscore(dattime)) < 3).all(axis=1)]
            if geo==" Altitude (km)":
                dattime.plot(y=geo, x=dat2, kind='scatter', s=2.0, alpha=0.003, title=dat2.split("(")[0]+"as a function of "+geoname)
            else:
                dattime.plot(x=geo, y=dat2, kind='scatter', s=2.0, alpha=0.003, title=dat2.split("(")[0]+"as a function of "+geoname)
            f = plt.gcf()
            f.set_figwidth(20)
            f.set_figheight(15)
            f.savefig(filename+"_"+geoname+"2.png")
'''

filelist = ["Aerosol Summary.csv", "BrO Summary.csv", "NO2 Summary.csv", "O3 Summary.csv", "OH Summary.csv"]
dflst = []
plt.rcParams.update({'font.size': 6})

for file in filelist:
    print("Reading "+file)
    df = pd.read_csv(file)
    if file=="OH Summary.csv":
        tdf = df.iloc[:,[4,5]]
        tdf.drop(tdf.loc[tdf[tdf.columns[0]]==-9999.0].index, inplace=True)
        tdf.drop(tdf.loc[tdf[tdf.columns[1]]==-9999.0].index, inplace=True)
        tdf = tdf[(np.abs(stats.zscore(tdf)) < 3).all(axis=1)]
    else:
        tdf = df.iloc[:,[4]]
        tdf.drop(tdf.loc[tdf[tdf.columns[0]]==-9999.0].index, inplace=True)
        tdf = tdf[(np.abs(stats.zscore(tdf)) < 3).all(axis=1)]

    print(tdf)
    dflst.append(tdf)


ndf = pd.concat([dflst[0],dflst[1],dflst[2],dflst[3],dflst[4]],axis=1)

#ndf = pd.DataFrame(np.random.randn(1000,4), columns=['A','B','C','D'])
pd.plotting.scatter_matrix(ndf, alpha=0.1, figsize=(20,15))
plt.suptitle("Scatterplot of OSIRIS data fields")
f = plt.gcf()
f.savefig("Scatterplot.png")
