import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

# We import the relevant packages and we set the font size for the plots
plt.rcParams.update({'font.size': 22})

# We list all the files we want to produce plots for and all the geofields we want to plot against.
filelist = ["OH_FD.csv"]
fdgeolist = ["Latitude (degree)", "Longitude (degree)", "Look", "Altitude (km)"]
fddata = ["Wind (m/s)", "Sigma_W", "Temperature (K)", "Sigma_T", "Volume Emission Rate", "Sigma_E"]
cdgeolist = ["SZA", "Altitude (km)"]
cddata = ["Zonal Wind (m/s)", "Sigma_ZW", "Temperature (K)", "Sigma_T", "Volume Emission Rate", "Sigma_E"]

# We iterate through these files
for file in filelist:
    filename = file.split(".")[0]
    # We load the summary file. Here we use pd.read_csv as it is much faster for bigger files than np.genfromtxt
    df = pd.read_csv(file)
    filetype = file.split(".")[0].split("_")[1]
    if filetype=="FD" or filetype=="FO":
        geolst = fdgeolist
        datalst = fddata
    else:
        geolst = cdgeolist
        datalst = cddata

    # The first 4 columns are geolocation fields columns (time, longitude, latitude, altitude) and so column with index 5 contains the data. We save the column header for later use.
    for data in datalst:
        for geo in geolst:
            geoname = geo.split("(")[0].lower()
            dataname = data.split("(")[0]
            print("Plotting "+dataname+" for "+geoname+"...")
            # We take only the two columns of the data of interest. Usually, it is one geolocation field and one data field, and we want to plot the latter against the former.
            dataframe = df[[geo, data]]

            # The data contains -9999.0 as a "NaN" value. We get rid of all rows containing that value
            dataframe.drop(dataframe.loc[dataframe[data]=="N/A"].index, inplace=True)

            # For plotting purposes, we remove outliers that are more than 3 standard deviations away.
            dataframe = dataframe[(np.abs(stats.zscore(dataframe)) < 3).all(axis=1)]

            # We create a plot of the two fields. When the geofield is altitude, we want to plot the data on the x axis and the altitude on the y axis.
            if geo=="Altitude (km)":
                dataframe.plot(y=geo, x=data, kind='scatter', s=2.0, alpha=0.003, title=dataname+" as a function of "+geoname)
            else:
                dataframe.plot(x=geo, y=data, kind='scatter', s=2.0, alpha=0.003, title=dataname+" as a function of "+geoname)

            # We turn the plot into a figure
            f = plt.gcf()
            # We make the figure big
            f.set_figwidth(20)
            f.set_figheight(15)
            # We save the figure
            f.savefig(filename+"_"+dataname+"_"+geoname+".png")
