#!/usr/bin/env python

import sys
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--gff3", help="Name of gff3 file to parse for information of exons")
parser.add_argument("--exons", help="Set the minimum number of exons required for a gene to be accepted", default=1)
parser.add_argument("-v", "--verbose", help="Print additional information about identified genes to STDOUT", action="store_true")
args = parser.parse_args()

# Create a dictionary to store the gene objects in.
gene_dict = {}
pacid_to_name = {}

class Gene(object):
	def __init__(self):
		self.CDS_count = 0

	def set_name(self, name):
		self.name = name

	def set_pacid(self, pacid):
		self.pacid = pacid

	def set_parent(self, parent):
		self.parent = parent

	def set_exon(self, start, stop):
		self.exon_list
	
	def add_CDS(self):
		self.CDS_count += 1

	def get_CDS_count(self):
		return int(self.CDS_count)

	def get_name(self):
		return self.name

	def get_pacid(self):
		return self.pacid
	
	def get_parent(self):
		return self.parent

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
	#		new_gene.set_parent(line.split()[8].split(";")[4].split("Parent=")[1])
			new_gene.set_name(line.split()[8].split(";")[1].split("Name=")[1])
			new_gene.set_pacid(line.split()[8].split(";")[2].split("pacid=")[1])
			gene_dict[new_gene.get_pacid()] = new_gene
			pacid_to_name[new_gene.get_pacid()] = new_gene.get_name()
		
		# Identify CDS'es and store info. in the correct Gene object.
		if line.split()[2] == "CDS":
			pacid = line.split()[8].split(";")[2].split("pacid=")[1]
			gene_dict[pacid].add_CDS()
	
	# Only print column names once
	first = True
	
	for gene in gene_dict:
		if int(gene_dict[gene].get_CDS_count()) >= int(args.exons):
			if args.verbose == False:
				print gene_dict[gene].get_name()
			else:
				while first:
					print "# Pacid	Name	Nr. exons"
					first = False
				print gene_dict[gene].get_pacid(), gene_dict[gene].get_name(), gene_dict[gene].get_CDS_count()


if __name__ == "__main__":
	if args.gff3:
		parse_gff3()
