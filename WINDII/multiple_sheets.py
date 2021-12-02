import pandas as pd
import glob

filelist = glob.glob("*.csv")
# Combine first 200 rows for all the csv files into one excel file with multiple sheets
with pd.ExcelWriter("First200Rows.xlsx") as writer:
    for file in filelist:
        database = pd.read_csv(file, nrows=200)
        database.to_excel(writer, sheet_name=file.split(".")[0])

