#!/usr/bin/env python3

#Author: Heresh Fattahi

import os, sys, glob
import argparse
import configparser
import datetime
import numpy as np
import shelve
import isce
import isceobj
from mroipac.baseline.Baseline import Baseline


filtStrength = '0.8'
noMCF = 'False'
defoMax = '2'
maxNodes = 72


class config(object):
    """
       A class representing the config file
    """
    def __init__(self, outname):
        self.f= open(outname,'w')
        self.f.write('[Common]'+'\n')
        self.f.write('')
        self.f.write('##########################'+'\n')

    def configure(self,inps):
        for k in inps.__dict__.keys():
            setattr(self, k, inps.__dict__[k])
        self.plot = 'False'
        self.misreg = None

    def cropFrame(self, function):
        self.f.write('##########################'+'\n')
        self.f.write(function+'\n')
        self.f.write('cropFrame : ' + '\n')
        self.f.write('input : ' +  self.inputDir + '\n')
        self.f.write('box_str : ' + self.bbox + '\n')
        self.f.write('output : ' + self.cropOutputDir + '\n')

        ##For booleans, just having an entry makes it True
        ##Value of the text doesnt matter
        if self.nativeDoppler:
            self.f.write('native : True \n')
        if self.israw:
            self.f.write('raw : True \n')
        self.f.write('##########################'+'\n')

    def focus(self,function):
        self.f.write('##########################'+'\n')
        self.f.write(function+'\n')
        self.f.write('focus : '+'\n')
        self.f.write('input : ' + self.slcDir +'\n')
        self.f.write('##########################'+'\n')

    def topo(self,function):

        self.f.write('##########################'+'\n')
        self.f.write(function+'\n')
        self.f.write('topo : '+'\n')
        self.f.write('reference : ' + self.slcDir +'\n')
        self.f.write('dem : ' + self.dem +'\n')
        self.f.write('output : ' + self.geometryDir +'\n')
        self.f.write('alks : ' + self.alks +'\n')
        self.f.write('rlks : ' + self.rlks +'\n')
        if self.nativeDoppler:
            self.f.write('native : True\n')
        if self.useGPU:
            self.f.write('useGPU : True \n')
        else:
            self.f.write('useGPU : False\n')
        self.f.write('##########################'+'\n')

    def createWaterMask(self, function):

        self.f.write('##########################'+'\n')
        self.f.write(function+'\n')
        self.f.write('createWaterMask : '+'\n')
        self.f.write('dem_file : ' + self.dem +'\n')
        self.f.write('lat_file : ' + self.latFile +'\n')
        self.f.write('lon_file : ' + self.lonFile +'\n')
        self.f.write('output : ' + self.waterMaskFile + '\n')
        self.f.write('##########################'+'\n')

    def geo2rdr(self, function):

        self.f.write('##########################'+'\n')
        self.f.write(function+'\n')
        self.f.write('geo2rdr : '+'\n')
        self.f.write('reference : ' + self.referenceSlc +'\n')
        self.f.write('secondary : ' + self.secondarySlc +'\n')
        self.f.write('geom : ' + self.geometryDir +'\n')
        if self.nativeDoppler:
            self.f.write('native : True\n')
        if self.useGPU:
            self.f.write('useGPU : True \n')
        else:
            self.f.write('useGPU : False\n')
        self.f.write('outdir : ' + self.offsetDir+'\n')
        self.f.write('##########################'+'\n')

    def resampleSlc(self, function):
        self.f.write('##########################'+'\n')
        self.f.write(function+'\n')
        self.f.write('resampleSlc : '+'\n')
        self.f.write('reference : ' + self.referenceSlc + '\n')
        self.f.write('secondary : ' + self.secondarySlc +'\n')
        self.f.write('coreg : ' + self.coregSecondarySlc +'\n')
        self.f.write('offsets : ' + self.offsetDir +'\n')
        if self.misreg:
            self.f.write('poly : ' + self.misreg + '\n')
        self.f.write('##########################'+'\n')

    def resampleSlc_subband(self, function):
        self.f.write('##########################'+'\n')
        self.f.write(function+'\n')
        self.f.write('resampleSlc_subBand : '+'\n')
        #self.f.write('reference : ' + self.referenceSlc + '\n')
        self.f.write('secondary : ' + self.secondarySlc +'\n')
        self.f.write('coreg : ' + self.coregSecondarySlc +'\n')
        self.f.write('offsets : ' + self.offsetDir +'\n')
        if self.misreg:
            self.f.write('poly : ' + self.misreg + '\n')
        self.f.write('##########################'+'\n')

    def baselineGrid(self, function):
        self.f.write('##########################'+'\n')
        self.f.write(function + '\n')
        self.f.write('baselineGrid : ' + '\n')
        self.f.write('reference : ' + self.coregSecondarySlc + "/referenceShelve" + '\n')
        self.f.write('secondary : '  + self.coregSecondarySlc + "/secondaryShelve" + '\n')
        self.f.write('baseline_file : ' + self.baselineGridFile + '\n')

    def refineSecondaryTiming(self, function):
        self.f.write('##########################'+'\n')
        self.f.write(function+'\n')
        self.f.write('refineSecondaryTiming : '+'\n')
        self.f.write('reference : ' + self.referenceSlc + '\n')
        self.f.write('secondary : ' + self.secondarySlc +'\n')
        self.f.write('mm : ' + self.referenceMetaData + '\n')
        self.f.write('ss : ' + self.secondaryMetaData + '\n')
        self.f.write('outfile : '+ self.outfile + '\n')

    def denseOffsets(self, function):
        self.f.write('##########################'+'\n')
        self.f.write(function+'\n')
        self.f.write('denseOffsets : '+'\n')
        self.f.write('reference : ' + self.referenceSlc + '\n')
        self.f.write('secondary : ' + self.secondarySlc +'\n')
        self.f.write('outPrefix : '+ self.outfile + '\n')

    def filterOffsets(self, function):
        self.f.write('##########################'+'\n')
        self.f.write(function+'\n')
        self.f.write('MaskAndFilter : '+'\n')
        self.f.write('dense_offset : ' + self.denseOffset + '\n')
        self.f.write('snr : ' + self.snr +'\n')
        self.f.write('output_directory : '+ self.outDir + '\n') 

    def resampleOffset(self, function):
        self.f.write('##########################'+'\n')
        self.f.write(function+'\n')
        self.f.write('resampleOffsets : ' + '\n')
        self.f.write('input : ' + self.input + '\n')
        self.f.write('target_file : '+ self.targetFile + '\n')
        self.f.write('output : ' + self.output + '\n')

    def rubbersheet(self, function):
        self.f.write('##########################'+'\n')
        self.f.write(function+'\n')
        self.f.write('rubberSheeting : ' + '\n')
        self.f.write('geometry_azimuth_offset : ' + self.geometry_azimuth_offset + '\n')
        self.f.write('dense_offset : '+ self.dense_offset + '\n')
        self.f.write('snr : ' + self.snr + '\n')
        self.f.write('output_azimuth_offset : ' + self.output_azimuth_offset + '\n')
        self.f.write('output_directory : ' + self.output_directory + '\n')

    def generateIgram(self, function):
        self.f.write('##########################'+'\n')
        self.f.write(function+'\n')
        self.f.write('crossmul : '+'\n')
        self.f.write('reference : ' + self.referenceSlc +'\n')
        self.f.write('secondary : ' + self.secondarySlc +'\n')
        self.f.write('outdir : ' + self.outDir + '\n')
        self.f.write('alks : ' + self.alks + '\n')
        self.f.write('rlks : ' + self.rlks + '\n')
        self.f.write('##########################'+'\n')

    def filterCoherence(self, function): 
        self.f.write('##########################'+'\n')
        self.f.write(function+'\n')
        self.f.write('FilterAndCoherence : ' + '\n')
        self.f.write('input : ' + self.igram + '\n')
        self.f.write('filt : ' + self.filtIgram + '\n')
        self.f.write('coh : ' + self.coherence  + '\n')
        self.f.write('strength : ' + self.filtStrength + '\n')
        self.f.write('##########################'+'\n')

    def unwrap(self, function):
        self.f.write('##########################'+'\n')
        self.f.write(function+'\n') 
        self.f.write('unwrap : ' + '\n')
        self.f.write( 'ifg : ' + self.igram + '\n')  
        self.f.write( 'coh : ' + self.coherence + '\n')
        self.f.write( 'unwprefix : ' + self.unwIfg + '\n')      
        self.f.write('nomcf : ' + self.noMCF + '\n')
        self.f.write('reference : ' + self.reference + '\n')
        self.f.write('defomax : ' + self.defoMax + '\n')
        self.f.write('alks : ' + self.alks + '\n')
        self.f.write('rlks : ' + self.rlks + '\n')
        self.f.write('method : ' + self.unwMethod + '\n')
        self.f.write('##########################'+'\n')

    def splitRangeSpectrum(self, function):
        self.f.write('##########################'+'\n')
        self.f.write(function+'\n')
        self.f.write('splitSpectrum : ' + '\n')
        self.f.write('slc : ' + self.slc + '\n')
        self.f.write('outDir : ' + self.outDir + '\n')
        self.f.write('shelve : ' + self.shelve + '\n')
        if self.fL and self.fH and self.bandWidth:
            self.f.write('dcL : ' + self.fL + '\n')
            self.f.write('dcH : ' + self.fH + '\n')
            self.f.write('bw : ' + self.bandWidth + '\n')
        self.f.write('##########################'+'\n')
   
    def estimateDispersive(self, function):
        self.f.write('##########################'+'\n')
        self.f.write(function+'\n')
        self.f.write('estimateIono :' + '\n')
        self.f.write('low_band_igram_prefix : ' + self.lowBandIgram + '\n')
        self.f.write('high_band_igram_prefix : ' + self.highBandIgram + '\n')
        self.f.write('low_band_igram_unw_method : ' + self.unwMethod + '\n')
        self.f.write('high_band_igram_unw_method : ' + self.unwMethod + '\n')
        self.f.write('low_band_shelve : '+ self.lowBandShelve +'\n')
        self.f.write('high_band_shelve : '+ self.highBandShelve +'\n')
        self.f.write('low_band_coherence : ' + self.lowBandCor + '\n')
        self.f.write('high_band_coherence : ' + self.highBandCor + '\n')
        self.f.write('azimuth_looks : ' + self.alks + '\n')
        self.f.write('range_looks : ' + self.rlks + '\n')
        self.f.write('filter_sigma_x : ' + self.filterSigmaX + '\n')
        self.f.write('filter_sigma_y : ' + self.filterSigmaY + '\n')
        self.f.write('filter_size_x : ' + self.filterSizeX + '\n')
        self.f.write('filter_size_y : ' + self.filterSizeY + '\n')
        self.f.write('filter_kernel_rotation : ' + self.filterKernelRotation + '\n')
        self.f.write('outDir : ' + self.outDir + '\n')
        self.f.write('##########################'+'\n')

    def finalize(self):
        self.f.close()



def get_dates(inps):
 
    dirs = glob.glob(inps.slcDir+'/*')
    acuisitionDates = []
    for dir in dirs:
        expectedRaw = os.path.join(dir,os.path.basename(dir) + '.slc')
        if os.path.exists(expectedRaw):
            acuisitionDates.append(os.path.basename(dir))
  
    acuisitionDates.sort()
    print (dirs)
    print (acuisitionDates)
    if inps.referenceDate not in acuisitionDates:
        print ('reference date was not found. The first acquisition will be considered as the stack reference date.')
    if inps.referenceDate is None or inps.referenceDate not in acuisitionDates:
        inps.referenceDate = acuisitionDates[0]
    secondaryDates = acuisitionDates.copy()
    secondaryDates.remove(inps.referenceDate)
    return acuisitionDates, inps.referenceDate, secondaryDates 
  
class run(object):
    """
       A class representing a run which may contain several functions
    """
    #def __init__(self):

    def configure(self,inps, runName):
        for k in inps.__dict__.keys():
            setattr(self, k, inps.__dict__[k])
        self.runDir = os.path.join(self.workDir, 'run_files')
        os.makedirs(self.runDir, exist_ok=True)

        self.run_outname = os.path.join(self.runDir, runName)
        print ('writing ', self.run_outname)

        self.configDir = os.path.join(self.workDir,'configs')
        os.makedirs(self.configDir, exist_ok=True)

        # passing argument of started from raw
        if inps.nofocus is  False:
            self.raw_string = '.raw'
        else:
            self.raw_string = '' 

        # folder structures
        self.stack_folder = inps.stack_folder
        selfdense_offsets_folder = inps.dense_offsets_folder

        self.runf= open(self.run_outname,'w')

    def crop(self, acquisitionDates, config_prefix, native=True, israw=True):
        for d in acquisitionDates:
            configName = os.path.join(self.configDir, config_prefix + d)
            configObj = config(configName)
            configObj.configure(self)
            configObj.inputDir = os.path.join(self.fullFrameSlcDir, d)
            configObj.cropOutputDir = os.path.join(self.slcDir, d)
            configObj.bbox = self.bbox
            configObj.nativeDoppler = native
            configObj.israw = israw
            configObj.cropFrame('[Function-1]')
            self.runf.write(self.text_cmd+'stripmapWrapper.py -c '+ configName+'\n')
 
    def reference_focus_split_geometry(self, stackReference, config_prefix, split=False, focus=True, native=True):
        """focusing reference and producing geometry files"""
        configName = os.path.join(self.configDir, config_prefix + stackReference)
        configObj = config(configName)
        configObj.configure(self)
        configObj.slcDir = os.path.join(self.slcDir,stackReference)
        configObj.geometryDir = os.path.join(self.workDir,self.stack_folder, 'geom_reference')

        counter=1
        if focus:
            configObj.focus('[Function-{0}]'.format(counter))
            counter += 1
       
        configObj.nativeDoppler = focus or native
        configObj.topo('[Function-{0}]'.format(counter))
        counter += 1

        if split:
            configObj.slc = os.path.join(configObj.slcDir,stackReference+self.raw_string+'.slc')
            configObj.outDir = configObj.slcDir
            configObj.shelve = os.path.join(configObj.slcDir, 'data')
            configObj.splitRangeSpectrum('[Function-{0}]'.format(counter))
            counter += 1

        # generate water mask in radar coordinates
        configObj.latFile = os.path.join(self.workDir, 'geom_reference/lat.rdr')
        configObj.lonFile = os.path.join(self.workDir, 'geom_reference/lon.rdr')
        configObj.waterMaskFile = os.path.join(self.workDir, 'geom_reference/waterMask.rdr')
        configObj.createWaterMask('[Function-{0}]'.format(counter))
        counter += 1

        configObj.finalize()
        del configObj
        self.runf.write(self.text_cmd+'stripmapWrapper.py -c '+ configName+'\n')


    def secondarys_focus_split(self, secondaryDates, config_prefix, split=False, focus=True, native=True):
        for secondary in secondaryDates:
            configName = os.path.join(self.configDir, config_prefix + '_'+secondary)
            configObj = config(configName)
            configObj.configure(self)
            configObj.slcDir = os.path.join(self.slcDir,secondary)
            counter=1
            if focus:
                configObj.focus('[Function-{0}]'.format(counter))
                counter += 1
            if split:
                configObj.slc = os.path.join(configObj.slcDir,secondary + self.raw_string + '.slc')
                configObj.outDir = configObj.slcDir
                configObj.shelve = os.path.join(configObj.slcDir, 'data')
                configObj.splitRangeSpectrum('[Function-{0}]'.format(counter))
            configObj.finalize()
            del configObj
            self.runf.write(self.text_cmd+'stripmapWrapper.py -c '+ configName+'\n')

    def secondarys_geo2rdr_resampleSlc(self, stackReference, secondaryDates, config_prefix, native=True):

        for secondary in secondaryDates:
            configName = os.path.join(self.configDir,config_prefix+secondary) 
            configObj = config(configName)
            configObj.configure(self)
            configObj.referenceSlc = os.path.join(self.slcDir, stackReference)
            configObj.secondarySlc = os.path.join(self.slcDir, secondary)
            configObj.geometryDir = os.path.join(self.workDir, self.stack_folder,'geom_reference')
            configObj.offsetDir = os.path.join(self.workDir, 'offsets',secondary)
            configObj.nativeDoppler = native
            configObj.geo2rdr('[Function-1]')
            configObj.coregSecondarySlc = os.path.join(self.workDir, 'coregSLC','Coarse',secondary)
            configObj.resampleSlc('[Function-2]')
            configObj.finalize()
            del configObj
            self.runf.write(self.text_cmd+'stripmapWrapper.py -c '+ configName+'\n')


    def refineSecondaryTiming_singleReference(self, stackReference, secondaryDates, config_prefix):
  
        for secondary in secondaryDates:
            configName = os.path.join(self.configDir,config_prefix+secondary)
            configObj = config(configName)  
            configObj.configure(self)
            configObj.referenceSlc = os.path.join(self.slcDir, stackReference,stackReference+self.raw_string+'.slc')
            configObj.secondarySlc = os.path.join(self.workDir, 'coregSLC','Coarse', secondary,secondary +'.slc')
            configObj.referenceMetaData = os.path.join(self.slcDir, stackReference)
            configObj.secondaryMetaData = os.path.join(self.slcDir, secondary)
            configObj.outfile = os.path.join(self.workDir, 'offsets', secondary ,'misreg')
            configObj.refineSecondaryTiming('[Function-1]')
            configObj.finalize()
            self.runf.write(self.text_cmd+'stripmapWrapper.py -c '+ configName+'\n')


    def refineSecondaryTiming_Network(self, pairs, stackReference, secondaryDates,  config_prefix):
  
        for pair in pairs:
            configName = os.path.join(self.configDir,config_prefix + pair[0] + '_' + pair[1])
            configObj = config(configName)
            configObj.configure(self)
            if pair[0] == stackReference:
                configObj.referenceSlc = os.path.join(self.slcDir,stackReference,stackReference+self.raw_string+'.slc')
            else:
                configObj.referenceSlc = os.path.join(self.workDir, 'coregSLC','Coarse', pair[0]  , pair[0] + '.slc')
            if pair[1] == stackReference:
                configObj.secondarySlc = os.path.join(self.slcDir,stackReference, stackReference+self.raw_string+'.slc')
            else:
                configObj.secondarySlc = os.path.join(self.workDir, 'coregSLC','Coarse', pair[1], pair[1] + '.slc')
            configObj.referenceMetaData = os.path.join(self.slcDir, pair[0])
            configObj.secondaryMetaData = os.path.join(self.slcDir, pair[1])
            configObj.outfile = os.path.join(self.workDir, 'refineSecondaryTiming','pairs', pair[0] + '_' + pair[1] ,'misreg')
            configObj.refineSecondaryTiming('[Function-1]')
            configObj.finalize()
            del configObj
            self.runf.write(self.text_cmd+'stripmapWrapper.py -c '+ configName+'\n')


    def denseOffsets_Network(self, pairs, stackReference, secondaryDates, config_prefix):

        for pair in pairs:
            configName = os.path.join(self.configDir,config_prefix + pair[0] + '_' + pair[1])
            configObj = config(configName)
            configObj.configure(self)
            if pair[0] == stackReference:
                 configObj.referenceSlc = os.path.join(self.slcDir,
                                                    stackReference,
                                                    stackReference+self.raw_string + '.slc')
            else:
                 configObj.referenceSlc = os.path.join(self.workDir,
                                                    self.stack_folder,
                                                    'SLC',
                                                    pair[0],
                                                    pair[0] + '.slc')
            if pair[1] == stackReference:
                 configObj.secondarySlc = os.path.join(self.slcDir,
                                                   stackReference,
                                                   stackReference+self.raw_string+'.slc')
            else:
                 configObj.secondarySlc = os.path.join(self.workDir,
                                                   self.stack_folder,
                                                   'SLC',
                                                   pair[1],
                                                   pair[1] + '.slc')
            configObj.outfile = os.path.join(self.workDir,
                                             self.dense_offsets_folder,
                                             'pairs',
                                             pair[0] + '_' + pair[1],
                                             pair[0] + '_' + pair[1])

            configObj.denseOffsets('[Function-1]')
            configObj.denseOffset = configObj.outfile + '.bil'
            configObj.snr = configObj.outfile + '_snr.bil'
            configObj.outDir = os.path.join(self.workDir, self.dense_offsets_folder,'pairs' , pair[0] + '_' + pair[1])
            configObj.filterOffsets('[Function-2]')
            configObj.finalize()
            del configObj
            self.runf.write(self.text_cmd + 'stripmapWrapper.py -c '+ configName+'\n')

  
    def invertMisregPoly(self):

        pairDirs = os.path.join(self.workDir, 'refineSecondaryTiming/pairs/')
        dateDirs = os.path.join(self.workDir, 'refineSecondaryTiming/dates/')
        cmd = self.text_cmd + 'invertMisreg.py -i ' + pairDirs + ' -o ' + dateDirs
        self.runf.write(cmd + '\n')


    def  invertDenseOffsets(self):

        pairDirs = os.path.join(self.workDir, self.dense_offsets_folder, 'pairs')
        dateDirs = os.path.join(self.workDir, self.dense_offsets_folder, 'dates')
        cmd = self.text_cmd + 'invertOffsets.py -i ' + pairDirs + ' -o ' + dateDirs
        self.runf.write(cmd + '\n')

    def rubbersheet(self, secondaryDates, config_prefix):

        for secondary in secondaryDates:
            configName = os.path.join(self.configDir, config_prefix+secondary)
            configObj = config(configName)
            configObj.configure(self)
            configObj.geometry_azimuth_offset = os.path.join(self.workDir, 'offsets' , secondary , 'azimuth.off')
            configObj.dense_offset = os.path.join(self.workDir,self.dense_offsets_folder,'dates', secondary , secondary + '.bil')
            configObj.snr = os.path.join(self.workDir,self.dense_offsets_folder,'dates' , secondary , secondary + '_snr.bil')
            configObj.output_azimuth_offset = 'azimuth.off'
            configObj.output_directory = os.path.join(self.workDir,self.dense_offsets_folder,'dates', secondary)
            configObj.rubbersheet('[Function-1]')
            configObj.finalize()
            self.runf.write(self.text_cmd+'stripmapWrapper.py -c '+ configName+'\n')
   

    def resampleOffset(self, secondaryDates, config_prefix):

        for secondary in secondaryDates:
            configName = os.path.join(self.configDir, config_prefix+secondary)
            configObj = config(configName)
            configObj.configure(self)
            configObj.targetFile = os.path.join(self.workDir, 'offsets/'+secondary + '/azimuth.off')
            configObj.input = os.path.join(self.workDir,self.dense_offsets_folder,'dates',secondary  , secondary + '.bil')
            configObj.output = os.path.join(self.workDir,self.dense_offsets_folder,'dates',secondary, 'azimuth.off')
            configObj.resampleOffset('[Function-1]')
            configObj.finalize()
            self.runf.write(self.text_cmd+'stripmapWrapper.py -c '+ configName+'\n')
  

    def replaceOffsets(self, secondaryDates):

        dateDirs = os.path.join(self.workDir, self.dense_offsets_folder,'dates')
        for secondary in secondaryDates:
            geometryOffset = os.path.join(self.workDir, 'offsets', secondary  , 'azimuth.off')
            geometryOnlyOffset = os.path.join(self.workDir, 'offsets' , secondary , 'azimuth.off.geometry')
            rubberSheeted = os.path.join(self.workDir,self.dense_offsets_folder,'dates' , secondary , 'azimuth.off')
            cmd = self.text_cmd + 'mv ' + geometryOffset + ' ' + geometryOnlyOffset
            cmd = cmd + '; mv ' + rubberSheeted + ' ' + geometryOffset
            self.runf.write(cmd + '\n')

  
    def gridBaseline(self, stackReference, secondaryDates, config_prefix, split=False):
        for secondary in secondaryDates:
            configName = os.path.join(self.configDir, config_prefix+secondary)
            configObj = config(configName)
            configObj.coregSecondarySlc = os.path.join(self.workDir,self.stack_folder,'SLC',secondary)
            configObj.baselineGridFile = os.path.join(self.workDir, self.stack_folder,'baselines', secondary,secondary )
            configObj.baselineGrid('[Function-1]')
            configObj.finalize()
            self.runf.write(self.text_cmd+'stripmapWrapper.py -c '+ configName+'\n')
            
        # also add the reference to be included
        configName = os.path.join(self.configDir, config_prefix+stackReference)
        configObj = config(configName)
        configObj.coregSecondarySlc = os.path.join(self.workDir,self.stack_folder,'SLC',stackReference)        
        configObj.baselineGridFile = os.path.join(self.workDir, self.stack_folder,'baselines', stackReference,stackReference )
        configObj.baselineGrid('[Function-1]')
        configObj.finalize()
        self.runf.write(self.text_cmd+'stripmapWrapper.py -c '+ configName+'\n')

    def secondarys_fine_resampleSlc(self, stackReference, secondaryDates, config_prefix, split=False):
        # copy over the reference into the final SLC folder as well
        self.runf.write(self.text_cmd + ' referenceStackCopy.py -i ' + 
                        os.path.join(self.slcDir, 
                                     stackReference,
                                     stackReference + self.raw_string + '.slc') + ' -o ' +
                        os.path.join(self.workDir,
                                     self.stack_folder,
                                     'SLC',
                                     stackReference,
                                     stackReference+'.slc' )+ '\n')

        # now resample each of the secondarys to the reference geometry
        for secondary in secondaryDates:
            configName = os.path.join(self.configDir, config_prefix+secondary)
            configObj = config(configName)
            configObj.configure(self)
            configObj.referenceSlc = os.path.join(self.slcDir, stackReference)
            configObj.secondarySlc = os.path.join(self.slcDir, secondary)
            configObj.offsetDir = os.path.join(self.workDir, 'offsets',secondary)
            configObj.coregSecondarySlc = os.path.join(self.workDir,self.stack_folder,'SLC',secondary) 
            configObj.misreg = os.path.join(self.workDir, 'refineSecondaryTiming','dates', secondary, 'misreg')
            configObj.resampleSlc('[Function-1]')
            
            if split:
                configObj.secondarySlc = os.path.join(self.slcDir, secondary,'LowBand')
                configObj.coregSecondarySlc = os.path.join(self.workDir, self.stack_folder,'SLC',  secondary, 'LowBand')
                configObj.resampleSlc_subband('[Function-2]')
                
                configObj.secondarySlc = os.path.join(self.slcDir, secondary,'HighBand')
                configObj.coregSecondarySlc = os.path.join(self.workDir,self.stack_folder, 'SLC', secondary, 'HighBand')
                configObj.resampleSlc_subband('[Function-3]')
            configObj.finalize()
            self.runf.write(self.text_cmd+'stripmapWrapper.py -c '+ configName+'\n')

    def igrams_network(self,  pairs, acuisitionDates, stackReference,low_or_high, config_prefix):

        for pair in pairs:
            configName = os.path.join(self.configDir,config_prefix + pair[0] + '_' + pair[1])
            configObj = config(configName)
            configObj.configure(self)
            
            if pair[0] == stackReference:
                 configObj.referenceSlc = os.path.join(self.slcDir,
                                                    stackReference + low_or_high + stackReference+self.raw_string +'.slc')
            else:
                 configObj.referenceSlc = os.path.join(self.workDir,
                                                    self.stack_folder,
                                                    'SLC',
                                                    pair[0] + low_or_high + pair[0] + '.slc')
            if pair[1] == stackReference:
                 configObj.secondarySlc = os.path.join(self.slcDir,
                                                   stackReference + low_or_high + stackReference+self.raw_string+'.slc')
            else:
                 configObj.secondarySlc = os.path.join(self.workDir,
                                                   self.stack_folder,
                                                   'SLC',
                                                   pair[1] + low_or_high + pair[1] + '.slc')

            configObj.outDir = os.path.join(self.workDir,
                                            'Igrams' + low_or_high + pair[0] + '_'  + pair[1],
                                            pair[0] + '_'  + pair[1])

            configObj.generateIgram('[Function-1]')

            configObj.igram = configObj.outDir+'.int'
            if float(configObj.filtStrength) > 0.:
                configObj.filtIgram = os.path.dirname(configObj.outDir) + '/filt_' + pair[0] + '_'  + pair[1] + '.int'
                configObj.coherence = os.path.dirname(configObj.outDir) + '/filt_' + pair[0] + '_'  + pair[1] + '.cor'
            else:
                # do not add prefix filt_ to output file if no filtering is applied.
                configObj.filtIgram = os.path.dirname(configObj.outDir) + '/' + pair[0] + '_'  + pair[1] + '.int'
                configObj.coherence = os.path.dirname(configObj.outDir) + '/' + pair[0] + '_'  + pair[1] + '.cor'
            configObj.filterCoherence('[Function-2]')

            # skip phase unwrapping if input method == no
            if self.unwMethod.lower() != 'no':
                configObj.igram = configObj.filtIgram
                configObj.unwIfg = os.path.splitext(configObj.igram)[0]
                configObj.noMCF = noMCF
                configObj.reference = os.path.join(self.slcDir,stackReference +'/data') 
                configObj.defoMax = defoMax
                configObj.unwrap('[Function-3]')
            configObj.finalize()
            self.runf.write(self.text_cmd+'stripmapWrapper.py -c '+ configName+'\n')


    def dispersive_nonDispersive(self, pairs, acuisitionDates, stackReference, 
                           lowBand, highBand, config_prefix):
        for pair in pairs:
            configName = os.path.join(self.configDir,config_prefix + pair[0] + '_' + pair[1])
            configObj = config(configName) 
            configObj.configure(self)
            configObj.lowBandIgram  = os.path.join(self.workDir,
                                                   'Igrams' + lowBand + pair[0] + '_'  + pair[1],
                                                   'filt_' + pair[0] + '_'  + pair[1])
            configObj.highBandIgram = os.path.join(self.workDir,
                                                   'Igrams' + highBand + pair[0] + '_'  + pair[1],
                                                   'filt_' + pair[0] + '_'  + pair[1])

            configObj.lowBandCor  = os.path.join(self.workDir,
                                                 'Igrams' + lowBand + pair[0] + '_'  + pair[1],
                                                 'filt_' + pair[0] + '_'  + pair[1] + '.cor')
            configObj.highBandCor = os.path.join(self.workDir,
                                                 'Igrams' + highBand + pair[0] + '_'  + pair[1],
                                                 'filt_' + pair[0] + '_'  + pair[1] + '.cor')

            configObj.lowBandShelve = os.path.join(self.slcDir,pair[0] + lowBand  + 'data') 
            configObj.highBandShelve = os.path.join(self.slcDir,pair[0] + highBand  + 'data')   
            configObj.outDir = os.path.join(self.workDir, 'Ionosphere/'+pair[0]+'_'+pair[1])
            configObj.estimateDispersive('[Function-1]')
            configObj.finalize()
            self.runf.write(self.text_cmd+'stripmapWrapper.py -c '+ configName+'\n')

    def finalize(self):
        self.runf.close() 
        writeJobFile(self.run_outname)


'''

class workflow(object):
    """
       A class representing a run which may contain several functions
    """
    #def __init__(self):

    def configure(self,inps, runName):
        for k in inps.__dict__.keys():
            setattr(self, k, inps.__dict__[k])

    def  

'''

##############################

def baselinePair(baselineDir, reference, secondary,doBaselines=True):
    
    if doBaselines: # open files to calculate baselines
        try:
            mdb = shelve.open( os.path.join(reference, 'raw'), flag='r')
            sdb = shelve.open( os.path.join(secondary, 'raw'), flag='r')
        except:
            mdb = shelve.open( os.path.join(reference, 'data'), flag='r')
            sdb = shelve.open( os.path.join(secondary, 'data'), flag='r')

        mFrame = mdb['frame']
        sFrame = sdb['frame']

        bObj = Baseline()
        bObj.configure()
        bObj.wireInputPort(name='referenceFrame', object=mFrame)
        bObj.wireInputPort(name='secondaryFrame', object=sFrame)
        bObj.baseline()    # calculate baseline from orbits
        pBaselineBottom = bObj.pBaselineBottom
        pBaselineTop = bObj.pBaselineTop
    else:       # set baselines to zero if not calculated
        pBaselineBottom = 0.0
        pBaselineTop = 0.0
        
    baselineOutName = os.path.basename(reference) + "_" + os.path.basename(secondary) + ".txt"
    f = open(os.path.join(baselineDir, baselineOutName) , 'w')
    f.write("PERP_BASELINE_BOTTOM " + str(pBaselineBottom) + '\n')
    f.write("PERP_BASELINE_TOP " + str(pBaselineTop) + '\n')
    f.close()
    print('Baseline at top/bottom: %f %f'%(pBaselineTop,pBaselineBottom))
    return (pBaselineTop+pBaselineBottom)/2.

def baselineStack(inps,stackReference,acqDates,doBaselines=True):
    from collections import OrderedDict
    baselineDir = os.path.join(inps.workDir,'baselines')
    os.makedirs(baselineDir, exist_ok=True)
    baselineDict = OrderedDict()
    timeDict = OrderedDict()
    datefmt = '%Y%m%d'
    t0 = datetime.datetime.strptime(stackReference, datefmt)
    reference = os.path.join(inps.slcDir, stackReference)
    for slv in acqDates:
        if slv != stackReference:
            secondary = os.path.join(inps.slcDir, slv)
            baselineDict[slv]=baselinePair(baselineDir, reference, secondary, doBaselines)
            t = datetime.datetime.strptime(slv, datefmt)
            timeDict[slv] = t - t0
        else:
            baselineDict[stackReference] = 0.0
            timeDict[stackReference] = datetime.timedelta(0.0)

    return baselineDict, timeDict

def selectPairs(inps,stackReference, secondaryDates, acuisitionDates,doBaselines=True):

    baselineDict, timeDict = baselineStack(inps, stackReference, acuisitionDates,doBaselines)
    for secondary in secondaryDates:
        print (secondary,' : ' , baselineDict[secondary])
    numDates = len(acuisitionDates)
    pairs = []
    for i in range(numDates-1):
        for j in range(i+1,numDates):
            db = np.abs(baselineDict[acuisitionDates[j]] - baselineDict[acuisitionDates[i]])
            dt = np.abs(timeDict[acuisitionDates[j]].days - timeDict[acuisitionDates[i]].days)
            if (db < inps.dbThr) and (dt < inps.dtThr):
                pairs.append((acuisitionDates[i],acuisitionDates[j]))

    plotNetwork(baselineDict, timeDict, pairs,os.path.join(inps.workDir,'pairs.pdf'))
    return pairs 


def plotNetwork(baselineDict, timeDict, pairs,save_name='pairs.png'):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.dates as mdates
    import matplotlib.pyplot as plt
    datefmt='%Y%m%d'
    fig1 = plt.figure(1)
    ax1=fig1.add_subplot(111)

    ax1.cla()
    for ni in range(len(pairs)):
#        ax1.plot(np.array([timeDict[pairs[ni][0]].days,timeDict[pairs[ni][1]].days]), 
         ax1.plot([datetime.datetime.strptime(pairs[ni][0],datefmt),
                   datetime.datetime.strptime(pairs[ni][1], datefmt)], 
                  np.array([baselineDict[pairs[ni][0]],
                            baselineDict[pairs[ni][1]]]),
                  '-ko',lw=1, ms=4, alpha=0.7, mfc='r')
  
    

    myFmt = mdates.DateFormatter('%Y-%m')
    ax1.xaxis.set_major_formatter(myFmt)

    plt.title('Baseline plot')
    plt.xlabel('Time')
    plt.ylabel('Perp. Baseline')
    plt.tight_layout()


    plt.savefig(save_name)

    ###Check degree of each SLC
    datelist = [k for k,v in list(timeDict.items())]
    connMat = np.zeros((len(pairs), len(timeDict)))
    for ni in range(len(pairs)):
        connMat[ni, datelist.index(pairs[ni][0])] = 1.0
        connMat[ni, datelist.index(pairs[ni][1])] = -1.0

    slcSum = np.sum( np.abs(connMat), axis=0)
    minDegree = np.min(slcSum)

    print('##################')
    print('SLCs with min degree connection of {0}'.format(minDegree))
    for ii in range(slcSum.size):
        if slcSum[ii] == minDegree:
            print(datelist[ii])
    print('##################')
    
    if np.linalg.matrix_rank(connMat) != (len(timeDict) - 1):
        raise Exception('The network for cascading coregistration   is not connected')

def writeJobFile(runFile):

  
    jobName = runFile + ".job"
    dirName = os.path.dirname(runFile)
    with open(runFile) as ff:
        nodes = len(ff.readlines())
    if nodes >maxNodes:
        nodes = maxNodes

    f = open (jobName,'w')
    f.write('#!/bin/bash '+ '\n')
    f.write('#PBS -N Parallel_GNU'+ '\n')
    f.write('#PBS -l nodes=' + str(nodes) + '\n')

    jobTxt='''#PBS -V
#PBS -l walltime=05:00:00
#PBS -q default

echo Working directory is $PBS_O_WORKDIR
cd $PBS_O_WORKDIR

echo Running on host `hostname`
echo Time is `date`

### Define number of processors
NPROCS=`wc -l < $PBS_NODEFILE`
echo This job has allocated $NPROCS cpus

# Tell me which nodes it is run on
echo " "
echo This jobs runs on the following processors:
echo `cat $PBS_NODEFILE`
echo " "

# 
# Run the parallel with the nodelist and command file
#

'''
    f.write(jobTxt+ '\n')
    f.write('parallel --sshloginfile $PBS_NODEFILE  -a '+runFile+'\n')
    f.write('')
    f.close()


def main(iargs=None):
    '''nothing to do'''

if __name__ == "__main__":
       
    # Main engine  
    main()
       

