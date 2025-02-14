#!/usr/bin/env python3.7
''' Main operation of FAAUTeC '''

import os
import sys
import time
import dendropy

import IOOps as IOOps
import FAAUTeCOps as FOps
import CheckOps as COps

def faautec(alignment,
            constraint_path,
            consel_path,
            model,
            mlcalc,
            au_inference,
            threadNumber,
            iqtree2_path,
            iqtree_path,
            raxml_path,
            alpha_level,
            outgroup,
            latex):

    if(not COps.checkPrerequisites(au_inference, iqtree2_path, consel_path, mlcalc)):
        sys.exit()

    overallLog = ["alignment: " + str(alignment),
                  "constraint_path: " + str(constraint_path),
                  "consel_path: " + str(consel_path),
                  "model: " + str(model),
                  "ml_inference: " + str(mlcalc),
                  "au_inference: " + str(au_inference),
                  "threadNumber: " + str(threadNumber),
                  "iqtree2_path: " + str(iqtree2_path),
                  "iqtree_path: " + str(iqtree_path),
                  "raxml_path: " + str(raxml_path),
                  "alpha_level:" + str(alpha_level),
                  "outgroup:" + str(outgroup),
                  "latex: " + str(latex)]

    FOps.commandline("mkdir output/")
    FOps.commandline("mkdir output/SUMMARY")

    constraints = FOps.readConstraints(constraint_path)
    place = ["hypo" + str(i) for i in range(len(constraints))]
    programs = au_inference.split(";")
    raxmlVersion = "standard"

    if(mlcalc == "RAxML" or "CONSEL" in programs):
        raxmlVersionNumber, raxmlVersion = COps.checkRAxMLVersion(raxml_path)
        if(not raxmlVersionNumber):
            print("The RAxML version: '" + raxml_path + "' is not supported")
            sys.exit()
        overallLog.append("RAxML Version: " + raxmlVersionNumber)

    if(mlcalc == "IQTree" or "IQTree" in programs):
        iqtreeVersionNumber = COps.checkIQTreeVersion(iqtree_path)
        if(not iqtreeVersionNumber):
            print("The IQTree version: '" + iqtree_path + "' is not supported")
            sys.exit()
        overallLog.append("IQTree Version: " + iqtreeVersionNumber)

    if("IQTree2" in programs):
        iqtreeVersionNumber = COps.checkIQTreeVersion(iqtree2_path)
        if(not iqtreeVersionNumber):
            print("The IQTree version: '" + iqtree2_path + "' is not supported")
            sys.exit()
        overallLog.append("IQTree2 Version: " + iqtreeVersionNumber)

    with open("output/SUMMARY/log.txt","w") as logFile:
        for line in overallLog:
            logFile.write(line + "\n")

    treeFile = open("output/SUMMARY/raxml_hypoTreeShortestDistUnconstTree.tre","w")
    auFile = open("output/SUMMARY/au_runtime_table.csv","w")

    auFile.write("gene," + ','.join([','.join([program + "_hypo" + str(i) for program in programs]) for i in range(len(constraints))]) + "," + ','.join(["runtime_" + program for program in programs]) + "\n")

    au_values = {}
    runtimes = {}

    alis = [i for i in os.listdir(alignment) if i.split(".")[-1]=="fasta" or i.split(".")[-1]=="fa" or i.split(".")[-1]=="phy" or i.split(".")[-1]=="nex"]

    colored = 0
    for ali in alis:
        print(ali)
        gene = ali.split(".")[0]
        ali = alignment + ali.strip()
        if ali.split(".")[-1] == "fasta" or ali.split(".")[-1] == "fa":
            pass
        elif ali.split(".")[-1] == "phy":
            ali = IOOps.Inp().phylip2fasta(ali)
        elif ali.split(".")[-1] == "nex":
            ali = IOOps.Inp().nexus2fasta(ali)
        else:
            print(ali + " was skipped because the file ending is not supported. Supported File endings: 'fasta', 'nex', 'phy'")
            continue

        COps.checkAlignmentFile(ali)

        log = ["#!/bin/bash", "# " + gene]

        ### Create a clear file system
        os.mkdir("output/" + gene)
        os.mkdir("output/" + gene + "/01_input")
        os.mkdir("output/" + gene + "/02_output_" + mlcalc)

        if("CONSEL" in programs):
            os.mkdir("output/" + gene + "/03a_output_CONSEL")

        if("IQTree" in programs):
            os.mkdir("output/" + gene + "/03b_output_IQTree")

        if("IQTree2" in programs):
            log.append(FOps.commandline("mkdir output/" + gene + "/03c_output_IQTree2"))

        log.append(FOps.commandline("cp " + ali + " output/" + gene + "/01_input/"))

        if(mlcalc == "RAxML"):
            log = log + ["\n",
                        "# Calculate ML-Trees with RAxML"]

            ### Calculate the ML-Trees with RAxML
            log = log + FOps.raxml(ali, constraints, model, gene, outgroup, str(threadNumber), raxml_path, raxmlVersion)

            ### Find Tree which has the smallest euclidic distance to
            ### to the unconstraint tree
            trees = []
            with open(gene + '_COMBINED.tre', "r") as multitree:
                for tree in multitree:
                    trees.append(tree.strip())
            best_tree = FOps.findBestTree(trees)
            trees = trees[1:]

            log.append(FOps.commandline("mv RAxML_* output/" + gene + "/02_output_RAxML/"))

        elif(mlcalc == "IQTree"):
            log = log + ["\n",
                        "# Calculate ML-Trees with IQTree"]

            ### Calculate the ML-Trees with IQTree
            log = log + FOps.iqtree_mltree(ali, constraints, gene, str(threadNumber),iqtree_path)

            ### Find Tree which has the smallest euclidic distance to
            ### to the unconstraint tree
            trees = []
            with open(gene + '_COMBINED.tre', "r") as multitree:
                for tree in multitree:
                    trees.append(tree.strip())
            best_tree = FOps.findBestTree(trees)
            trees = trees[1:]

            log.append(FOps.commandline("mv " + gene + "_IQTree* output/" + gene + "/02_output_IQTree/"))

        else:
            print("Error: The Program " + mlcalc + " is not supported to run ML Tree calculation use" +
                  " 'RAxML' or 'IQTree' instead.")
            break

        ## write the best tree to the best tree file
        treeFile.write(gene + place[best_tree] + " " + trees[best_tree])

        ### AU Test by CONSEL
        if("CONSEL" in programs):
            print("AU Test by CONSEL")
            log = log + ["\n",
                        "# Calculate AU-Test with CONSEL"]

            start = time.time()
            log = log + FOps.consel(ali, consel_path, model, gene, mlcalc, str(threadNumber), raxml_path, raxmlVersion)
            runtimes.update({"CONSEL":round(time.time() - start,3)})

            ## Save the AU Test values to a variable
            au_consel = [0] * (len(constraints) + 1)
            with open(gene + "_CONSEL.consel") as consel:
                for line in consel.readlines()[3:len(constraints)+4]:
                    au_consel[int(line.split()[2]) - 1] = float(line.split()[4])
            au_consel = au_consel[1:]

            ## mark values below significance level
            for i in range(len(au_consel)):
                if au_consel[i] <= alpha_level:
                    au_consel[i] = str(au_consel[i]) + "*"

            ## mark the tree with the smallest euclidic distance
            au_consel[best_tree] = str(au_consel[best_tree]) + "s"

            au_values.update({"CONSEL":au_consel})


            log.append(FOps.commandline("mv " + gene + "_CONSEL* output/" + gene + "/03a_output_CONSEL/"))
            log.append(FOps.commandline("mv RAxML* output/" + gene + "/03a_output_CONSEL/"))

        # AU Test by IQTree
        if("IQTree" in programs):
            print("AU Test by IQTree")
            log = log + ["\n",
                        "# Calculate AU-Test with IQTree"]
            start = time.time()
            log = log + FOps.iqtree_autest(ali, iqtree_path, gene, mlcalc, str(threadNumber), raxmlVersion)
            runtimes.update({"IQTree":round(time.time() - start,3)})

            au_iqtree = []
            with open(gene + "_IQTree.iqtree","r") as iqtree_out:
                for line in iqtree_out:
                    if line.strip() == "-------------------------------------------------------------------------":
                        break
                    else:
                        pass
                for line in iqtree_out:
                    try:
                        au_iqtree.append(float(line.split()[11]))
                    except:
                        break
            au_iqtree = au_iqtree[1:]

            ## mark values below significance level
            for i in range(len(au_iqtree)):
                if au_iqtree[i] <= alpha_level:
                    au_iqtree[i] = str(au_iqtree[i]) + "*"

            ## mark the tree with the smallest euclidic distance
            au_iqtree[best_tree] = str(au_iqtree[best_tree]) + "s"

            au_values.update({"IQTree":au_iqtree})

            log.append(FOps.commandline("mv " + gene + "_IQTree* output/" + gene + "/03b_output_IQTree/"))


        # AU Test by IQTree2
        if("IQTree2" in programs):
            print("AU Test by IQTree2")
            log = log + ["\n",
                         "# Calculate AU-Test with IQTree"]
            start = time.time()
            log = log + FOps.iqtree_autest(ali, iqtree2_path, gene, mlcalc, str(threadNumber), raxmlVersion)
            runtimes.update({"IQTree2":round(time.time() - start,3)})

            au_iqtree2 = []
            with open(gene + "_IQTree.iqtree","r") as iqtree2_out:
                for line in iqtree2_out:
                    if line.strip() == "-------------------------------------------------------------------------":
                        break
                    else:
                        pass
                for line in iqtree2_out:
                    try:
                        au_iqtree2.append(float(line.split()[11]))
                    except:
                        break
            au_iqtree2 = au_iqtree2[1:]

            ## mark values below significance level
            for i in range(len(au_iqtree2)):
                if au_iqtree2[i] <= alpha_level:
                    au_iqtree2[i] = str(au_iqtree2[i]) + "*"

            ## mark the tree with the smallest euclidic distance
            au_iqtree2[best_tree] = str(au_iqtree2[best_tree]) + "s"

            au_values.update({"IQTree2":au_iqtree2})

            log.append(FOps.commandline("mv " + gene + "_IQTree* output/" + gene + "/03c_output_IQTree2/"))


        auFile.write(gene + ''.join(["," + str(au_values[program][i]) for i in range(len(constraints)) for program in programs]) + ''.join(["," + str(runtimes[program]) for program in programs]) + "\n")

        colored = colored + 1

        with open("output/" + gene + "/" + gene + "_log.sh","w") as logFile:
            for line in log:
                logFile.write(line + "\n")

        os.remove(gene + "_COMBINED.tre")
        os.remove("hypo.txt")
        os.remove("hypo_rem.txt")
        print(str(colored) + " / " + str(int(len(alis))))


    treeFile.close()
    auFile.close()

    if(latex):
        IOOps.Outp().createLatex("output/SUMMARY/au_runtime_table.csv", latex)
