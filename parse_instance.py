#! /usr/bin/env python

# Copyright (C) 2016-2018
# Alexandra Carpen-Amarie

# changes made by Sascha Hunold 2019-2021
# changes made by Klaus Kraßnitzer 2022
# version 1.4

import sys
import os
import pprint
from optparse import OptionParser


def read_and_check_one_elem_line(f, expected_element_type, error_message):
    try:
        res = expected_element_type(f.readline())
    except ValueError:
        print(error_message, file=sys.stderr)
        exit(1)
    if res <= 0:
        print(error_message, file=sys.stderr)
        exit(1)
    return res

def read_and_check_list(f, expected_length, expected_element_type, error_message):
    s = f.readline()
    res_list = s.split(" ")
    try:
        res_list = list(map(expected_element_type, res_list))
    except ValueError:
        print(error_message, file=sys.stderr)
        exit(1)
    if len(res_list) != expected_length:
        print(error_message, file=sys.stderr)
        exit(1)
    return res_list


# #####################
# N (number of tasks, int)
# N times Task Size (p_j) in scientific notation
# M (number of machines, int)
# S (number of states, int)
# S times Freq in HZ in scientific notation
# S times Pow in Watt as floats
#
#   for each task i in (1:N)
#   print predecessors in one line (as ints) or "0" if task i has no predecessor
# D (deadline , float)
# #####################
def read_instance(inputfile=None):
    instance = {}

    if inputfile is not None:
        if not os.path.isfile(inputfile):
            print("ERROR: Cannot open file %s" % inputfile, file=sys.stderr)
            exit(1)
        f = open(inputfile, 'r')
    else:
        f = sys.stdin


    # number of tasks
    instance["N"] = read_and_check_one_elem_line(f, int,
                                    "ERROR: Number of tasks not correctly specified")

    # work in operations (e.g., FLOPS)
    instance["work"] = read_and_check_list(f, instance["N"], float,
                                    "ERROR: work list not correctly specified")

    # number of machines
    instance["M"] = read_and_check_one_elem_line(f, int,
                                    "ERROR: Number of machines not correctly specified")

    # number of states
    instance["S"] = read_and_check_one_elem_line(f, int,
                                    "ERROR: Number of states not correctly specified")

    # list of states (frequencies)
    instance["freq_list"] = read_and_check_list(f, instance["S"], float,
                                    "ERROR: States list not correctly specified")

    # list of power values for each state
    instance["power_list"] = read_and_check_list(f, instance["S"], float,
                                    "ERROR: Power values list not correctly specified")

    instance["predecessors"] = {}
    for j in range(1, instance["N"] + 1):
        pred_list = f.readline().split(" ")
        try:
            pred_list = list(map(int, pred_list))
        except ValueError:
            print("ERROR: Predecessor list not correctly specified for task %d" % (j), file=sys.stderr)
            exit(1)
        if len(pred_list) == 0:
            print("ERROR: Predecessor list not correctly specified for task %d" % (j), file=sys.stderr)
            exit(1)
        if len(pred_list) == 1 and pred_list[0] == 0:
            # no predecessors for current task
            continue
        instance["predecessors"][j] = pred_list

    instance["deadline"] = read_and_check_one_elem_line(f, float,
                            "ERROR: Deadline not correctly specified")

    if f != sys.stdin:
        f.close()

    return instance



if __name__ == "__main__":

    parser = OptionParser(usage="usage: %prog [options]")

    parser.add_option("-i", "--inputfile",
                       action="store",
                       dest="inputfile",
                       type="string",
                       help="path to input file")
    parser.add_option("-o", "--outputfile",
                       action="store",
                       dest="outputfile",
                       type="string",
                       help="path to output file where rendered instances should be stored")
    parser.add_option("-g", "--graph",
                       action="store_true",
                       dest="createdag",
                       help="generate a visualization of the graph")

    (options, args) = parser.parse_args()

    if options.inputfile == None or not os.path.exists(options.inputfile):
        print("Input file invalid", file=sys.stderr)        
        parser.print_help()
        sys.exit(1)

    instance = read_instance(options.inputfile)

    if options.createdag == True:
        try:
            import graphviz
        except ImportError:
            print("WARNING: Cannot find graphviz. Skipping instance plotting.", file=sys.stderr)                    
            exit (1)

        if options.outputfile == None:
            print("Output filename does not exist.", file=sys.stderr)                    
            parser.print_help()
            sys.exit(1)
            
        dot = graphviz.Digraph(comment="Instance %s" % os.path.basename(options.inputfile))

        task = 1
        for p in instance["work"]:
            dot.node(str(task), "Task %d (w=%.2e)" % (task, p))
            task = task + 1

        for task in instance["predecessors"].keys():
            predec_list = instance["predecessors"][task]
            for j in predec_list:
                dot.edge(str(j), str(task))

        outputfile = os.path.join(options.outputfile)
        rendered = dot.render(outputfile, format='pdf')
    