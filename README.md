# Introduction
This repository describes a method for finding useful gene sequences to use for developing target capture (a.k.a. sequence capture) probes for DNA sequencing. The idea is that these probes will be general enough to capture DNA molecules from several different species, and that the sequences can be used for e.g. phylogenetic analysis of species from a family, order or a group at some other taxonomic level.

## The data
The first part of your analysis should be to familiarise yourself with the input data you'll use for designing the probes. I imagine you will have one or two transcriptome datasets from your ingroup and perhaps an annotated whole genome dataset from a related organism.

![Data](images/1.png)

In this figure we see the phylogenetic relationship between the two species from where we have transcriptome data (Tr.1 and Tr.2) and one species with an annotated reference genome (or Whole Genome Sequence dataset [WGS]). The number of species from which WGS data is available is rather limited, but a species from the same family or order as your ingroup taxa will most likely be sufficient. 

![Best case scenario](images/2.png)
![Reality](images/3.png)

## Basic work flow
A more comprehensive description of the steps involved in this analysis can be find in [Sequence_capture.pdf](./Sequence_capture.pdf). The aim of this type of analysis is to find transcriptome sequences that can be used to design capture probes. To that end, we identify transcriptome sequences (in practice the exon sequences of genes) that are conserved within a phylogenetic clade, and that hopefully contain intron sequences with enough phylogenetically informative sites that we will be able to resolve the relationships in our group of interest (here called the ingroup). Since the transcriptome data often originates from cDNA generated from mRNA, where the intron sequences have been spliced out, we don\'t know how many variable intron regions we can expect from just analysing the transcriptome data. However, the annotated reference genome will provide information on the gene models (UTRs, introns, exons etc.) that can be incorporated into our analysis.

![Venn diagram](images/4.png)

The area in the Venn diagram where all three circles overlap indicates part of the sequence space (i.e. all available sequences) where the transcriptome sequences are conserved (and therefore similar) and the genes they originate from have the desired number of introns. The required level of similarity and number of introns are for you to decide after the first iteration of this analysis. You will most likely want to go back and redo some steps in order to end up with a sufficient number of reference transcripts to use as templates for your capture probes.

## 1. Identify low copy gene sequences in transcriptome 1
This part of the analysis is conducted using `BLAST` on the command line. How `BLAST` works is out of the scope of this tutorial, but I suggest you read up on the [on-line manual](https://www.ncbi.nlm.nih.gov/books/NBK279680/) before you start. An example command might looks like this:

First, format the `BLAST` databases needed for this analysis:

```bash
makeblastdb -in example_data/transcriptome1.fst -dbtype nucl
makeblastdb -in example_data/transcriptome2.fst -dbtype nucl
makeblastdb -in example_data/Rcommunis_119_v0.1.transcript.fa -dbtype nucl
```


```bash
blastn -query $INPUT -db $DB -max_target_seqs 2 -outfmt 7 -out $OUT -num_threads $NSLOTS
```
where `$INPUT` and `$DB` should be replaced with the input file in fasta format and a `BLAST` database of the same data (remember, you are blasting transcriptome 1 to itself). `$OUT` should indicate the name of the output file and `$NSLOTS` the number of CPU cores to use (the `-num_threads $NSLOTS` command is optional but can significantly speed up your analysis if you're analysing a large transcriptome and have a system with several CPU cores). Important to include is the command `-outfmt 7` which determines the output format for `BLAST`. Here we are using the tab-delimited format, which makes it easier to analyse the result afterwards. An example of what the output will look like can be found below:

```blast
# BLASTN 2.3.0+
# Query: scaffold-CKDK-2001401-Ochna_serrulata
# Database: Ochna_serrulata_transcriptome_300.fst
# Fields: query id, subject id, % identity, alignment length, mismatches, gap opens, q. start, q. end, s. start, s. end, evalue, bit score
# 1 hits found
scaffold-CKDK-2001401-Ochna_serrulata	scaffold-CKDK-2001401-Ochna_serrulata	100.000	300	0	0	1	300	1	300	9.42e-157	551
```

An example output file can also be found [here](example_data/transcriptome_to_self.BLASTn.txt). `BLAST` matches including the line `# 1 hits found` indicate sequences that (given the settings used for the `BLAST` search) did not have any good matches in the data set, except matches to them self. This is a good indication that these sequences are from single- or low copy genes, and hence what we are looking for. Later on we might want to consider other sequences with poor matches (also indications of low- single copy genes).

You can extract the interesting `BLAST` matches and save them in a new file like this:

```blast
grep -A1 "# 1 hits found" example_data/transcriptome1_to_self.BLASTn.txt > example_data/low_copy_sequences.BLASTn.txt
```

The newly created file `low_copy_sequences.BLASTn.txt` now contains information about the `BLAST` matches of the low copy genes. We need to extract the sequence names for the next step, and we can do that like this:

```blast
cut -f1 example_data/low_copy_sequences.BLASTn.txt | grep -v "\-\-" | grep -v "#" > example_data/low_copy_names.txt
```
This command may look complicated, so I suggest you explore the manual pages for the included sub-commands to learn more (`man cut` and `man grep`).

We now have the names of the (presumed) low copy genes in transcriptome 1 stored in the file `low_copy_names.txt`. We can use this file to extract the DNA sequences using the program `fp.py` available for download [here](https://github.com/topel-research-group/misc).

```blast
fp.py --grep example_data/low_copy_names.txt example_data/transcriptome1.fst > example_data/low_copy_sequences.fst
```
The extracted sequences are automatically saved to the file `example_data/low_copy_sequences.fst`, and the first part of the analysis is finished. It's important to continuously examine the content of the output files in each step, to make sure your commands produce the expected output, and that you find a sufficient amount of low copy sequences.

## 2. Make sure the identified sequences in transcriptome 2 are single copy.
At this stage we could in principle make the assumption that single copy genes in species 1 (from which we got transcriptome 1) are also single copy genes in species 2. However, to be on the safe side, it's better to explicitly test this assumption for species 2 as we did above for species 1.

## 3. Find the homologous sequences in transcriptome 2
In this part of the analysis you will use your newly identified (presumed) low-copy genes to query the second transcriptome, in order to identify similar (and hopefully homologous) sequences. Here it is worth noting the difference between homology (e.g. shared ancestry) and similarity. The former often leads to the latter but this is not necessarily always the case. Still, since we can only infer homology, we will use similarity as a proxy. 

Use the sequences in `low_copy_sequences.fst` to query the sequence database containing the second transcriptome:

```bash
blastn -query example_data/low_copy_sequences.fst -db example_data/transcriptome2.fst -outfmt '7 std qlen slen' -out example_data/transcriptome1_to_transcriptome2.txt -num_threads $NSLOTS
```
Note that the output format sub-command has a few additional arguments (`std qlen slen`). These can be included in the first `BLAST` command as well but are particularly important for this second `BLAST` analysis, instructing the program to include the standard output (`std`), the length of the query sequence (`qlen`) and the subject sequence length (`slen`). We can now use this additional output data to identify homologous sequences that fulfil the selection criteria we will decide on next.

A first analysis of the blast result can look like this:

```bash
parseBLASTtable.py -q 100 -i example_data/transcriptome1_to_transcriptome2.txt | wc -l
	2720
```
The command will not display the actual `BLAST` result, only count the number of matches that fulfil the criteria we have set, and in this case we are looking for matches where the query sequence is >=100 bp (indicated by the `-q 100` option). The `parseBLASTtable.py` program (available for download [here](https://github.com/topel-research-group/misc)) has many more options to choose from, in order to select sequences useful for sequence capture probes. It's a good idea to play around with the different options to see which criteria have an effect on the number of identified sequences. A final combination of options may look something like this:

```bash
parseBLASTtable.py -q 100 -s 100 -% 80 -i example_data/transcriptome1_to_transcriptome2.txt > example_data/conserved_single_copy_genes.txt
```
The file `example_data/conserved_single_copy_genes.txt` now contains information on 2117 genes that are presumed single-copy and conserved in both species from which we have transcriptome data. To further filter our dataset, we could continue comparing our selection to additional transcriptome datasets by extracting the gene names using `cut` and then obtaining the sequences using `fp.py`. The exact steps you take here will depend on the data you have available.

Extract the conserved singe-copy genes from transcriptome 1 and use them to design your capture baits, or optionally, do the last step of this tutorial and include information from an annotated reference genome in your analysis.

```bash
fp.py --grep example_data/conserved_single_copy_genes.txt example_data/transcriptome1.fst > example_data/conserved_single_copy_genes_transcript1.fst
```

## 4. [Optional] Extract gene structure data from a WGS dataset (number of exons, length of introns, copy number, ...)
So far we have been looking for conserved DNA regions that are suitable templates for capture probes. If conserved regions are used, that means we can use these probes for capturing DNA from a whole group of species. At the same time, for a phylogenetic analysis, we would also like to capture variable regions that carry a phylogenetic signal. One assumption we make is that exons (which often make up the majority of the transcript sequences [cf. UTRs]) are more conserved than intron regions. By designing probes for the exon sequences, we get general enough probes that work on many species, while at the same time capturing the more variable intron sequences that will give us phylogenetic resolution. Therefore, the more introns a particular gene includes, the more signal we will capture. From the transcript data it is difficult, or impossible, to get information about the intron/exon structure of the genes we analyse. However, for well-studied and annotated model organisms it is possible to get this information, and if the intron/exon structure is conserved in the group we are analysing, we can infer this for our transcriptomes.

In this example we can use the reference genome of _Ricinus communis_ available from [www.phytozome.jgi.doe.gov](https://phytozome.jgi.doe.gov/pz/portal.html#!info?alias=Org_Rcommunis). 

In the example below we are identifying the genes in the _Ricinus communis_ reference genome which consist of at least three exons (`--cds 3`), where each exon is at least 50 bp long (`--min_cds_length 50`).

```bash
parseGff3.py --gff3 example_data/Rcommunis_119_v0.1.gene.gff3 --cds 3 --min_cds_length 50 > example_data/Rcommunis_cds3_50bp_names.txt
```
(`parseGff3.py` available in this repository)

Then we use these names to extract the sequences from the transcriptome.

```bash
fp.py --grep example_data/Rcommunis_cds3_50bp_names.txt example_data/Rcommunis_119_v0.1.transcript.fa > example_data/Rcommunis_cds3_50bp_transcript.fst
```
Final steps in this analysis include identifying which sequences in `conserved_single_copy_genes_transcript1.fst` have a good `BLAST` match to the identified _Ricinus communis_ sequences, and then extracting only those sequences to a file.

```bash
blastn -query example_data/conserved_single_copy_genes_transcript1.fst -db example_data/Rcommunis_119_v0.1.transcript.fa -outfmt '7 std qlen slen' -out example_data/transcript1_to_Rcommunis.txt -num_threads $NSLOTS
```

```bash
parseBLASTtable.py -q 100 -s 100 -% 80 -i example_data/transcript1_to_Rcommunis.txt > example_data/bait_sequences_names.txt
```

```bash
fp.py --grep example_data/bait_sequences_names.txt example_data/conserved_single_copy_genes_transcript1.fst > example_data/bait_sequences.fasta
```

In this example, the file `bait_sequences.fasta` contains 946 sequences from transcriptome 1 that we assume are 1.) single-copy, 2.) conserved across the clade we are analysing, 3.) contain at least two introns (sitting between the three or more exons we identified in _Ricinus communis_), and 4.) contain exon sequences that are around 50 bp or longer.

Depending on the data you are analysing, you might want to go back and redo some of the steps above, if for example you end up with too few, or too many sequences to base your baits on.
