
#Good and bad string:
#   Date(yyyy/mm/dd/yyyy),time(hh:mi:ss),X,Y,Z,F=. if the data is valid anything else the data is suspect.
#   # Date(dd/mm/yyyy),time(hh:mi:ss),X,Y,Z,F=. if the data is valid anything else the data is suspect.



##Create a test file
#head ISLL_UnderReview.csv > bad_header_for_testing.csv
#head ISLL_UnderReview.csv > bad2_header_for_testing.csv
#head ISLL_UnderReview.csv > bad3_header_for_testing.csv

#replace in tester file
#sed -i 's+# Date(dd/mm/yyyy)+Date(yyyy/mm/dd)+' bad_header_for_testing.csv

#Check file
#cat bad_header_for_testing.csv

#Apply to two test files
#find . -type f -name '*_header_for_testing.csv' -exec sed -i 's+# Date(dd/mm/yyyy)+Date(yyyy/mm/dd)+' {} \;

# Apply replacement to all files
find . -type f -name '*.csv' -exec sed -i 's+# Date(dd/mm/yyyy)+Date(yyyy/mm/dd)+' {} \;

# Clean up after sed
find . -type f -name 'sed0*' -exec rm {} \;
