# Merge heads into a single file

# Clean up file
echo '## Starting lines of each file' > sample_from_all_files.txt

#Iterate over all files while appending
for FILE in ./*
do
	echo "#File name: $FILE" >> sample_from_all_files.txt
	head $FILE>> sample_from_all_files.txt
done
