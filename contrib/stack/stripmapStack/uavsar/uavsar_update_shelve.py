#!/usr/bin/env python3
############################################################
# Script to concatenate UAVSAR segmets for isce processing.#
# Author: Talib Oliver, 2021                               #
############################################################

import isce
from isceobj.Sensor import createSensor
import shelve
import argparse
import glob
from isceobj.Util import Poly1D
from isceobj.Planet.AstronomicalHandbook import Const
import os

def cmdLineParse():
    '''
    Command line parser.
    '''

    parser = argparse.ArgumentParser(description='Update shelve file for UAVSAR.')
    parser.add_argument('-i','--input', dest='workdir', type=str,
            required=True, help='Input UAVSAR directory')
    parser.add_argument('-d','--shelve', dest='shelve_file', type=str,
            default=None, help='Shelve file')
    parser.add_argument('-l', '--length', dest='length', type=int,
            required=True, help='Length of merged file')
    parser.add_argument('-lrc_lat', '--low_right_lat', dest='lrc_lat', type=float,
            required=True, help='Lower right corner latitude')
    parser.add_argument('-lrc_lon', '--low_right_lon', dest='lrc_lon', type=float,
            required=True, help='Lower right corner longitude')
    parser.add_argument('-llc_lat', '--low_left_lat', dest='llc_lat', type=float,
            required=True, help='Lower right corner latitude')
    parser.add_argument('-llc_lon', '--low_left_lon', dest='llc_lon', type=float,
            required=True, help='Lower left corner longitude')
    return parser.parse_args()


def update_shelve(fname, length, lowerRightCornerLat, lowerRightCornerLon,
                  lowerLeftCornerLat, lowerLeftCornerLon):
    '''
    Update shelve file with new length.
    '''
    shelveFile = shelve.open(fname, writeback = True)
    frame = shelveFile['frame']
    ## inputting total values we want to update 
    ## to the already existing list in shelf_file.
    frame.numberOfLines = length
    frame.lowerRightCorner.setLatitude(lowerRightCornerLat)
    frame.lowerRightCorner.setLongitude(lowerRightCornerLon)
    frame.lowerLeftCorner.setLatitude(lowerLeftCornerLat)
    frame.lowerLeftCorner.setLongitude(lowerLeftCornerLon)

    shelveFile.sync() 
    ## now, we simply close the file 'shelf_file'.
    shelveFile.close()


if __name__ == '__main__':
    '''
    Main driver.
    '''

    inps = cmdLineParse()
    work_dir = os.path.expanduser(inps.workdir) #go to work dir
    os.chdir(work_dir)  

    update_shelve(inps.shelve_file, inps.length, inps.lrc_lat, 
                  inps.lrc_lon, inps.llc_lat, inps.llc_lon)
