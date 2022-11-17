#!/usr/bin/env python3
''' Command-line execution '''

import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'FAAUTeC'))
import FAAUTeCMain
import argparse

class CLI():

    def __init__(self):
        self.client()

    def client(self):

        parser = argparse.ArgumentParser(description="FAAUTeC v.0.2")
        parser._action_groups.pop()
        required = parser.add_argument_group('required arguments')
        optional = parser.add_argument_group('optional arguments')


        ### REQUIRED ###
        required.add_argument('-a',
                            '--alignment', type=str, 
                            help='absolute path to infile; infile in PHYLIP or FASTA format; Example: /path_to_input/test.phy',
                            required=True)

        required.add_argument('-c',
                            '--constraint', type=str, 
                            help='absolute path to constraint file; infile in NEWICK format; Example: /path_to_input/tree.tre',
                            required=True)

        ### OPTIONAL ###

        optional.add_argument('--model', type=str, 
                            help='(Optional) Model for RAxML',
                            default="GTRGAMMAI",
                            required=False)

        optional.add_argument('--ml_inference', type=str, 
                             help="(Optional) Choose which program should run the ML-Tree calculation 'RAxML' or 'IQTree'",
                             default='RAxML',
                             required=False)

        optional.add_argument('--path_iqtree', type=str, 
                            help='(Optional) absolute path to the iqtree executable',
                            default="iqtree",
                            required=False)

        optional.add_argument('--path_raxml', type=str, 
                            help='(Optional) absolute path to the raxml executable',
                            default="raxmlHPC",
                            required=False)

        optional.add_argument('--au_inference', type=str, 
                             help="(Optional) Choose program for AU-test calculation 'CONSEL' or 'IQTree' or 'IQTree2', multiple selection possible by ';' as delimiter, e.g. 'CONSEL;IQTree'",
                             default='CONSEL',
                             required=False)

        optional.add_argument('--path_consel', type=str, 
                              help='(Optional) path to consel executables',
                              required=False)

        optional.add_argument('--path_iqtree2', type=str, 
                            help='(Optional) absolute path to the iqtree2 executable',
                            default=False,
                            required=False)

        optional.add_argument('--alpha_level', type=float, 
                             help="(Optional) Choose alpha level below which a differences is marked as significant",
                             default='0.05',
                             required=False)

        optional.add_argument('--outgroup', 
                            help='(Optional) name of a sequence of the input alignment to be used as the outgroup',
                            default=False,
                            required=False)

        optional.add_argument('--latex_format',
                             help='(Optional) Shall output table also be saved in LaTeX format?',
                             default=False,
                             action='store_true',
                             required=False)

        optional.add_argument('--thread_number', type=int, 
                             help="(Optional) Number of maximal used threads",
                             default='1',
                             required=False)

        args = parser.parse_args()

        FAAUTeCMain.faautec(args.alignment,
                            args.constraint,
                            args.path_consel,
                            args.model,
                            args.ml_inference,
                            args.au_inference,
                            args.thread_number,
                            args.path_iqtree2,
                            args.path_iqtree,
                            args.path_raxml,
                            args.alpha_level,
                            args.outgroup,
                            args.latex_format)


def start_faautec():
    CLI()
