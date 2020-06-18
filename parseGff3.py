#!/usr/bin/env python3

import sys
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--gff3", help="Name of gff3 file to parse the CDS information from")
parser.add_argument("--cds", help="Set the minimum number of CDS regions required for a gene to be accepted", default=1)
parser.add_argument("--min_cds_length", help="Set the minimum length for any single CDS region", default=1)
parser.add_argument("-v", "--verbose", help="Print additional information about identified genes to STDOUT", action="store_true")
args = parser.parse_args()

# Create a dictionary to store the gene objects in.
gene_dict = {}
pacid_to_name = {}

class Gene(object):
	def __init__(self):
		self.CDS_count = 0
		self.CDS_length_list = []
		self.start_pos = 0
		self.stop_pos = 0

	def set_name(self, name):
		self.name = name

	def set_pacid(self, pacid):
		self.pacid = pacid

	def set_parent(self, parent):
		self.parent = parent

	def set_exon(self, start, stop):
		self.exon_list
	
	def add_CDS(self, start, stop):
		length = int(stop) - int(start)
		self.CDS_length_list.append(length)
		# Check if start position of the CDS has been set
		if self.start_pos == 0:
			self.start_pos = start
#		self.CDS_count += 1

	def get_CDS_count(self):
#		return int(self.CDS_count)
		return len(self.CDS_length_list)
	
	def get_CDS_length(self):
		return sum(self.CDS_length_list)

	def get_name(self):
		return self.name

	def get_pacid(self):
		return self.pacid
	
	def get_parent(self):
		return self.parent
	
	# Return length of shortest CDS
	def get_min_CDS_length(self):
		return min(self.CDS_length_list)

	def __str__(self):
		return self.name + ": " + str(self.CDS_length_list) + str(len(self.CDS_length_list))

def parse_gff3():
	# Parse a Phytozome.net gff3 file.
	gff3_file = open(args.gff3, "r")

	for line in gff3_file.readlines():
		if line[0] == "#":
			continue

		# Identify the name of the loci
		if line.split()[2] == "mRNA":
			
			# Instantiate a new gene object
			new_gene = Gene()

			lables = line.split()[8].split(";")
			for lable in lables:
				if lable.split("=")[0] == "Parent":
					new_gene.set_parent(lable.split("=")[1])
					continue
				elif lable.split("=")[0] == "Name":
					new_gene.set_name(lable.split("=")[1])
					continue
				elif lable.split("=")[0] == "ID":
					new_gene.set_pacid(lable.split("=")[1])
					continue
				
				gene_dict[new_gene.get_pacid()] = new_gene
				pacid_to_name[new_gene.get_pacid()] = new_gene.get_name()


		# Identify CDS'es and store info. in the correct Gene object.
		if line.split()[2] == "CDS":
			lables = line.split()[8].split(";")
			
			for lable in lables:
				if lable.split("=")[0] == "Parent":
					pacid = lable.split("=")[1]
					start = line.split()[3]
					stop = line.split()[4]
					gene_dict[pacid].add_CDS(start, stop)
					

	
	# Only print column names once
	first = True
	
	for gene in gene_dict:
		if int(gene_dict[gene].get_CDS_count()) >= int(args.cds) and gene_dict[gene].get_min_CDS_length() >= int(args.min_cds_length):
			if args.verbose == False:
				print(gene_dict[gene].get_name())
			#	print(gene_dict[gene].get_CDS_count())			# Devel.
			else:
				while first:
					print("# Pacid	Name	Nr._CDS	Total_CDS_length	Min._CDS_length")
					first = False
				print(gene_dict[gene].get_pacid(), gene_dict[gene].get_name(), gene_dict[gene].get_CDS_count(), gene_dict[gene].get_CDS_length(), gene_dict[gene].get_min_CDS_length())


if __name__ == "__main__":
	if args.gff3:
		parse_gff3()
