#!/usr/bin/env python

# Identifies BLAST matches with an e-value > threshold value.
#
# Input: Expects an inputfile (blast table [-outfmt 7 or similar] 
# where only the two best maches have been saved.
# Output: Sequence idenfifiers from the BLAST file are printed 
# to STDOUT. One identifier per line.
#
# Usage: get_low_copy.py <BLAST_output-file.table> <value>
#
# Example: get_low_copy.py Antirrhinum_majus_est.BLAST.table 0.0001

import sys

file_name = sys.argv[1]
my_file = open(file_name, "r")

e_val_cutoff = sys.argv[2]

for line in my_file.readlines():
	if line[0] != "#":
		if float(line.split()[10]) != 0.0 and float(line.split()[10]) >= float(e_val_cutoff):
			print line.split()[0]
