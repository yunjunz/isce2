#!/usr/bin/env python3

import os
import glob
import datetime
import argparse
import isce
import isceobj
import shelve 
from isceobj.Util.decorators import use_api
from iscesys import DateTimeUtil as DTU


def createParser():
    '''
    Create command line parser.
    '''

    parser = argparse.ArgumentParser(description='Unzip Alos zip files.')
    parser.add_argument('-i', '--input', dest='input', type=str, required=True,
            help='directory which has all dates as directories. Inside each date, zip files are expected.')
    parser.add_argument('-d', '--dop_file', dest='dopFile', type=str, required=True,
            help='Doppler file for the stack.')
    parser.add_argument('-o', '--output', dest='output', type=str, required=True,
            help='output directory which will be used for unpacking.')
    parser.add_argument('-s', '--segment', dest='segment', type=str, default='1',
            help='segment of the UAVSAR stack to prepare. For "s2" use "2", etc. Default is "1" ')
    parser.add_argument('-t', '--text_cmd', dest='text_cmd', type=str, default='source ~/.bash_profile;', 
            help='text command to be added to the beginning of each line of the run files. Example : source ~/.bash_profile;')

    return parser


def cmdLineParse(iargs=None):
    '''
    Command line parser.
    '''

    parser = createParser()
    return parser.parse_args(args = iargs)

def write_xml(shelveFile, slcFile):
    with shelve.open(shelveFile,flag='r') as db:
        frame = db['frame']

    length = frame.numberOfLines 
    width = frame.numberOfSamples

    print (frame) ## To test
    print (width,length)

    slc = isceobj.createSlcImage()
    slc.setWidth(width)
    slc.setLength(length)
    slc.filename = slcFile
    slc.setAccessMode('write')
    slc.renderHdr()
    slc.renderVRT()

def main(iargs=None):
    '''
    The main driver.
    '''
    inps = cmdLineParse(iargs)
    
    outputDir = os.path.abspath(inps.output)
    run_unPack = 'run_unPackAlos'

    #######################################
  
    slc_files = glob.glob(os.path.join(inps.input, '*_s{a}_*.slc'.format(a=inps.segment)))
    print (slc_files) 

    for file in slc_files:
        fileann = file.replace('_s{a}_1x1.slc'.format(a=inps.segment),'')+'.ann' ## change number for segment
        print (fileann) 

        #for filename in fileann:
        for line in open(fileann):
            if 'Start Time of Acquisition' in line:
                val = line.split('=')[1]
                date = val.split()[0]
                time = val.split()[1]
                time_zone = val.split()[2]
                dt = date + ' ' + time + ' ' + time_zone
                print(dt)
                tStart = datetime.datetime.strptime(dt,"%d-%b-%Y %H:%M:%S %Z")
                filedate = tStart.strftime("%Y%m%dT%H%M")
        
        imgDate = (filedate)
        print (imgDate)
        annFile = file.replace('_s{a}_1x1.slc'.format(a=inps.segment),'')+'.ann' ## TO
        print (annFile)
        imgDir = os.path.join(outputDir,imgDate)
        if not os.path.exists(imgDir):
            os.makedirs(imgDir) ### TO
        # print (imgDir)
        cmd = 'unpackFrame_UAVSAR_seg.py -i ' + annFile  + ' -d '+ inps.dopFile + ' -s '+ inps.segment + ' -o ' + imgDir
        ## to read segments
        print (cmd)
        os.system(cmd)
        
        cmd = 'mv ' + file + ' ' + imgDir
        print(cmd)
        os.system(cmd)

        cmd = 'cp ' + annFile + ' ' + imgDir 
        print(cmd)
        os.system(cmd)

        shelveFile = os.path.join(imgDir, 'data')
        slcFile = os.path.join(imgDir, os.path.basename(file))
        write_xml(shelveFile, slcFile)

if __name__ == '__main__':

    main()


