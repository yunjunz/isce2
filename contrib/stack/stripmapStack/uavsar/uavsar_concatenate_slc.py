#!/usr/bin/env python3
############################################################
# Script to concatenate UAVSAR segmets for isce processing.#
# Author: Talib Oliver, 2021                               #
############################################################

import os
import sys
import argparse
import json
import shelve
import gdal
from gdalconst import GA_ReadOnly
import numpy as np
import isce
import isceobj


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


def createParser():
    EXAMPLE = """example:
      uavsar_concatenate_slc.py -w ./ -s1 SLC_seg1 -o SLC_merged
    """
    parser = argparse.ArgumentParser(description='Concatenate 2 UAVSAR segmets for isce processing',
                                     formatter_class=argparse.RawTextHelpFormatter,
                                     epilog=EXAMPLE)

    parser.add_argument('-w', '--work_dir', dest='work_dir', type=str, required=True,
            help='work dir containing slc segments.')
    parser.add_argument('-s1', '--seg1_dir', dest='seg1_dir', type=str, required=True,
            help='Segment 1 directory.')
    parser.add_argument('-o', '--slc_out', dest='slc_merged_dir', type=str, required=True,
            help='merged out directory.')
    return parser


def cmdLineParse(iargs=None):
    '''
    Command line parser.
    '''

    parser = createParser()
    return parser.parse_args(args = iargs)

def read(file, processor='ISCE' , bands=None , dataType=None):
    ''' reader based on GDAL.

    Args:
        * file      -> File name to be read
    Kwargs:
        * processor -> the processor used for the InSAR processing. default: ISCE
        * bands     -> a list of bands to be extracted. If not specified all bands will be extracted.
        * dataType  -> if not specified, it will be extracted from the data itself
    Returns:
        * data : A numpy array with dimensions : number_of_bands * length * width
    '''

    if processor == 'ISCE':
        cmd = 'isce2gis.py envi -i ' + file
        os.system(cmd)

    dataset = gdal.Open(file,GA_ReadOnly)

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


def write(raster, fileName, nbands, bandType):

    ############
    # Create the file
    driver = gdal.GetDriverByName( 'ENVI' )
    dst_ds = driver.Create(fileName, raster.shape[1], raster.shape[0], nbands, bandType )
    dst_ds.GetRasterBand(1).WriteArray( raster, 0 ,0 )

    dst_ds = None

def getShape(file):

    dataset = gdal.Open(file,GA_ReadOnly)
    return dataset.RasterXSize , dataset.RasterYSize


def write_xml(shelveFile, slcFile, length, width):
    with shelve.open(shelveFile,flag='r') as db:
        frame = db['frame']

    # length = frame.numberOfLines
    # width = frame.numberOfSamples

    print (frame) ## To test
    print (width,length)

    slc = isceobj.createSlcImage()
    slc.setWidth(width)
    slc.setLength(length)
    slc.filename = slcFile
    slc.setAccessMode('write')
    slc.renderHdr()
    slc.renderVRT()

    ##### Main #####
def main(iargs=None):
    inps = cmdLineParse(iargs) # read inputs
    work_dir = os.path.expanduser(inps.work_dir) # go to work dir
    os.chdir(work_dir)  
    print('Go to directory: '+ work_dir)
    if not os.path.exists(inps.slc_merged_dir):
        os.mkdir(inps.slc_merged_dir)
    slc_dir_sample = os.path.expanduser(inps.seg1_dir)
    # Check slc segment folders
    images_json = os.path.join(work_dir, 'images.json')
    with open(images_json) as fp:
        images = json.load(fp)
    id = list(images.keys())[0] 
    slc_list = list(images.keys())
    # create shelve folder
    for a in slc_list:
        segs = sorted(images[a]['segments'], key=int)
        slc_group = images[a]['segments']
        total_segs = len(segs)
        slc1_path = (os.path.join(slc_dir_sample.replace('1', segs[0]), a)) + '/' + slc_group[segs[0]]
        slc2_path = (os.path.join(slc_dir_sample.replace('1', segs[1]), a)) + '/' + slc_group[segs[1]]
        slc_merged_path= os.path.join(inps.slc_merged_dir, a)
        slc_merged_file = slc_merged_path + '/' + a + '.slc'
        source_shelveFile = (os.path.join(slc_dir_sample.replace('1', segs[0]), a)) + '/data'
        if not os.path.exists(slc_merged_path):
            os.mkdir(slc_merged_path)

        ## Read slc's
        slc1 = read(slc1_path, processor='ISCE' , bands=None , dataType=None)
        print ('slc segment1', slc1.dtype, slc1.size, slc1.shape)
        slc2 =read(slc2_path, processor='ISCE' , bands=None , dataType=None)
        print ('slc segment2', slc2.dtype, slc2.size, slc2.shape)
        ## Concat
        slc_merged = np.concatenate((slc1, slc2), axis=1)
        print ('merged slc size', slc_merged.dtype, slc_merged.size, slc_merged.shape)
        length, width = slc_merged.shape[1], slc_merged.shape[2]
        slc_merged.tofile(slc_merged_file)

        cmd = 'cp ' + source_shelveFile + ' ' + slc_merged_path +'/'
        print (cmd)
        os.system(cmd)

        cmd = 'uavsar_update_shelve.py -i ' + work_dir + ' -d ' + slc_merged_path + '/data' + ' -l ' + str(length) 
        print (cmd)
        os.system(cmd)


        shelveFile = slc_merged_path + '/data'
        print ('shelve file -->', shelveFile)
        slcFile = os.path.join(slc_merged_path, os.path.basename(slc_merged_file))
        print ('slcfile--->', slcFile)
        write_xml(shelveFile, slcFile, length, width)


###################
if __name__ == "__main__":
    main(sys.argv[1:])
