# TreeTopology
* Version: 0.1

## INSTALLATION
```
python3 setup.py install  # Installation
python3 setup.py test     # Testing
```

## Requirements
* RAxML (https://github.com/stamatak/standard-RAxML)
* CONSEL (https://github.com/shimo-lab/consel)
* IQTree (http://www.iqtree.org/)
* Python3
* Biopython
* Dendropy
* mmv

## USAGE
#### On Linux
```
ALIGN=examples/input/FASTA/
CONST=examples/input/Constraint/tree_hypothesis.txt
CONSL=path/to/consel

python3 scripts/treetopology_launcher_CLI.py -a $INPUT -c $CONST --consel $CONSL
```
