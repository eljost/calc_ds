#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
from optparse import OptionParser

usage = "Usage: %prog [OPTION]"
parser = OptionParser(usage=usage)
parser.add_option("-c", dest="c_ratio", help="DS calculation by carbon-ratio in the EA. Used with -m.")
parser.add_option("-x", dest="x_ratio", help="DS calculation by substituent-ratio in the EA. Used with -m.")
parser.add_option("-m", dest="subst", help="Type of substituent.")
parser.add_option("-e", dest="raw_formula", help="Elemental composition of the formula.")
parser.add_option("-w", dest="mw_by_ds", action="store_true", help="MW of substituted AGU according to the DS. Used \
                    with -d and -m.")
parser.add_option("-d", dest="x_ds", help="DS of the substituent.")

TOKENS = {"H" : 1.0079,
            "C" : 12.011,
            "N" : 14.007,
            "O" : 15.999,
            "Cl" : 35.453,
            "Br" : 79.904,
            "Si" : 28.086}

def parse_formula(raw_formula):
    formula = list()
    # Split by element
    formula_split = re.findall("([A-Z][a-z]?[\d\.]*)", raw_formula)
    for item in formula_split:
        # Get the stoichiometric coefficients (count)
        element, count = re.match("([A-Za-z]+)([\d\.]*)", item).groups()
        if count is "":
            count = 1
        else:
            count = float(count)
        formula.append((element, count))

    return formula

def get_mw(element):
    return TOKENS[element]

def get_total_mw(raw_formula):
    formula = parse_formula(raw_formula)
    total_mw = 0
    for item in formula:
        element, count = item
        total_mw += get_mw(element) * count

    return total_mw

def get_mw_by_ds(subst, subst_ratio):
    mw_subst = get_mw(subst)
    agu_mw = get_total_mw("C6H10O5")
    agu_subst_mw = agu_mw + mw_subst - get_total_mw("OH")
    
    return (1 - subst_ratio) * agu_mw + (subst_ratio * agu_subst_mw)

def get_element_ratios(raw_formula):
    formula = parse_formula(raw_formula)
    element_ratios = list()
    total_mw = get_total_mw(raw_formula)
    for item in formula:
        element, count = item
        ratio = get_mw(element) * count / total_mw
        element_ratios.append((element, ratio))

    return element_ratios

def get_ds_c_ratio(subst, c_ratio):
    """ Calculates the DS when only one type of substituent with mol weight
    mw_subst is present in the cellulose. The DS is determined according
    to the percentage of carbon in the elemental analysis."""
    mw_subst = get_mw(subst)
    return -3 * (54047 * c_ratio - 24022) / ((1000 * mw_subst - 17007) * c_ratio)

def get_ds_x_ratio(subst, x_ratio):
    """ Calculates the DS using the ratio of the specified
    substituent according to the elemental analysis."""
    mw_c = get_mw("C")
    mw_h = get_mw("H")
    mw_o = get_mw("O")
    mw_subst = get_mw(subst)
    return x_ratio * (6 * mw_c + 10 * mw_h + 5 * mw_o) / (mw_subst + x_ratio * (mw_h + mw_o - mw_subst))

def input_elemental_analysis(raw_formula):
    formula = parse_formula(raw_formula)
    print("Enter your elemental analysis (in %)")
    print("Leave non determined elements empty!")
    elemental_analysis = list()
    for item in formula:
        element = item[0]
        percents = input("{0}: ".format(element))
        if percents is not "":
            elemental_analysis.append((element, percents))

    return elemental_analysis        

if __name__ == "__main__":
    options, args = parser.parse_args()
    raw_formula = options.raw_formula
    c_ratio = options.c_ratio
    x_ratio = options.x_ratio
    subst = options.subst
    mw_by_ds = options.mw_by_ds
    x_ds = options.x_ds
    if raw_formula:
        ratios = get_element_ratios(raw_formula)
        for item in ratios:
            element, ratio = item
            print("{}\t{:.3%}".format(element, ratio))
        print("Total molweight in g/mol: {0}".format(get_total_mw(raw_formula)))
    if c_ratio and subst:
            print("DS of {}-substituted AGU with C-ratio {}: {:.3}".format(
                subst, c_ratio, get_ds_c_ratio(subst, float(c_ratio))))
    if x_ratio and subst:
            print("DS of {}-substituted AGU with by X-ratio {}: {:.3}".format(
                subst, x_ratio, get_ds_x_ratio(subst, float(x_ratio))))
    if mw_by_ds and subst and x_ds:
        print("MW of {}-substituted AGU with DS {} is {:.5}".format(
                subst, x_ds, get_mw_by_ds(subst, float(x_ds))))
