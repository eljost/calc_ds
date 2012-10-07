#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
from optparse import OptionParser

usage = "Usage: %prog [OPTION]"
parser = OptionParser(usage=usage)
parser.add_option("-c", dest="c_ratio", help="Carbon ration in the elemental analysis.")
parser.add_option("-m", dest="subst", help="Type of substituent.")
parser.add_option("-e", dest="raw_formula", help="Displays elemental composition of the formula.")

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
    formula_split = re.findall("([A-Z][a-z]?\d*)", raw_formula)
    for item in formula_split:
        # Get the stoichiometric coefficients (count)
        element, count = re.match("([A-Za-z]+)(\d*)", item).groups()
        if count is "":
            count = 1
        else:
            count = int(count)
        formula.append((element, count))

    return formula

def get_mw(element):
    return TOKENS[element]

def get_total_mw(formula):
    total_mw = 0
    for item in formula:
        element, count = item
        total_mw += get_mw(element) * count

    return total_mw

def get_element_ratios(formula):
    element_ratios = list()
    total_mw = get_total_mw(formula)
    for item in formula:
        element, count = item
        ratio = get_mw(element) * count / total_mw
        element_ratios.append((element, ratio))

    return element_ratios

def get_ds_mono(mw_subst, c_ratio):
    """ Calculates the DS when only one type of substituent with mol weight
    mw_subst is present in the cellulose. The DS is determined according
    to the percentage of carbon in the elemental analysis."""
    return -3 * (54047 * c_ratio - 24022) / ((1000 * mw_subst - 17007) * c_ratio)

def input_elemental_analysis(formula):
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
    subst = options.subst
    if raw_formula is not None:
        formula = parse_formula(raw_formula)
        ratios = get_element_ratios(formula)
        for item in ratios:
            element, ratio = item
            print("{}\t{:.3%}".format(element, ratio))
    if (c_ratio is not None) and (subst is not None):
        mw_subst = get_mw(subst)
        print("DS: {:.3}".format(get_ds_mono(mw_subst, float(c_ratio))))
