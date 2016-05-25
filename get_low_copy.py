#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Identifies BLAST matches with an e-value > threshold value.
#
# Input: Expects an inputfile (blast table [-outfmt 7 or similar] 
# where only the two best maches have been saved.
# Output: Sequence idenfifiers from the BLAST file are printed 
# to STDOUT. One identifier per line.
#
# Usage: get_low_copy.py <BLAST_output-file.table> <value>
#
# Example: 	blastp -query Os.aa.fa -db Os.aa.fa -max_target_seqs 2 -outfmt 7 -out Os_2_Os.aa.BLAST.table
#			get_low_copy.py Antirrhinum_majus_est.BLAST.table 0.0001
#
#   Copyright (C) 2016 Mats Töpel. mats.topel@bioenv.gu.se
#
#   Citation: If you use this version of the program, please cite;
#   Mats Töpel (2016) Open Laboratory Notebook. www.matstopel.se
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#   
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sys

file_name = sys.argv[1]
my_file = open(file_name, "r")
e_val_cutoff = sys.argv[2]
result = []

for line in my_file.readlines():
	if line[0] != "#":
		# Disregard exact matches and then find matches with e-values greater then threshold value.
		if float(line.split()[10]) != 0.0 and float(line.split()[10]) >= float(e_val_cutoff):
			# Store result if not already in result list.
			if line.split()[0] not in result:
				result.append(line.split()[0])

for seq_id in result:
	print seq_id
