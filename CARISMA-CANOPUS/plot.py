import pandas as pd
import matplotlib.pyplot as plt
import random
import seaborn as sns
import img2pdf
import glob
flist = ["BACK","DAWS", "ESKI", "FSIM", "MCMU","PINA", "RANK", "TALO", "CONT","FCHU", "FSMI", "GILL", "ISLL", "RABB"]

# plt.figure(figsize=(20, 15))
summary = ""
for file in flist:
    plt.figure(figsize=(20, 15))
    print("Working for "+file+".")
    # We load in the summary file, which takes a while
    n = sum(1 for line in open(file+".csv")) - 1  # number of records in file (excludes header)
    s = 100000  # desired sample size
    skip = sorted(random.sample(range(1, n + 1), n - s))  # the 0-indexed header will not be included in the skip list
    database = pd.read_csv(file+".csv",
        dtype={"X": 'float', "Y": 'float', "Z": 'float'}, skiprows=skip)

    database[database.columns.values.tolist()[0]] = pd.to_datetime(database[database.columns.values.tolist()[0]])
    database[database.columns.values.tolist()[1]] = pd.to_datetime(database[database.columns.values.tolist()[1]])
    print("Done loading csv")
    print(database.describe())
    print(database.dtypes)

    summary = summary+file+" Summary: \n"+database.describe().to_string()+"\n\n"
    ax1 = database.plot(kind="scatter", y="X", x=database.columns.values.tolist()[0], color='b', label="X", alpha=0.2)
    database.plot(kind='scatter', y='Y', x=database.columns.values.tolist()[0], color='r', ax=ax1, label="Y", alpha=0.2)
    database.plot(kind='scatter', y='Z', x=database.columns.values.tolist()[0], color='g', ax=ax1, label="Z", alpha=0.2)
    ax1.set_ylabel("X, Y and Z readings of Earth's magnetic field (nT)")
    plt.title(file+" Site: X, Y and Z readings of Earth's magnetic field vs Date")
    plt.savefig("Plots/"+file+"Date.png")
    ax2 = database.plot(kind="scatter", y="X", x=database.columns.values.tolist()[1], color='b', label="X", alpha=0.2)
    database.plot(kind='scatter', y='Y', x=database.columns.values.tolist()[1], color='r', ax=ax2, label="Y", alpha=0.2)
    database.plot(kind='scatter', y='Z', x=database.columns.values.tolist()[1], color='g', ax=ax2, label="Z", alpha=0.2)
    ax2.set_ylabel("X, Y and Z readings of Earth's magnetic field (nT)")
    ax2.set_xlabel("Date")
    plt.title(file+" Site: X, Y and Z readings of Earth's magnetic field vs Time of Day")
    plt.savefig("Plots/" + file + "Time.png")
    ax3 = database.plot(kind="scatter", y="Y", x="X", alpha=0.1)
    ax3.set_ylabel("Y readings of Earth's magnetic field (nT)")
    ax3.set_xlabel("X readings of Earth's magnetic field (nT)")
    plt.title(file+" Site: Y vs X readings of Earth's magnetic field")
    plt.savefig("Plots/" + file + "YvsX.png")
    ax4 = database.plot(kind="scatter", y="Z", x="X", alpha=0.1)
    ax4.set_ylabel("Z readings of Earth's magnetic field (nT)")
    ax4.set_xlabel("X readings of Earth's magnetic field (nT)")
    plt.title(file+" Site: Z vs X readings of Earth's magnetic field")
    plt.savefig("Plots/" + file + "ZvsX.png")
    pplot = sns.pairplot(database)
    fig = pplot.fig
    fig.suptitle(file+" Site: pairplot", x=0.55)
    fig.savefig("Plots/"+file+"pairplot.png")


f = open("Plots/Summary.txt", "w")
f.write(summary)
f.close()
images = []
for name in glob.glob('Plots/'+"*"+".png"):
    print(name)
    images.append(name)
with open("ExamplePlots.pdf", "wb") as f:
    f.write(img2pdf.convert(images))



