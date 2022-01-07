#!/usr/bin/env python3
############################################################
# Script to concatenate UAVSAR segmets for isce processing.#
# Author: Talib Oliver, Zhang Yunjun, 2021                 #
############################################################

import os
import sys
import argparse
import glob
import shutil
import json
import shelve
import numpy as np
from osgeo import gdal

import isce
import isceobj
from isceobj.Util.ImageUtil import ImageLib as IML


GDAL2NUMPY_DATATYPE = {
    1 : np.uint8,
    2 : np.uint16,
    3 : np.int16,
    4 : np.uint32,
    5 : np.int32,
    6 : np.float32,
    7 : np.float64,
    10: np.complex64,
    11: np.complex128,
}

EXAMPLE = """example:
  mergeSegments_UAVSAR.py -w ./ -s SLC_seg1 -o SLC
"""

def createParser():
    parser = argparse.ArgumentParser(description='Concatenate 2 UAVSAR segmets for isce processing',
                                     formatter_class=argparse.RawTextHelpFormatter,
                                     epilog=EXAMPLE)

    parser.add_argument('-w', '--work_dir', dest='work_dir', type=str, required=True,
            help='work dir containing slc segments.')
    parser.add_argument('-s', '--s1', '--seg1_dir', dest='seg1_dir', type=str, required=True,
            help='Segment 1 directory.')
    parser.add_argument('-o', '--slc_out', dest='slc_merged_dir', type=str, required=True,
            help='merged out directory.')
    return parser


def cmdLineParse(iargs=None):
    '''
    Command line parser.
    '''
    parser = createParser()
    inps = parser.parse_args(args=iargs)

    inps.work_dir = os.path.abspath(os.path.expanduser(inps.work_dir))
    inps.slc_merged_dir = os.path.abspath(os.path.expanduser(inps.slc_merged_dir))
    inps.seg1_dir = os.path.abspath(os.path.expanduser(inps.seg1_dir))

    return inps


def read(fname, processor='ISCE' , bands=None , dataType=None):
    ''' reader based on GDAL.

    Args:
        * fname     -> File name to be read
    Kwargs:
        * processor -> the processor used for the InSAR processing. default: ISCE
        * bands     -> a list of bands to be extracted. If not specified all bands will be extracted.
        * dataType  -> if not specified, it will be extracted from the data itself
    Returns:
        * data : A numpy array with dimensions : number_of_bands * length * width
    '''

    if processor == 'ISCE':
        img = IML.loadImage(fname)[0]
        img.renderEnviHDR()

    dataset = gdal.Open(fname, gdal.GA_ReadOnly)

    ######################################
    # if the bands have not been specified, all bands will be extracted
    if bands is None:
        bands = range(1,dataset.RasterCount+1)
    ######################################
    # if dataType is not known let's get it from the data:
    if dataType is None:
        band = dataset.GetRasterBand(1)
        dataType =  GDAL2NUMPY_DATATYPE[band.DataType]

    ######################################
    # Form a numpy array of zeros with the the shape of (number of bands * length * width) and a given data type
    data = np.zeros((len(bands), dataset.RasterYSize, dataset.RasterXSize),dtype=dataType)
    ######################################
    # Fill the array with the Raster bands
    idx=0
    for i in bands:
        band=dataset.GetRasterBand(i)
        data[idx,:,:] = band.ReadAsArray()
        idx+=1

    dataset = None
    return data


def read_uavsar_ann_file(fname, comment=';', delimiter='='):
    """Read the UAVSAR annotation file into dictionary.
    """
    # read the entirer text file into list of strings
    lines = None
    with open(fname, 'r') as f:
        lines = f.readlines()

    # convert the list of strings into a dict object
    meta = {}
    for line in lines:
        line = line.strip()
        c = [x.strip() for x in line.split(delimiter, 1)]
        if len(c) >= 2 and not line.startswith(comment):
            key = c[0].split('(')[0].strip()
            value = str.replace(c[1], '\n', '').split(comment)[0].strip()
            meta[key] = value

    return meta


def update_shelve_file(shelve_file, ann_file, length, seg_nums):
    """Update shelve file for multiple segments.
    Segment x Data Approximate Corner 1/2/3/4 represent first line near/far range, last line near/far range
    thus, merged corner 1/2 = first segment corner 1/2
          merged corner 3/4 = last  segment corner 3/4
    """

    # read annotation file for lat/lon1/2/3/4
    ann_dict = read_uavsar_ann_file(ann_file)
    lat1, lon1 = [float(x) for x in ann_dict[f'Segment {seg_nums[0]} Data Approximate Corner 1'].split(',')]
    lat2, lon2 = [float(x) for x in ann_dict[f'Segment {seg_nums[0]} Data Approximate Corner 2'].split(',')]
    lat3, lon3 = [float(x) for x in ann_dict[f'Segment {seg_nums[-1]} Data Approximate Corner 3'].split(',')]
    lat4, lon4 = [float(x) for x in ann_dict[f'Segment {seg_nums[-1]} Data Approximate Corner 4'].split(',')]

    # update shelve file
    fs = shelve.open(shelve_file, writeback=True)
    frame = fs['frame']
    frame.numberOfLines = length
    frame.upperLeftCorner.setLatitude(lat1)
    frame.upperLeftCorner.setLongitude(lon1)
    frame.upperRightCorner.setLatitude(lat2)
    frame.upperRightCorner.setLongitude(lon2)
    frame.lowerLeftCorner.setLatitude(lat3)
    frame.lowerLeftCorner.setLongitude(lon3)
    frame.lowerRightCorner.setLatitude(lat4)
    frame.lowerRightCorner.setLongitude(lon4)
    fs.sync() 
    fs.close()

    return


def write_xml(slcFile, length, width):
    slc = isceobj.createSlcImage()
    slc.setWidth(width)
    slc.setLength(length)
    slc.filename = slcFile
    slc.setAccessMode('write')
    slc.renderHdr()
    slc.renderVRT()
    return


###########################################################################
def main(iargs=None):
    inps = cmdLineParse(iargs)
    seg_dir_dir = os.path.dirname(inps.seg1_dir)
    seg_dir_base = os.path.basename(inps.seg1_dir)

    os.chdir(inps.work_dir)
    print(f'Go to directory: {inps.work_dir}')

    # create merged SLC directory
    if not os.path.exists(inps.slc_merged_dir):
        os.mkdir(inps.slc_merged_dir)

    # read json file for segments info
    images_json = os.path.join(inps.work_dir, 'images.json')
    with open(images_json) as fp:
        images = json.load(fp)
    date_list = list(images.keys())

    # loop over each date
    for date_str in date_list:
        merged_dir = os.path.join(inps.slc_merged_dir, date_str)
        merged_file = os.path.join(merged_dir, f'{date_str}.slc')
        os.makedirs(merged_dir, exist_ok=True)

        # loop over the list of segments to read and concatenate
        seg_dict = images[date_str]['segments']
        seg_inds = sorted(list(seg_dict.keys()))
        data = None
        for seg_ind in seg_inds:
            seg_dir = os.path.join(seg_dir_dir, seg_dir_base.replace('1', seg_ind), date_str)
            seg_file = os.path.join(seg_dir, os.path.basename(seg_dict[seg_ind]))

            print(f'reading SLC segment{seg_ind}: {seg_file}')
            data_seg = read(seg_file, processor='ISCE', bands=None , dataType=None)
            print(f'segment size: {data_seg.shape}')
            if data is None:
                data = np.array(data_seg)
            else:
                data = np.concatenate((data, data_seg), axis=1)
        del data_seg

        print(f'writing the merged SLC in {data.shape} in {data.dtype} to {merged_file} ...')
        data.tofile(merged_file)
        (length, width) = data.shape[-2:]
        del data

        # prepare shelve file
        print(f'copy shelve file from {seg_dir}')
        for fname in glob.glob(os.path.join(seg_dir, 'data*')):
            shutil.copy2(fname, merged_dir)
        shelve_file = os.path.join(merged_dir, 'data')

        ann_file = glob.glob(os.path.join(seg_dir, '*.ann'))[0]
        update_shelve_file(shelve_file, ann_file, length, seg_inds)
        print(f'update shelve file based on {ann_file} for segments {seg_inds}')
        
        # prepare XML file
        write_xml(merged_file, length, width)

    return


###################
if __name__ == "__main__":
    main(sys.argv[1:])
