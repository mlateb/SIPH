""" Module for IO of non-image files
"""
import os
import csv
import ast

from netCDF4 import Dataset


def csv2list(_file, header=False, fixType=True):
    """ read a csv file based table to a list

    Args:
        file (str): path to input text file
        header (bool): first line header or not
        fixType (bool): convert data to correct type or not

    Returns:
        table (list): the table

    """
    # read file
    with open(_file, 'rb') as f:
        reader = csv.reader(f)
        if header:
            next(reader)
        table = list(reader)

    # fix data type
    if fixType:
        for i, row in enumerate(table):
            for j, value in enumerate(row):
                try:
                    table[i][j] = ast.literal_eval(value)
                except:
                    pass

    # done
    return table


def csv2dict(_file, fixType=True):
    """ read a csv file based table to a dictionary

    Args:
        _file (str): path to input text file
        fixType (bool): convert data to correct type or not

    Returns:
        table (list): the table

    """
    # read file
    with open(_file, 'rb') as f:
        reader = csv.DictReader(f)
        table = list(reader)

    # fix data type
    if fixType:
        for i, row in enumerate(table):
            for key in row:
                try:
                    table[i][key] = ast.literal_eval(table[i][key])
                except:
                    pass

    # done
    return table


def hdr2geo(_file):
    """ read envi header file and return geo

    Args:
        file (str): path to input hdr file

    Returns:
        geo (dic): spatial reference

    """
    with open(_file, 'r') as f:
        header = f.readlines()
    geo = {'file': _file}
    for line in header:
        line2 = [x.strip() for x in line.split('=')]
        if line2[0] == 'samples':
            geo['samples'] = ast.literal_eval(line2[1])
        elif line2[0] == 'lines':
            geo['lines'] = ast.literal_eval(line2[1])
        elif line2[0] == 'bands':
            geo['bands'] = ast.literal_eval(line2[1])
        elif line2[0] == 'coordinate system string':
            geo['proj'] = line2[1][1:-1]
        elif line2[0] == 'map info':
            minfo = line2[1][1:-1].split(', ')
            geo['geotrans'] = (ast.literal_eval(minfo[3]),
                                ast.literal_eval(minfo[5]), 0.0,
                                ast.literal_eval(minfo[4]), 0.0,
                                ast.literal_eval(minfo[6]) * (-1))
    return geo


def nc2array(_file, var=0):
    """ read a netCDF file and return an numpy array

    Args:
        _file (str): path to input netCDF file
        var (str): which variable, if NA grab the first one, if int grab nkey

    Returns:
        array (ndarray): output array

    """
    nc = Dataset(_file)
    if type(var) == int:
        var = nc.variables.keys()[var]
    array = nc.variables[var][:]
    return array
