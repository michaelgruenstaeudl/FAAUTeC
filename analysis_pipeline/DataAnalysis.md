***
**Data analysis for my Master thesis**\
author: Yannick Hartmaring; improved by: Michael Gruenstaeudl, PhD
***


## Preparation
### Download and install FAAUTeC
```
git clone https://github.com/Yanjo96/FAAUTeC
cd FAAUTeC
python3 setup.py install
```


### Download prepare the Datasets
#### Goncalves Et Al 2019
https://www.sciencedirect.com/science/article/pii/S1055790318306602

1. Download the Data from here: https://github.com/deisejpg/rosids/tree/master/II_phylogenetic_analysis/data

2. Take the following constrained trees from the file `newick/`
  - iqtree_ge_concat.nwk
  - iqtree_ex_concat.nwk
  - iqtree_cd_concat.nwk

3. Remove all branch length with the following bash script
```
cat iqtree_cd_concat.nwk | sed 's/E-//g' | sed 's/[:.0-9]//g' > iqtree_cd_concat_wobl.nwk
cat iqtree_ex_concat.nwk | sed 's/E-//g' | sed 's/[:.0-9]//g' > iqtree_ex_concat_wobl.nwk
cat iqtree_ge_concat.nwk | sed 's/E-//g' | sed 's/[:.0-9]//g' > iqtree_ge_concat_wobl.nwk
```

#### Goncalves Et Al 2020
https://bsapubs.onlinelibrary.wiley.com/doi/abs/10.1002/ajb2.1502

1. download the data from here:\
https://datadryad.org/stash/dataset/doi:10.5061/dryad.sn02v6x1g

2. save the tree files in a seperate folder and remove all branch length with the removeBranchLength.py script from FAAUTeC
```
python3 /path/to/removeBranchLength.py -r / -t astral_bs_boot_apr2019.tre -o astral_bs_boot_apr2019_wobl.tre
python3 /path/to/removeBranchLength.py -r / -t iq_bs_besttree_boot_apr2019.tre -o iq_bs_besttree_boot_apr2019_wobl.tre
python3 /path/to/removeBranchLength.py -r / -t iq_gepart_besttree_boot_apr2019.tre -o iq_gepart_besttree_boot_apr2019_wobl.tre
python3 /path/to/removeBranchLength.py -r / -t iq_unpart_besttree_boot_apr2019.tre -o iq_unpart_besttree_boot_apr2019_wobl.tre
```

3. combine all wobl trees in one file and remember order in a new file called `combined_wobl.tre`
```
cat astral_bs_boot_apr2019_wobl.tre iq_bs_besttree_boot_apr2019_wobl.tre iq_gepart_besttree_boot_apr2019_wobl.tre iq_unpart_besttree_boot_apr2019_wobl.tre > combined_wobl.tre
```

## Execution of FAAUTeC
### Goncalves et. al (2019)
for each of the three matrices _gene_, _exon_ and _codon-aligned_
  1. Copy the alignment files in an empty folder (except the concatenated file)

  2. Run FAAUTeC with IQTree as tree inference software; rename output folder to `output_ge_iqtree`
  ```
  ALIGN=/path/to/dir_of_alignments_ge/
  CONST=/path/to/iqtree_ge_concat_wobl.nwk
  MLINF=IQTree
  AUINF=CONSEL;IQTree;IQTree2
  CONSL_DIR=/path/to/consel_bin_dir/
  IQTREE2=/path/to/iqtree2
  NTHREADS=4

  FAAUTeC -a $ALIGN -c $CONST --ml_inference $MLINF --au_inference $AUINF \
      --path_consel $CONSL_DIR --path_iqtree2 $IQTREE2 --thread_number $NTHREADS --latex_format
  mv output output_ge_iqtree
  ```
  3. Run FAAUTeC with RAxML (default) as tree inference software; rename output folder to `output_ge_raxml`
  ```
  FAAUTeC -a $ALIGN -c $CONST 
      --path_consel $CONSL_DIR --thread_number $NTHREADS
  mv output/ output_ge_raxml/
  ```
  4. Combine the output tables via script `combineTables.py`
  ```
  combineTables.py \
      -1 output_ge_iqtree/SUMMARY/au_runtime_table.csv \
      -2 output_ge_raxml/SUMMARY/au_runtime_table.csv \
      -o combined_ge.csv
  ```
  5. Manually remove the runtime information and change the names of the columns

  6. Afterwards, combine all output tables from _gene_, _exon_ and _codon-aligned_ in one table to handle them as hypotheses

#### Calculate the AU Test five times
```
CONSL="/path/to/consel"
IQTREE="iqtree"
IQTREE2="/path/to/iqtree2"
RAXML="raxmlHPC"
INPUT="/path/to/FAUUTeC/output"
NRUNS=5
NHYPOS=3
MLINF="RAxML"
python3 path/to/multi_AU.py $CONSL $IQTREE $IQTREE2 $RAXML $INPUT $NRUNS $NHYPOS $MLINF

MLINF="IQTree"
python3 path/to/multi_AU.py $CONSL $IQTREE $IQTREE2 $RAXML $INPUT $NRUNS $NHYPOS $MLINF
```
---------

### Goncalves et al 2020

1. run the program for IQTree
```
ALIGN=path_to_alignments_dir/
CONST=path_to_combined_wobl.tre
MLINF=IQTree
AUINF=CONSEL;IQTree;IQTree2
CONSL=path_to_consel_dir/
IQTREE2=/path/to/iqtree2
NTHREADS=4
FAAUTeC -a $ALIGN -c $CONST --ml_inference $MLINF --au_inference $AUINF --path_consel $CONSL --path_iqtree2 $IQTREE2 --thread_number $NTHREADS --latex_format
```
2. rename output folder
```
MLINF=RAxML
FAAUTeC -a $ALIGN -c $CONST --ml_inference $MLINF --au_inference $AUINF --path_consel $CONSL --path_iqtree2 $IQTREE2 --thread_number $NTHREADS --latex_format
```

#### Calculate the AU Test five times
```
CONSL="/path/to/consel"
IQTREE="iqtree"
IQTREE2="/path/to/iqtree2"
RAXML="raxmlHPC"
INPUT="/path/to/FAUUTeC/output"
NRUNS=5
NHYPOS=3
MLINF="RAxML"
python3 path/to/multi_AU.py $CONSL $IQTREE $IQTREE2 $RAXML $INPUT $NRUNS $NHYPOS $MLINF

MLINF="IQTree"
python3 path/to/multi_AU.py $CONSL $IQTREE $IQTREE2 $RAXML $INPUT $NRUNS $NHYPOS $MLINF
```

## Creating Plots
Execute the functions in `plots.R` to create the plots 
