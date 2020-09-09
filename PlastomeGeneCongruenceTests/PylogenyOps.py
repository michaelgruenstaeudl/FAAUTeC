import os
import dendropy

def edit_num(value):
    value = str(value)
    value = value.replace("s","\\textsuperscript{s}").replace("*","\\textsuperscript{*}")
    if "*" in str(value):
        return "\\textbf{" + str(value) + "}"
    return value

def findBestTree(treeList):
    tns = dendropy.TaxonNamespace()
    rank = []
    unconst = dendropy.Tree.get_from_string(
            treeList[0],
            "newick",
            taxon_namespace=tns)
    unconst.encode_bipartitions()
    for tree in treeList[1:]:
        hypo = dendropy.Tree.get_from_string(
                tree,
                "newick",
                taxon_namespace=tns)
        hypo.encode_bipartitions()
        rank.append(dendropy.calculate.treecompare.euclidean_distance(unconst, hypo))
    return rank.index(min(rank))


def readConstraints(constraint_path):
    constraints_tmp = []

    ## put all constraint trees in one list
    with open(constraint_path) as constFile:
        for line in constFile:
            constraints_tmp.append(line.strip())
        constraints_tmp = ''.join(constraints_tmp).split(";")[:-1]

    ## deroot the trees
    constraints = []
    for const in constraints_tmp:
        tree = dendropy.Tree.get_from_string(const + ";", "newick")
        tree.deroot()
        constraints.append(tree)

    return constraints

def iqtree(alignment, gene_name):
    log = []
    #log.append(commandline("iqtree -s "+ alignment +" -m GTR+I+G -pre " + gene_name + "_IQTree_unconst -quiet"))

    #for i in range(len(constraints)):
    #    with open("hypo.txt","w") as hypo:
    #        hypo.write(constraints[i].as_string(schema="newick"))
    #    log.append(commandline("iqtree -s "+ alignment +" -m GTR+I+G -g hypo.txt -pre " + gene_name + "_IQTree_hypo" + str(i) + " -quiet"))
    #log.append(commandline("cat " + gene_name + "_IQTree_unconst.treefile " + ''.join([gene_name + "_IQTree_hypo" + str(i) + ".treefile " for i in range(len(constraints))]) + "> " + gene_name + "_COMBINED.tre"))
    log.append(commandline("iqtree -s "+ alignment +" -m GTR+I+G -z " + "RAxML_" + gene_name + "_COMBINED.tre -te RAxML_bestTree.withoutConstraints_" + gene_name + " -zb 10000 -au -pre " + gene_name + "_IQTree -quiet"))
    return log

def raxml(alignment, constraints, model, gene_name):
    log = []
    log.append(commandline("raxmlHPC -s " + alignment + " -n withoutConstraints_" + gene_name + " -m  " + model + " -p 10000 -w " + os.getcwd()) + " --silent")
    for i in range(len(constraints)):
        with open("hypo.txt","w") as hypo:
            hypo.write(constraints[i].as_string(schema="newick"))
        log.append(commandline("raxmlHPC -s " + alignment + " -n hypothesis" + str(i) + "_" + gene_name + " -m " + model + " -g hypo.txt -p 10000 -w " + os.getcwd()) + " --silent")

    log.append(commandline("cat RAxML_bestTree.withoutConstraints_" + gene_name + ''.join([" RAxML_bestTree.hypothesis" + str(i) + "_" + gene_name for i in range(len(constraints))]) + " > RAxML_" + gene_name + "_COMBINED.tre"))
    #log.append(commandline("cp RAxML_bestTree.withoutConstraints_" + gene_name + " test.tre"))
    return log

def consel(alignment, consel_path, model, gene_name):
    log = []

    log.append(commandline("raxmlHPC -s " + alignment + " -n " + gene_name + ".trees.sitelh -m "+ model + " -f g -t RAxML_bestTree.withoutConstraints_" + gene_name + " -z " + "RAxML_" + gene_name + "_COMBINED.tre -p 10000 -w " + os.getcwd()) + " --silent")
    log.append("\n## CONSEL")
    log.append(commandline("mv RAxML_perSiteLLs." + gene_name + ".trees.sitelh RAxML_perSiteLLs_" + gene_name + ".trees.sitelh"))
    log.append(commandline(consel_path + "/seqmt --puzzle RAxML_perSiteLLs_" + gene_name + ".trees.sitelh " + gene_name + "_CONSEL.mt"))
    log.append(commandline(consel_path + "/makermt " + gene_name + "_CONSEL.mt"))
    log.append(commandline(consel_path + "/consel " + gene_name + "_CONSEL.rmt"))
    log.append(commandline(consel_path + "/catpv " + gene_name + "_CONSEL.pv > " + gene_name + "_CONSEL.consel"))

    return log

def commandline(command):
    os.system(command)
    return command
