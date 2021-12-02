import pandas as pd

filelist = ["BACK","DAWS", "ESKI", "FSIM", "MCMU","PINA", "RANK", "TALO", "CONT","FCHU", "FSMI", "GILL", "ISLL", "RABB"]

# Combine first 200 rows for all the csv files into one excel file with multiple sheets
with pd.ExcelWriter("First200Rows.xlsx") as writer:
    for file in filelist:
        database = pd.read_csv(file + ".csv",
                               dtype={"X": 'float', "Y": 'float', "Z": 'float'}, nrows=200)
        database.to_excel(writer, sheet_name=file)
