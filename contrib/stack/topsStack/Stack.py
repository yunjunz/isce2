#!/usr/bin/env python3
########################
#Author: Heresh Fattahi

#######################

import os, glob , sys
import  datetime


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
        self.misreg_az = None
        self.misreg_rng = None
        self.multilook_tool = None
        self.no_data_value = None

    def Sentinel1_TOPS(self,function):
        self.f.write('##########################'+'\n')
        self.f.write(function+'\n')
        self.f.write('Sentinel1_TOPS : ' + '\n')
        self.f.write('dirname : ' + self.dirName+'\n')
        self.f.write('swaths : ' + self.swaths+'\n')

        if self.orbit_type == 'precise':
            self.f.write('orbitdir : '+self.orbit_dirname+'\n')
        else:
            self.f.write('orbit : '+self.orbit_file+'\n')

        self.f.write('outdir : ' + self.outDir + '\n')
        self.f.write('auxdir : ' + self.aux_dirname + '\n')
        if self.bbox is not None:
            self.f.write('bbox : ' + self.bbox + '\n')
        self.f.write('pol : ' + self.polarization + '\n')
        self.f.write('##########################' + '\n')

    def computeAverageBaseline(self, function):
        self.f.write('##########################'+'\n')
        self.f.write(function + '\n')
        self.f.write('computeBaseline : '+'\n')
        self.f.write('reference : ' + self.reference + '\n')
        self.f.write('secondary : ' + self.secondary + '\n')
        self.f.write('baseline_file : ' + self.baselineFile + '\n')

    def computeGridBaseline(self, function):
        self.f.write('##########################'+'\n')
        self.f.write(function + '\n')
        self.f.write('baselineGrid : '+'\n')
        self.f.write('reference : ' + self.reference + '\n')
        self.f.write('secondary : ' + self.secondary + '\n')
        self.f.write('baseline_file : ' + self.baselineFile + '\n')

    def topo(self,function):
        self.f.write('##########################'+'\n')
        self.f.write('#Call topo to produce reference geometry files'+'\n')
        self.f.write(function + '\n')
        self.f.write('topo : ' + '\n')
        self.f.write('reference : ' + self.outDir + '\n')
        self.f.write('dem : ' + self.dem + '\n')
        self.f.write('geom_referenceDir : ' + self.geom_referenceDir + '\n')
        self.f.write('##########################' + '\n')

    def geo2rdr(self,function):
        self.f.write('##########################' + '\n')
        self.f.write(function + '\n')
        self.f.write('geo2rdr :' + '\n')
        self.f.write('secondary : ' + self.secondaryDir + '\n')
        self.f.write('reference : ' + self.referenceDir + '\n')
        self.f.write('geom_referenceDir : ' + self.geom_reference + '\n')
        self.f.write('coregSLCdir : ' + self.coregSecondaryDir + '\n')
        self.f.write('overlap : ' + self.overlapTrueOrFalse + '\n')
        if self.useGPU:
            self.f.write('useGPU : True \n')
        else:
            self.f.write('useGPU : False\n')
        if self.misreg_az is not None:
            self.f.write('azimuth_misreg : ' + self.misreg_az + '\n')
        if self.misreg_rng is not None:
            self.f.write('range_misreg : ' + self.misreg_rng + '\n')

    def resamp_withCarrier(self,function):
        self.f.write('##########################' + '\n')
        self.f.write(function + '\n')
        self.f.write('resamp_withCarrier : ' + '\n')
        self.f.write('secondary : ' + self.secondaryDir + '\n')
        self.f.write('reference : ' + self.referenceDir + '\n')
       #self.f.write('interferogram_prefix :' + self.interferogram_prefix + '\n')
        self.f.write('coregdir : ' + self.coregSecondaryDir + '\n')
        self.f.write('overlap : ' + self.overlapTrueOrFalse + '\n')
        if self.misreg_az is not None:
            self.f.write('azimuth_misreg : ' + self.misreg_az + '\n')
        if self.misreg_rng is not None:
            self.f.write('range_misreg : ' + self.misreg_rng + '\n')

    def generateIgram(self, function):
        self.f.write('###################################'+'\n')
        self.f.write(function + '\n')
        self.f.write('generateIgram : ' + '\n')
        self.f.write('reference : ' + self.referenceDir + '\n')
        self.f.write('secondary : ' + self.secondaryDir + '\n')
        self.f.write('interferogram : ' + self.interferogramDir + '\n')
        self.f.write('flatten : ' + self.flatten + '\n')
        self.f.write('interferogram_prefix : ' + self.interferogram_prefix +'\n')
        self.f.write('overlap : ' + self.overlapTrueOrFalse + '\n')
        if self.misreg_az is not None:
            self.f.write('azimuth_misreg : ' + self.misreg_az + '\n')
        if self.misreg_rng is not None:
            self.f.write('range_misreg : ' + self.misreg_rng + '\n')
        self.f.write('###################################' + '\n')

    def overlap_withDEM(self,function):

        self.f.write('###################################'+'\n')
        self.f.write(function + '\n')
        self.f.write('overlap_withDEM : '+'\n')
        self.f.write('interferogram : ' + self.interferogramDir +'\n')
        self.f.write('reference_dir : ' + self.referenceDir+'\n')
        self.f.write('secondary_dir : ' + self.secondaryDir+'\n')
        self.f.write('overlap_dir : ' + self.overlapDir+'\n')

    def azimuthMisreg(self, function):
        self.f.write('###################################'+'\n')
        self.f.write(function + '\n')
        self.f.write('estimateAzimuthMisreg : ' + '\n')
        self.f.write('overlap_dir : ' + self.overlapDir + '\n')
        self.f.write('out_azimuth : ' + self.misregFile + '\n')
        self.f.write('coh_threshold : ' + self.esdCoherenceThreshold + '\n')
        self.f.write('plot : ' + self.plot + '\n')

    def rangeMisreg(self, function):
        self.f.write('###################################'+'\n')
        self.f.write(function + '\n')
        self.f.write('estimateRangeMisreg : ' + '\n')
        self.f.write('reference : ' + self.referenceDir + '\n')
        self.f.write('secondary : ' + self.secondaryDir + '\n')
        self.f.write('out_range : ' + self.misregFile + '\n')
        self.f.write('snr_threshold : ' + self.snrThreshold + '\n')

    def mergeBurst(self, function):

        self.f.write('###################################'+'\n')
        self.f.write(function + '\n')
        self.f.write('mergeBursts : ' + '\n')
        try:
            self.f.write('stack : ' + self.stack +'\n')
        except:
            pass

        self.f.write('inp_reference : ' + self.reference +'\n')
        self.f.write('dirname : ' + self.dirName + '\n')
        self.f.write('name_pattern : ' + self.namePattern + '\n')
        self.f.write('outfile : ' + self.mergedFile + '\n')
        self.f.write('method : ' + self.mergeBurstsMethod + '\n')
        self.f.write('aligned : ' + self.aligned + '\n')
        self.f.write('valid_only : ' + self.validOnly + '\n')
        self.f.write('use_virtual_files : ' + self.useVirtualFiles + '\n')
        self.f.write('multilook : ' + self.multiLook + '\n')
        self.f.write('range_looks : ' + self.rangeLooks + '\n')
        self.f.write('azimuth_looks : ' + self.azimuthLooks + '\n')
        if self.multilook_tool:
            self.f.write('multilook_tool : ' + self.multilook_tool + '\n')
        if self.no_data_value is not None:
            self.f.write('no_data_value : ' + self.no_data_value + '\n')

    def mergeSwaths(self, function):
        self.f.write('###################################'+'\n')
        self.f.write(function + '\n')
        self.f.write('mergeSwaths : ' + '\n')
        self.f.write('input : ' + self.inputDirs  +  '\n')
        self.f.write('file : ' + self.fileName + '\n')
        self.f.write('metadata : ' + self.metadata + '\n')
        self.f.write('output : ' + self.outDir +'\n')

    def multiLook(self, function):
        self.f.write('###################################'+'\n')
        self.f.write(function + '\n')
        self.f.write('looks_withDEM : ' + '\n')
        self.f.write('input : ' + self.input + '\n')
        self.f.write('output : ' + self.output + '\n')
        self.f.write('range : ' + self.rangeLooks + '\n')
        self.f.write('azimuth : ' + self.azimuthLooks + '\n')

    def FilterAndCoherence(self, function):
        self.f.write('###################################'+'\n')
        self.f.write(function + '\n')
        self.f.write('FilterAndCoherence : ' + '\n')
        self.f.write('input : ' + self.input + '\n')
        self.f.write('filt : ' + self.filtName + '\n')
        self.f.write('coh : ' + self.cohName + '\n')
        self.f.write('strength : ' + self.filtStrength + '\n')
        self.f.write('slc1 : ' + self.slc1 + '\n')
        self.f.write('slc2 : ' + self.slc2 + '\n')
        self.f.write('complex_coh : '+ self.cpxCohName + '\n')
        self.f.write('range_looks : ' + self.rangeLooks + '\n')
        self.f.write('azimuth_looks : ' + self.azimuthLooks + '\n')

    def unwrap(self, function):
        self.f.write('###################################'+'\n')
        self.f.write(function + '\n')
        self.f.write('unwrap : ' + '\n')
        self.f.write('ifg : ' + self.ifgName + '\n')
        self.f.write('unw : ' + self.unwName + '\n')
        self.f.write('coh : ' + self.cohName + '\n')
        self.f.write('nomcf : ' + self.noMCF + '\n')
        self.f.write('reference : ' + self.reference + '\n')
        self.f.write('defomax : ' + self.defoMax + '\n')
        self.f.write('rlks : ' + self.rangeLooks + '\n')
        self.f.write('alks : ' + self.azimuthLooks + '\n')
        if self.rmFilter:
            self.f.write('rmfilter : True \n')
        else:
            self.f.write('rmfilter : False\n')
        self.f.write('method : ' + self.unwMethod + '\n')

    def unwrapSnaphu(self, function):
        self.f.write('###################################'+'\n')
        self.f.write(function + '\n')
        self.f.write('unwrapSnaphu : ' + '\n')
        self.f.write('ifg : ' + self.ifgName + '\n')
        self.f.write('unw : ' + self.unwName + '\n')
        self.f.write('coh : ' + self.cohName + '\n')
        self.f.write('nomcf : ' + self.noMCF + '\n')
        self.f.write('reference : ' + self.reference + '\n')
        self.f.write('defomax : ' + self.defoMax + '\n')
        self.f.write('rlks : ' + self.rangeLooks + '\n')
        self.f.write('alks : ' + self.azimuthLooks + '\n')

    def denseOffset(self, function):
        self.f.write('###################################'+'\n')
        self.f.write(function + '\n')

        # CPU or GPU
        self.f.write('denseOffsets : ' + '\n')
        #self.f.write('DenseOffsets : ' + '\n')
        #self.f.write('cuDenseOffsets : ' + '\n')
        self.f.write('reference : ' + self.reference + '\n')
        self.f.write('secondary : ' + self.secondary + '\n')
        self.f.write('outprefix : ' + self.output + '\n')

        #self.f.write('ww : 256\n')
        #self.f.write('wh : 128\n')

    def finalize(self):
        self.f.close()


class run(object):
    """
       A class representing a run which may contain several functions
    """
    #def __init__(self):

    def configure(self,inps, runName):
        for k in inps.__dict__.keys():
            setattr(self, k, inps.__dict__[k])
        self.runDir = os.path.join(self.work_dir, 'run_files')
        os.makedirs(self.runDir, exist_ok=True)

        self.run_outname = os.path.join(self.runDir, runName)
        print ('writing ', self.run_outname)

        self.config_path = os.path.join(self.work_dir,'configs')
        os.makedirs(self.config_path, exist_ok=True)

        self.runf= open(self.run_outname,'w')

    def unpackSLC(self, acquisitionDates, safe_dict):
        swath_path = self.work_dir
        os.makedirs(self.config_path, exist_ok=True)

        for slcdate in acquisitionDates:
            configName = os.path.join(self.config_path,'config_unpack_'+slcdate)
            configObj = config(configName)
            configObj.configure(self)
            configObj.dirName = safe_dict[slcdate].safe_file
            configObj.orbit_file = safe_dict[slcdate].orbit
            configObj.orbit_type = safe_dict[slcdate].orbitType
            configObj.swaths = self.swath_num
            configObj.outDir = os.path.join(self.work_dir, 'slc/' + slcdate)
            configObj.geom_referenceDir = os.path.join(self.work_dir, 'geom_slc/' + slcdate)
            configObj.dem = os.path.join(self.work_dir, configObj.dem)
            configObj.Sentinel1_TOPS('[Function-1]')
            configObj.topo('[Function-2]')
            configObj.finalize()
            del configObj
            self.runf.write(self.text_cmd + 'SentinelWrapper.py -c ' + configName + '\n')

    def unpackStackReferenceSLC(self, safe_dict):
        swath_path = self.work_dir
        os.makedirs(self.config_path, exist_ok=True)
        configName = os.path.join(self.config_path,'config_reference')
        configObj = config(configName)
        configObj.configure(self)
        configObj.dirName = safe_dict[self.reference_date].safe_file
        configObj.orbit_file = safe_dict[self.reference_date].orbit
        configObj.orbit_type = safe_dict[self.reference_date].orbitType
        configObj.swaths = self.swath_num
        configObj.outDir = os.path.join(self.work_dir, 'reference')
        configObj.geom_referenceDir = os.path.join(self.work_dir, 'geom_reference')
        configObj.dem = os.path.join(self.work_dir, configObj.dem)
        configObj.Sentinel1_TOPS('[Function-1]')
        configObj.topo('[Function-2]')
        configObj.finalize()
        del configObj
        self.runf.write(self.text_cmd + 'SentinelWrapper.py -c ' + configName + '\n')

    def unpackSecondarysSLC(self,  stackReferenceDate, secondaryList, safe_dict):

        for secondary in secondaryList:
            configName = os.path.join(self.config_path,'config_secondary_'+secondary)
            outdir = os.path.join(self.work_dir,'secondarys/'+secondary)
            configObj = config(configName)
            configObj.configure(self)
            configObj.dirName = safe_dict[secondary].safe_file
            configObj.orbit_file = safe_dict[secondary].orbit
            configObj.orbit_type = safe_dict[secondary].orbitType
            configObj.swaths = self.swath_num
            configObj.outDir = outdir
            configObj.Sentinel1_TOPS('[Function-1]')
            configObj.finalize()
            del configObj
            self.runf.write(self.text_cmd + 'SentinelWrapper.py -c ' + configName+'\n')

    def averageBaseline(self, stackReferenceDate, secondaryList):

        for secondary in secondaryList:
            configName = os.path.join(self.config_path,'config_baseline_'+secondary)
            configObj = config(configName)
            configObj.configure(self)
            configObj.reference = os.path.join(self.work_dir,'reference/')
            configObj.secondary = os.path.join(self.work_dir,'secondarys/'+secondary)
            configObj.baselineFile = os.path.join(self.work_dir,'baselines/' + stackReferenceDate +'_' + secondary + '/' + stackReferenceDate +'_'+ secondary  + '.txt')
            configObj.computeAverageBaseline('[Function-1]')
            configObj.finalize()
            del configObj
            self.runf.write(self.text_cmd + 'SentinelWrapper.py -c ' + configName+'\n')

    def gridBaseline(self, stackReferenceDate, secondaryList):
        for secondary in secondaryList:
            configName = os.path.join(self.config_path,'config_baselinegrid_'+secondary)
            configObj = config(configName)
            configObj.configure(self)
            configObj.reference = os.path.join(self.work_dir,'reference/')
            configObj.secondary = os.path.join(self.work_dir,'secondarys/'+secondary)
            configObj.baselineFile = os.path.join(self.work_dir, 'merged/baselines/' + secondary + '/' + secondary )
            configObj.computeGridBaseline('[Function-1]')
            configObj.finalize()
            del configObj
            self.runf.write(self.text_cmd + 'SentinelWrapper.py -c ' + configName+'\n')
        # also add the reference in itself to be consistent with the SLC dir
        configName = os.path.join(self.config_path,'config_baselinegrid_reference')
        configObj = config(configName)
        configObj.configure(self)
        configObj.reference = os.path.join(self.work_dir,'reference/')
        configObj.secondary = os.path.join(self.work_dir,'reference/')
        configObj.baselineFile = os.path.join(self.work_dir, 'merged/baselines/' + stackReferenceDate + '/' + stackReferenceDate)
        configObj.computeGridBaseline('[Function-1]')
        configObj.finalize()
        del configObj
        self.runf.write(self.text_cmd + 'SentinelWrapper.py -c ' + configName+'\n')


    def extractOverlaps(self):

        self.runf.write(self.text_cmd + 'subsetReference.py -m ' + os.path.join(self.work_dir, 'reference') + ' -g ' + os.path.join(self.work_dir, 'geom_reference') + '\n')


    def geo2rdr_offset(self, secondaryList, fullBurst='False'):

        for secondary in secondaryList:
            reference = self.reference_date
            if fullBurst == 'True':
                configName = os.path.join(self.config_path, 'config_fullBurst_geo2rdr_' + secondary)
            else:
                configName = os.path.join(self.config_path, 'config_overlap_geo2rdr_'+secondary)
            ###########
            configObj = config(configName)
            configObj.configure(self)
            configObj.secondaryDir = os.path.join(self.work_dir, 'secondarys/'+secondary)
            configObj.referenceDir = os.path.join(self.work_dir, 'reference')
            configObj.geom_reference = os.path.join(self.work_dir, 'geom_reference')
            configObj.coregSecondaryDir = os.path.join(self.work_dir, 'coreg_secondarys/'+secondary)
            if fullBurst == 'True':
                configObj.misreg_az = os.path.join(self.work_dir, 'misreg/azimuth/dates/' + secondary + '.txt')
                configObj.misreg_rng = os.path.join(self.work_dir, 'misreg/range/dates/' + secondary + '.txt')
                configObj.overlapTrueOrFalse = 'False'
            else:
                configObj.overlapTrueOrFalse = 'True'
            configObj.geo2rdr('[Function-1]')
            configObj.finalize()
            del configObj
            self.runf.write(self.text_cmd + 'SentinelWrapper.py -c ' + configName + '\n')

    def resample_with_carrier(self, secondaryList, fullBurst='False'):
        for secondary in secondaryList:
            reference = self.reference_date
            if fullBurst == 'True':
                configName = os.path.join(self.config_path, 'config_fullBurst_resample_' + secondary)
            else:
                configName = os.path.join(self.config_path, 'config_overlap_resample_' + secondary)
            ###########
            configObj = config(configName)
            configObj.configure(self)
            configObj.secondaryDir = os.path.join(self.work_dir, 'secondarys/' + secondary)
            configObj.referenceDir = os.path.join(self.work_dir, 'reference')
            configObj.coregSecondaryDir = os.path.join(self.work_dir, 'coreg_secondarys/' + secondary)
            configObj.interferogram_prefix = 'coarse'
            configObj.referenceDir = os.path.join(self.work_dir, 'reference')
            if fullBurst == 'True':
                configObj.misreg_az = os.path.join(self.work_dir, 'misreg/azimuth/dates/' + secondary + '.txt')
                configObj.misreg_rng = os.path.join(self.work_dir, 'misreg/range/dates/' + secondary + '.txt')
                configObj.overlapTrueOrFalse = 'False'
            else:
                configObj.overlapTrueOrFalse = 'True'
            configObj.resamp_withCarrier('[Function-1]')
            configObj.finalize()
            del configObj
            self.runf.write(self.text_cmd + 'SentinelWrapper.py -c ' + configName + '\n')

    def pairs_misregistration(self, dateList, safe_dict):
        # generating overlap interferograms, estimate azimuth misregistration for each pair:
        pairs = []
        num_overlap_connections = int(self.num_overlap_connections) + 1
        for i in range(len(dateList)-1):
            for j in range(i+1,i+num_overlap_connections):
                if j<len(dateList):
                    pairs.append((dateList[i],dateList[j]))

        for date in dateList:
            safe_dict[date].slc = os.path.join(self.work_dir , 'coreg_secondarys/'+date)
            safe_dict[date].slc_overlap = os.path.join(self.work_dir , 'coreg_secondarys/'+date)
        safe_dict[self.reference_date].slc = os.path.join(self.work_dir , 'reference')
        safe_dict[self.reference_date].slc_overlap = os.path.join(self.work_dir , 'reference')
        for pair in pairs:
            reference = pair[0]
            secondary = pair[1]
            interferogramDir = os.path.join(self.work_dir, 'coarse_interferograms/'+reference+'_'+secondary)
            configName = os.path.join(self.config_path ,'config_misreg_'+reference+'_'+secondary)
            configObj = config(configName)
            configObj.configure(self)
            configObj.referenceDir = safe_dict[reference].slc_overlap
            configObj.secondaryDir = safe_dict[secondary].slc_overlap
            configObj.interferogramDir = interferogramDir
            configObj.interferogram_prefix = 'int'
            configObj.flatten = 'False'
            configObj.overlapTrueOrFalse = 'True'
            configObj.generateIgram('[Function-1]')
            ########################
            configObj.reference = interferogramDir + '/' + 'coarse_ifg'
            configObj.referenceDir = safe_dict[reference].slc_overlap
            configObj.secondaryDir = safe_dict[secondary].slc_overlap
            configObj.overlapDir = os.path.join(self.work_dir, 'ESD/' + reference + '_' + secondary)
            configObj.overlap_withDEM('[Function-2]')
            ########################

            configObj.misregFile = os.path.join(self.work_dir , 'misreg/azimuth/pairs/' + reference+'_'+secondary + '/' + reference+'_'+secondary + '.txt')
            configObj.azimuthMisreg('[Function-3]')
            ########################
            configObj.misregFile = os.path.join(self.work_dir , 'misreg/range/pairs/' + reference+'_'+secondary + '/' + reference+'_'+secondary + '.txt')
            configObj.rangeMisreg('[Function-4]')
            configObj.finalize()

            self.runf.write(self.text_cmd + 'SentinelWrapper.py -c ' + configName + '\n')
            ########################



    def timeseries_misregistration(self):
        #inverting the misregistration offsets of the overlap pairs to estimate the offsets of each date
        self.runf.write(self.text_cmd + 'invertMisreg.py -i ' + os.path.join(self.work_dir,'misreg/azimuth/pairs/') + ' -o ' + os.path.join(self.work_dir,'misreg/azimuth/dates/') + '\n')
        self.runf.write(self.text_cmd + 'invertMisreg.py -i ' + os.path.join(self.work_dir,'misreg/range/pairs/') + ' -o ' + os.path.join(self.work_dir,'misreg/range/dates/') + '\n')

    def extractStackValidRegion(self):
        referenceDir = os.path.join(self.work_dir, 'reference')
        coregSecondaryDir = os.path.join(self.work_dir, 'coreg_secondarys')
        self.runf.write(self.text_cmd + 'extractCommonValidRegion.py -m ' + referenceDir + ' -s ' + coregSecondaryDir + '\n')

    def generate_burstIgram(self, dateList, safe_dict, pairs):

        for date in dateList:
            safe_dict[date].slc = os.path.join(self.work_dir, 'coreg_secondarys/'+date)
        safe_dict[self.reference_date].slc = os.path.join(self.work_dir , 'reference')
        for pair in pairs:
            reference = pair[0]
            secondary = pair[1]
            interferogramDir = os.path.join(self.work_dir, 'interferograms/' + reference + '_' + secondary)
            configName = os.path.join(self.config_path ,'config_generate_igram_' + reference + '_' + secondary)
            configObj = config(configName)
            configObj.configure(self)
            configObj.referenceDir = safe_dict[reference].slc
            configObj.secondaryDir = safe_dict[secondary].slc
            configObj.interferogramDir = interferogramDir
            configObj.interferogram_prefix = 'fine'
            configObj.flatten = 'False'
            configObj.overlapTrueOrFalse = 'False'
            configObj.generateIgram('[Function-1]')
            configObj.finalize()
            del configObj

            self.runf.write(self.text_cmd + 'SentinelWrapper.py -c ' + configName + '\n')

    def igram_mergeBurst(self, dateList, safe_dict, pairs):
        for date in dateList:
            safe_dict[date].slc = os.path.join(self.work_dir, 'coreg_secondarys/'+date)
        safe_dict[self.reference_date].slc = os.path.join(self.work_dir , 'reference')
        for pair in pairs:
            reference = pair[0]
            secondary = pair[1]
            interferogramDir = os.path.join(self.work_dir, 'interferograms/' + reference + '_' + secondary)
            mergedDir = os.path.join(self.work_dir, 'merged/interferograms/' + reference + '_' + secondary)
            configName = os.path.join(self.config_path ,'config_merge_igram_' + reference + '_' + secondary)
            configObj = config(configName)
            configObj.configure(self)
            configObj.interferogram_prefix = 'fine'
            configObj.reference = interferogramDir
            configObj.dirName = interferogramDir
            configObj.namePattern = 'fine*int'
            configObj.mergedFile = mergedDir + '/' + configObj.interferogram_prefix + '.int'
            configObj.mergeBurstsMethod = 'top'
            configObj.aligned = 'True'
            configObj.validOnly = 'True'
            configObj.useVirtualFiles = 'True'
            configObj.multiLook = 'True'
            configObj.stack = os.path.join(self.work_dir, 'stack')
            configObj.mergeBurst('[Function-1]')
            configObj.finalize()
            del configObj

            self.runf.write(self.text_cmd + 'SentinelWrapper.py -c ' + configName + '\n')

    def mergeSecondarySLC(self, secondaryList, virtual='True'):

        for secondary in secondaryList:
            configName = os.path.join(self.config_path,'config_merge_' + secondary)
            configObj = config(configName)
            configObj.configure(self)
            configObj.stack = os.path.join(self.work_dir, 'stack')
            configObj.reference = os.path.join(self.work_dir, 'coreg_secondarys/' + secondary)
            configObj.dirName = configObj.reference
            configObj.namePattern = 'burst*slc'
            configObj.mergedFile = os.path.join(self.work_dir, 'merged/SLC/' + secondary + '/' + secondary + '.slc')
            configObj.mergeBurstsMethod = 'top'
            configObj.aligned = 'True'
            configObj.validOnly = 'True'
            configObj.useVirtualFiles = virtual
            configObj.multiLook = 'False'
            configObj.stack = os.path.join(self.work_dir, 'stack')
            configObj.mergeBurst('[Function-1]')
            configObj.finalize()
            self.runf.write(self.text_cmd + 'SentinelWrapper.py -c ' + configName + '\n')

    def mergeReference(self, stackReference, virtual='True'):

        configName = os.path.join(self.config_path,'config_merge_' + stackReference)
        configObj = config(configName)
        configObj.configure(self)
        configObj.stack = os.path.join(self.work_dir, 'stack')
        configObj.reference = os.path.join(self.work_dir, 'reference')
        configObj.dirName = configObj.reference
        configObj.namePattern = 'burst*slc'
        configObj.mergedFile = os.path.join(self.work_dir, 'merged/SLC/' + stackReference + '/' + stackReference + '.slc')
        configObj.mergeBurstsMethod = 'top'
        configObj.aligned = 'False'
        configObj.validOnly = 'True'
        configObj.useVirtualFiles = virtual
        configObj.multiLook = 'False'
        configObj.mergeBurst('[Function-1]')
        configObj.finalize()
        self.runf.write(self.text_cmd + 'SentinelWrapper.py -c ' + configName + '\n')

        geometryList = ['lat*rdr', 'lon*rdr', 'los*rdr', 'hgt*rdr', 'shadowMask*rdr','incLocal*rdr']
        multiookToolDict = {'lat*rdr': 'gdal', 'lon*rdr': 'gdal', 'los*rdr': 'gdal' , 'hgt*rdr':"gdal", 'shadowMask*rdr':"isce",'incLocal*rdr':"gdal"}
        noDataDict = {'lat*rdr': '0', 'lon*rdr': '0', 'los*rdr': '0' , 'hgt*rdr':None, 'shadowMask*rdr':None,'incLocal*rdr':"0"}

        for i in range(len(geometryList)):
            pattern = geometryList[i]
            configName = os.path.join(self.config_path,'config_merge_' + pattern.split('*')[0])
            configObj = config(configName)
            configObj.configure(self)
            configObj.reference = os.path.join(self.work_dir, 'reference')
            configObj.dirName = os.path.join(self.work_dir, 'geom_reference')
            configObj.namePattern = pattern
            configObj.mergedFile = os.path.join(self.work_dir, 'merged/geom_reference/' + pattern.split('*')[0] + '.' + pattern.split('*')[1])
            configObj.mergeBurstsMethod = 'top'
            configObj.aligned = 'False'
            configObj.validOnly = 'False'
            configObj.useVirtualFiles = virtual
            configObj.multiLook = 'True'
            configObj.multilook_tool = multiookToolDict[pattern]
            configObj.no_data_value = noDataDict[pattern]
            configObj.stack = os.path.join(self.work_dir, 'stack')
            configObj.mergeBurst('[Function-1]')
            configObj.finalize()
            self.runf.write(self.text_cmd + 'SentinelWrapper.py -c ' + configName + '\n')

    def mergeSLC(self, aquisitionDates, virtual='True'):

        for slcdate in aquisitionDates:
            configName = os.path.join(self.config_path,'config_merge_' + slcdate)
            configObj = config(configName)
            configObj.configure(self)
            configObj.reference = os.path.join(self.work_dir, 'slc/' + slcdate)
            configObj.dirName = configObj.reference
            configObj.namePattern = 'burst*slc'
            configObj.mergedFile = os.path.join(self.work_dir, 'merged/slc/' + slcdate + '/' + slcdate + '.slc')
            configObj.mergeBurstsMethod = 'top'
            configObj.aligned = 'False'
            configObj.validOnly = 'True'
            configObj.useVirtualFiles = virtual
            configObj.multiLook = 'False'
            configObj.stack = os.path.join(self.work_dir, 'stack')
            configObj.mergeBurst('[Function-1]')
            configObj.finalize()
            self.runf.write(self.text_cmd + 'SentinelWrapper.py -c ' + configName + '\n')

            geometryList = ['lat*rdr', 'lon*rdr', 'los*rdr', 'hgt*rdr', 'shadowMask*rdr','incLocal*rdr']
            for i in range(len(geometryList)):
                pattern = geometryList[i]
                configName = os.path.join(self.config_path,'config_merge_' + slcdate + '_' +pattern.split('*')[0])
                configObj = config(configName)
                configObj.configure(self)
                configObj.reference = os.path.join(self.work_dir, 'slc/' + slcdate)
                configObj.dirName = os.path.join(self.work_dir, 'geom_slc/' + slcdate)
                configObj.namePattern = pattern
                configObj.mergedFile = os.path.join(self.work_dir, 'merged/geom_slc/' + slcdate + '/' + pattern.split('*')[0] + '.' + pattern.split('*')[1])
                configObj.mergeBurstsMethod = 'top'
                configObj.aligned = 'False'
                configObj.validOnly = 'False'
                configObj.useVirtualFiles = virtual
                configObj.multiLook = 'False'
                configObj.stack = os.path.join(self.work_dir, 'stack')
                configObj.mergeBurst('[Function-1]')
                configObj.finalize()
                self.runf.write(self.text_cmd + 'SentinelWrapper.py -c ' + configName + '\n')

    def filter_coherence(self, pairs):

        for pair in pairs:
            reference = pair[0]
            secondary = pair[1]
            mergedDir = os.path.join(self.work_dir, 'merged/interferograms/' + reference + '_' + secondary)
            mergedSLCDir = os.path.join(self.work_dir, 'merged/SLC')
            configName = os.path.join(self.config_path, 'config_igram_filt_coh_' + reference + '_' + secondary)
            configObj = config(configName)
            configObj.configure(self)
            configObj.input = os.path.join(mergedDir, 'fine.int')
            configObj.filtName = os.path.join(mergedDir, 'filt_fine.int')
            configObj.cohName = os.path.join(mergedDir, 'filt_fine.cor')
            configObj.slc1 = os.path.join(mergedSLCDir, '{}/{}.slc.full'.format(reference, reference))
            configObj.slc2 = os.path.join(mergedSLCDir, '{}/{}.slc.full'.format(secondary, secondary))
            configObj.cpxCohName = os.path.join(mergedDir, 'fine.cor')
            if int(self.rangeLooks) * int(self.azimuthLooks) == 1:
                configObj.cpxCohName += '.full'
            #configObj.filtStrength = str(self.filtStrength)
            configObj.FilterAndCoherence('[Function-1]')
            configObj.finalize()
            self.runf.write(self.text_cmd + 'SentinelWrapper.py -c ' + configName + '\n')

    def unwrap(self, pairs):
        for pair in pairs:
            reference = pair[0]
            secondary = pair[1]
            mergedDir = os.path.join(self.work_dir, 'merged/interferograms/' + reference + '_' + secondary)
            configName = os.path.join(self.config_path ,'config_igram_unw_' + reference + '_' + secondary)
            configObj = config(configName)
            configObj.configure(self)
            configObj.ifgName = os.path.join(mergedDir,'filt_fine.int')
            configObj.cohName = os.path.join(mergedDir,'filt_fine.cor')
            configObj.unwName = os.path.join(mergedDir,'filt_fine.unw')
            configObj.noMCF = noMCF
            configObj.rmFilter = self.rmFilter
            configObj.reference = os.path.join(self.work_dir,'reference')
            configObj.defoMax = defoMax
            configObj.unwMethod = self.unwMethod
            configObj.unwrap('[Function-1]')
            configObj.finalize()
            self.runf.write(self.text_cmd + 'SentinelWrapper.py -c ' + configName + '\n')

    def denseOffsets(self, pairs):

        for pair in pairs:
            reference = pair[0]
            secondary = pair[1]
            configName = os.path.join(self.config_path ,'config_denseOffset_' + reference + '_' + secondary)
            configObj = config(configName)
            configObj.configure(self)
            configObj.reference = os.path.join(self.work_dir, 'merged/SLC/' + reference + '/' + reference + '.slc.full')
            configObj.secondary = os.path.join(self.work_dir, 'merged/SLC/' + secondary + '/' + secondary + '.slc.full')

            configObj.output = os.path.join(self.work_dir , 'merged/dense_offsets/'+reference+'_'+secondary + '/'  + reference+'_'+secondary)
            configObj.denseOffset('[Function-1]')
            configObj.finalize()
            del configObj
            self.runf.write(self.text_cmd + 'SentinelWrapper.py -c ' + configName + '\n')


    def finalize(self):
        self.runf.close()
        #writeJobFile(self.run_outname)

class sentinelSLC(object):
    """
        A Class representing the SLCs
    """
    def __init__(self, safe_file=None, orbit_file=None ,slc=None ):
        self.safe_file = safe_file
        self.orbit = orbit_file
        self.slc = slc

    def get_dates(self):
        datefmt = "%Y%m%dT%H%M%S"
        safe = os.path.basename(self.safe_file)
        fields = safe.split('_')
        self.platform = fields[0]
        self.start_date_time = datetime.datetime.strptime(fields[5], datefmt)
        self.stop_date_time = datetime.datetime.strptime(fields[6], datefmt)
        self.datetime = datetime.datetime.date(self.start_date_time)
        self.date = self.datetime.isoformat().replace('-','')

    def get_lat_lon(self):
        lats=[]
        lons=[]
        for safe in self.safe_file.split():
           from xml.etree import ElementTree as ET

           file=os.path.join(safe,'preview/map-overlay.kml')
           kmlFile = open( file, 'r' ).read(-1)
           kmlFile = kmlFile.replace( 'gx:', 'gx' )

           kmlData = ET.fromstring( kmlFile )
           document = kmlData.find('Document/Folder/GroundOverlay/gxLatLonQuad')
           pnts = document.find('coordinates').text.split()
           for pnt in pnts:
              lons.append(float(pnt.split(',')[0]))
              lats.append(float(pnt.split(',')[1]))
        self.SNWE=[min(lats),max(lats),min(lons),max(lons)]




    def getkmlQUAD(self,safe):
        # The coordinates in pnts must be specified in counter-clockwise order with the first coordinate corresponding to the lower-left corner of the overlayed image.
        # The shape described by these corners must be convex.
        # It appears this does not mean the coordinates are counter-clockwize in lon-lat reference.
        import zipfile
        from xml.etree import ElementTree as ET


        if safe.endswith('.zip'):
            zf = zipfile.ZipFile(safe,'r')
            fname = os.path.join(os.path.basename(safe).replace('zip','SAFE'), 'preview/map-overlay.kml')
            xmlstr = zf.read(fname)
            xmlstr=xmlstr.decode('utf-8')
            start = '<coordinates>'
            end = '</coordinates>'
            pnts = xmlstr[xmlstr.find(start)+len(start):xmlstr.find(end)].split()

        else:
            file=os.path.join(safe,'preview/map-overlay.kml')
            kmlFile = open( file, 'r' ).read(-1)
            kmlFile = kmlFile.replace( 'gx:', 'gx' )
            kmlData = ET.fromstring( kmlFile )
            document = kmlData.find('Document/Folder/GroundOverlay/gxLatLonQuad')
            pnts = document.find('coordinates').text.split()

        # convert the pnts to a list
        from scipy.spatial import distance as dist
        import numpy as np
        import cv2
        lats = []
        lons = []
        for pnt in pnts:
            lons.append(float(pnt.split(',')[0]))
            lats.append(float(pnt.split(',')[1]))
        pts = np.array([[a,b] for a,b in zip(lons,lats)])

        # The two points with most western longitude correspond to the left corners of the rectangle
        xSorted = pts[np.argsort(pts[:, 0]), :]
        leftMost = xSorted[:2, :]
        # the top right corner corresponds to the point which has the highest latitude of the two western most corners
        # the second point left will be the bottom left corner
        leftMost = leftMost[np.argsort(leftMost[:, 1]), :]
        (bl, tl) = leftMost


        # the two points with the most eastern longitude correspond to the right cornersof the rectangle
        rightMost = xSorted[2:, :]

        '''print("left most")
        print(leftMost)
        print("")
        print("right most")
        print(rightMost)
        print("")'''


        # now that we have the top-left coordinate, use it as an
        # anchor to calculate the Euclidean distance between the
        # top-left and right-most points; by the Pythagorean
        # theorem, the point with the largest distance will be
        # our bottom-right point
        D = dist.cdist(tl[np.newaxis], rightMost, "euclidean")[0]
        (br, tr) = rightMost[np.argsort(D)[::-1], :]

        # return the coordinates in top-left, top-right,
        # bottom-right, and bottom-left order
        temp = np.array([tl, tr, br, bl], dtype="float32")
        #print(temp)
        #print(pnts)
        pnts_new = [str(bl[0])+','+str(bl[1]),str(br[0])+','+str(br[1]) ,str(tr[0])+','+str(tr[1]),str(tl[0])+','+str(tl[1])]
        #print(pnts_new)
        #raise Exception ("STOP")
        return pnts_new

    def get_lat_lon_v2(self):

        import numpy as np
        lats = []
        lons = []

        # track the min lat and max lat in columns with the rows each time a different SAF file
        lat_frame_max = []
        lat_frame_min = []
        for safe in self.safe_file.split():
           safeObj=sentinelSLC(safe)
           pnts = safeObj.getkmlQUAD(safe)
           # The coordinates must be specified in counter-clockwise order with the first coordinate corresponding
           # to the lower-left corner of the overlayed image
           counter=0
           for pnt in pnts:
              lons.append(float(pnt.split(',')[0]))
              lats.append(float(pnt.split(',')[1]))

              # only take the bottom [0] and top [3] left coordinates
              if counter==0:
                  lat_frame_min.append(float(pnt.split(',')[1]))
              elif counter==3:
                  lat_frame_max.append(float(pnt.split(',')[1]))
              counter+=1

        self.SNWE=[min(lats),max(lats),min(lons),max(lons)]

        # checking for missing gaps, by doing a difference between end and start of frames
        # will shift the vectors such that one can diff in rows to compare start and end
        # note need to keep temps seperate as otherwize one is using the other in calculation
        temp1 = max(lat_frame_max)
        temp2 = min(lat_frame_min)
        lat_frame_min.append(temp1)
        lat_frame_min.sort()
        lat_frame_max.append(temp2)
        lat_frame_max.sort()

        # combining the frame north and south left edge
        lat_frame_min = np.transpose(np.array(lat_frame_min))
        lat_frame_max = np.transpose(np.array(lat_frame_max))
        # if the differnce between top and bottom <=0 then there is overlap

        overlap_check = (lat_frame_min-lat_frame_max)<=0
        overlap_check = overlap_check.all()
        """if overlap_check:
            print(lat_frame_min)
            print(lat_frame_max)
            print(lat_frame_min-lat_frame_max)
            print("*********overlap")
        else:
            print(lat_frame_min)
            print(lat_frame_max)
            print(lat_frame_min-lat_frame_max)
            print("gap")"""

        #raise Exception("STOP")
        self.frame_nogap=overlap_check

    def get_lat_lon_v3(self,inps):
        from isceobj.Sensor.TOPS.Sentinel1 import Sentinel1
        lats=[]
        lons=[]

        for swathnum in inps.swath_num.split():
           obj = Sentinel1()
           obj.configure()
           obj.safe = self.safe_file.split()
           obj.swathNumber = int(swathnum)
           print(obj.polarization)
           # add by Minyan
           obj.polarization='vv'
          #obj.output = '{0}-SW{1}'.format(safe,swathnum)
           obj.parse()

           s,n,w,e = obj.product.bursts[0].getBbox()
           lats.append(s);lats.append(n)
           lons.append(w);lons.append(e)

           s,n,w,e = obj.product.bursts[-1].getBbox()
           lats.append(s);lats.append(n)
           lons.append(w);lons.append(e)

        self.SNWE=[min(lats),max(lats),min(lons),max(lons)]

    def get_orbit(self, orbitDir, workDir, margin=60.0):
        margin = datetime.timedelta(seconds=margin)
        datefmt = "%Y%m%dT%H%M%S"
        orbit_files = glob.glob(os.path.join(orbitDir,  self.platform + '*.EOF'))
        if len(orbit_files) == 0:
            orbit_files = glob.glob(os.path.join(orbitDir, '*/{0}*.EOF'.format(self.platform)))

        match = False
        for orbit in orbit_files:
           orbit = os.path.basename(orbit)
           fields = orbit.split('_')
           orbit_start_date_time = datetime.datetime.strptime(fields[6].replace('V',''), datefmt) + margin
           orbit_stop_date_time = datetime.datetime.strptime(fields[7].replace('.EOF',''), datefmt) - margin

           if self.start_date_time >= orbit_start_date_time and self.stop_date_time < orbit_stop_date_time:
               self.orbit = os.path.join(orbitDir,orbit)
               self.orbitType = 'precise'
               match = True
               break
        if not match:
           print ("*****************************************")
           print (self.date)
           print ("orbit was not found in the "+orbitDir) # It should go and look online
           print ("downloading precise or restituted orbits ...")

           restitutedOrbitDir = os.path.join(workDir ,'orbits/' + self.date)
           if os.path.exists(restitutedOrbitDir):
              orbitFile = glob.glob(os.path.join(restitutedOrbitDir,'*.EOF'))[0]

              #fields = orbitFile.split('_')
              fields = os.path.basename(orbitFile).split('_')
              orbit_start_date_time = datetime.datetime.strptime(fields[6].replace('V',''), datefmt)
              orbit_stop_date_time = datetime.datetime.strptime(fields[7].replace('.EOF',''), datefmt)
              if self.start_date_time >= orbit_start_date_time and self.stop_date_time < orbit_stop_date_time:
                  print ("restituted orbit already exists.")
                  self.orbit =  orbitFile
                  self.orbitType = 'restituted'

           #if not os.path.exists(restitutedOrbitDir):
           else:
              os.makedirs(restitutedOrbitDir)

              cmd = 'fetchOrbit.py -i ' + self.safe_file + ' -o ' + restitutedOrbitDir
              print(cmd)
              os.system(cmd)
              orbitFile = glob.glob(os.path.join(restitutedOrbitDir,'*.EOF'))
              self.orbit =  orbitFile[0]
              self.orbitType = 'restituted'



# an example for writing job files when using clusters

"""
def writeJobFile(runFile):

  jobName = runFile + '.job'
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
#PBS -m bae -M hfattahi@gps.caltech.edu

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
  f.write('parallel --sshloginfile $PBS_NODEFILE  -a ' + os.path.basename(runFile) + '\n')
  f.write('')
  f.close()

"""
