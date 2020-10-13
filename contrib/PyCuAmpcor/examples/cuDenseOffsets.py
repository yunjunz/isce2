#!/usr/bin/env python3

# Author: Minyan Zhong, Lijun Zhu
# Add geometry preparation, Zhang Yunjun, 07-Oct-2020


import os
import sys
import time
import argparse
import numpy as np

import isce
import isceobj
from isceobj.Util.decorators import use_api
from isceobj.Util.ImageUtil import ImageLib as IML
from contrib.PyCuAmpcor.PyCuAmpcor import PyCuAmpcor


EXAMPLE = '''example
  cuDenseOffsets.py -m ./SLC/20151120/20151120.slc.full -s ./SLC/20151214/20151214.slc.full
  cuDenseOffsets.py -m ./SLC/20151120/20151120.slc.full -s ./SLC/20151214/20151214.slc.full --outprefix ./offsets/20151120_20151214/offset --ww 256 --wh 256 --oo 32 --kw 300 --kh 100 --nwac 100 --nwdc 1 --sw 8 --sh 8 --gpuid 2

  # offset and its geometry
  cuDenseOffsets.py -m ./SLC/20151120/20151120.slc.full -s ./SLC/20151214/20151214.slc.full --outprefix ./offsets/20151120_20151214/offset --ww 256 --wh 256 --oo 32 --kw 300 --kh 100 --nwac 100 --nwdc 1 --sw 8 --sh 8 --gpuid 2 --full-geom ./geom_reference --out-geom ./offset/geom_reference
'''


def createParser():
    '''
    Command line parser.
    '''


    parser = argparse.ArgumentParser(description='Generate offset field between two SLCs',
                                     formatter_class=argparse.RawTextHelpFormatter,
                                     epilog=EXAMPLE)
    parser.add_argument('-m','--reference', type=str, dest='reference', required=True,
                        help='Reference image')
    parser.add_argument('-s', '--secondary',type=str, dest='secondary', required=True,
                        help='Secondary image')
    parser.add_argument('-l', '--lat',type=str, dest='lat', required=False,
                        help='Latitude')
    parser.add_argument('-L', '--lon',type=str, dest='lon', required=False,
                        help='Longitude')
    parser.add_argument('--los',type=str, dest='los', required=False,
                        help='Line of Sight')
    parser.add_argument('-x', '--referencexml',type=str, dest='referencexml', required=False,
                        help='Reference Image XML File')

    parser.add_argument('--op','--outprefix','--output-prefix', type=str, dest='outprefix',
                        default='offset', required=True,
                        help='Output prefix, default: offset.')
    parser.add_argument('--os','--outsuffix', type=str, dest='outsuffix', default='',
                        help='Output suffix, default:.')
    parser.add_argument('--ww', type=int, dest='winwidth', default=64,
                        help='Window width (default: %(default)s).')
    parser.add_argument('--wh', type=int, dest='winhgt', default=64,
                        help='Window height (default: %(default)s).')

    parser.add_argument('--sw', type=int, dest='srcwidth', default=20, choices=range(8, 33),
                        help='Search window width (default: %(default)s).')
    parser.add_argument('--sh', type=int, dest='srchgt', default=20, choices=range(8, 33),
                        help='Search window height (default: %(default)s).')
    parser.add_argument('--mm', type=int, dest='margin', default=50,
                        help='Margin (default: %(default)s).')

    parser.add_argument('--kw', type=int, dest='skipwidth', default=64,
                        help='Skip across (default: %(default)s).')
    parser.add_argument('--kh', type=int, dest='skiphgt', default=64,
                        help='Skip down (default: %(default)s).')

    parser.add_argument('--raw-osf','--raw-over-samp-factor', type=int, dest='raw_oversample',
                        default=2, choices=range(2,5),
                        help='raw data oversampling factor (default: %(default)s).')

    gross = parser.add_argument_group('Initial gross offset')
    gross.add_argument('-g','--gross', type=int, dest='gross', default=0,
                       help='Use gross offset or not')
    gross.add_argument('--aa', type=int, dest='azshift', default=0,
                       help='Gross azimuth offset (default: %(default)s).')
    gross.add_argument('--rr', type=int, dest='rgshift', default=0,
                       help='Gross range offset (default: %(default)s).')

    corr = parser.add_argument_group('Correlation surface')
    corr.add_argument('--corr-stat-size', type=int, dest='corr_stat_win_size', default=21,
                      help='Zoom-in window size of the correlation surface for statistics(snr/cov) (default: %(default)s).')
    corr.add_argument('--corr-win-size', type=int, dest='corr_win_size', default=-1,
                      help='Zoom-in window size of the correlation surface for oversampling (default: %(default)s).')
    corr.add_argument('--corr-osf', '--oo', '--corr-over-samp-factor', type=int, dest='corr_oversample', default=32,
                      help = 'Oversampling factor of the zoom-in correlation surface (default: %(default)s).')
    corr.add_argument('--corr-osm', '--corr-over-samp-method', type=int, dest='corr_oversamplemethod', default=0,
                      help = 'Oversampling method for the correlation surface 0=fft, 1=sinc (default: %(default)s).')

    geom = parser.add_argument_group('Geometry', 'generate corresponding geometry datasets ')
    geom.add_argument('--full-geom', dest='full_geometry_dir', type=str,
                      help='(Input) Directory of geometry files in full resolution.')
    geom.add_argument('--out-geom', dest='out_geometry_dir', type=str,
                      help='(Output) Directory of geometry files corresponding to the offset field.')

    parser.add_argument('--nwa', type=int, dest='numWinAcross', default=-1,
                        help='Number of window across (default: %(default)s).')
    parser.add_argument('--nwd', type=int, dest='numWinDown', default=-1,
                        help='Number of window down (default: %(default)s).')

    parser.add_argument('--nwac', type=int, dest='numWinAcrossInChunk', default=1,
                        help='Number of window across in chunk (default: %(default)s).')
    parser.add_argument('--nwdc', type=int, dest='numWinDownInChunk', default=1,
                        help='Number of window down in chunk (default: %(default)s).')
    parser.add_argument('-r', '--redo', dest='redo', action='store_true',
                        help='To redo by force (ignore the existing offset fields).')

    parser.add_argument('--drmp', '--deramp', dest='deramp', type=int, default=0,
                        help='deramp method (0: mag, 1: complex) (default: %(default)s).')
    # gpu settings
    parser.add_argument('--gpuid', '--gid', '--gpu-id', dest='gpuid', type=int, default=-1,
                        help='GPU ID (default: %(default)s).')
    parser.add_argument('--nstreams', dest='nstreams', type=int, default=2,
                        help='Number of cuda streams (default: %(default)s).')
    parser.add_argument('--usemmap', dest='usemmap', type=int, default=1,
                        help='Whether to use memory map for loading image files (default: %(default)s).')
    parser.add_argument('--mmapsize', dest='mmapsize', type=int, default=8,
                        help='The memory map buffer size in GB (default: %(default)s).')

    # specify a starting pixel of the reference image, -1 to auto compute
    parser.add_argument('--startpixelac', dest='startpixelac', type=int, default=-1,
                        help='Starting Pixel across (default: %(default)s).')

    parser.add_argument('--startpixeldw', dest='startpixeldw', type=int, default=-1,
                        help='Starting Pixel down (default: %(default)s).')

    parser.add_argument('-alg', '--algorithm', dest='algorithm', type=int, default=0,
                        help='algorithm to use (0 = frequency, 1 = spatial) (default: %(default)s).')

    return parser


def cmdLineParse(iargs = None):
    parser = createParser()
    inps =  parser.parse_args(args=iargs)

    # check oversampled window size
    if (inps.winwidth + 2 * inps.srcwidth) * inps.raw_oversample > 1024:
        msg = 'input oversampled window size in the across/range direction '
        msg += 'exceeds the current implementaion limit of 1024!'
        raise ValueError(msg)

    return inps


@use_api
def estimateOffsetField(reference, secondary, inps=None):

    # update file path in xml file
    for fname in [reference, secondary]:
        fname = os.path.abspath(fname)
        img = IML.loadImage(fname)[0]
        img.filename = fname
        img.setAccessMode('READ')
        img.renderHdr()

    ###Loading the secondary image object
    sim = isceobj.createSlcImage()
    sim.load(secondary+'.xml')
    sim.setAccessMode('READ')
    sim.createImage()

    ###Loading the reference image object
    sar = isceobj.createSlcImage()
    sar.load(reference+'.xml')

    sar.setAccessMode('READ')
    sar.createImage()

    width = sar.getWidth()
    length = sar.getLength()

    objOffset = PyCuAmpcor()

    objOffset.algorithm = inps.algorithm
    objOffset.deviceID = inps.gpuid  # -1:let system find the best GPU
    objOffset.nStreams = 2 #cudaStreams
    objOffset.derampMethod = inps.deramp
    print('deramp method (0 for magnitude, 1 for complex): ', objOffset.derampMethod)

    objOffset.referenceImageName = reference+'.vrt'
    objOffset.referenceImageHeight = length
    objOffset.referenceImageWidth = width
    objOffset.secondaryImageName = secondary+'.vrt'
    objOffset.secondaryImageHeight = length
    objOffset.secondaryImageWidth = width

    print("image length:",length)
    print("image width:",width)

    objOffset.numberWindowDown = (length-2*inps.margin-2*inps.srchgt-inps.winhgt)//inps.skiphgt
    objOffset.numberWindowAcross = (width-2*inps.margin-2*inps.srcwidth-inps.winwidth)//inps.skipwidth

    if (inps.numWinDown != -1):
        objOffset.numberWindowDown = inps.numWinDown
    if (inps.numWinAcross != -1):
        objOffset.numberWindowAcross = inps.numWinAcross
    print("offset field length: ",objOffset.numberWindowDown)
    print("offset field width: ",objOffset.numberWindowAcross)


    # window size
    objOffset.windowSizeHeight = inps.winhgt
    objOffset.windowSizeWidth = inps.winwidth
    print('cross correlation window size: {} by {}'.format(objOffset.windowSizeHeight, objOffset.windowSizeWidth))

    # search range
    objOffset.halfSearchRangeDown = inps.srchgt
    objOffset.halfSearchRangeAcross = inps.srcwidth
    print('half search range: {} by {}'.format(inps.srchgt, inps.srcwidth))

    # starting pixel
    if (inps.startpixeldw != -1):
        objOffset.referenceStartPixelDownStatic = inps.startpixeldw
    else:
        objOffset.referenceStartPixelDownStatic = inps.margin
    if (inps.startpixelac != -1):
        objOffset.referenceStartPixelAcrossStatic = inps.startpixelac
    else:
        objOffset.referenceStartPixelAcrossStatic = inps.margin

    # skip size
    objOffset.referenceStartPixelDownStatic = inps.margin
    objOffset.referenceStartPixelAcrossStatic = inps.margin

    objOffset.skipSampleDown = inps.skiphgt
    objOffset.skipSampleAcross = inps.skipwidth
    print('search step: {} by {}'.format(inps.skiphgt, inps.skipwidth))

    # oversample raw data (SLC)
    objOffset.rawDataOversamplingFactor = inps.raw_oversample
    print('raw data oversampling factor:', inps.raw_oversample)

    # correlation surface
    objOffset.corrStatWindowSize = inps.corr_stat_win_size
    if inps.corr_win_size == -1:
        corr_win_size_orig = min(inps.srchgt, inps.srcwidth) * inps.raw_oversample + 1
        inps.corr_win_size = np.power(2, int(np.log2(corr_win_size_orig)))
        objOffset.corrSurfaceZoomInWindow = inps.corr_win_size
        print('correlation surface zoom-in window size:', inps.corr_win_size)

    # oversampling method: 0 for fft, 1 for sinc
    objOffset.corrSufaceOverSamplingMethod = inps.corr_oversamplemethod
    objOffset.corrSurfaceOverSamplingFactor = inps.corr_oversample
    print('correlation surface oversampling factor:', inps.corr_oversample)

    # output filenames
    fbase = '{}{}'.format(inps.outprefix, inps.outsuffix)
    objOffset.offsetImageName = fbase + '.bip'
    objOffset.grossOffsetImageName = fbase + '_gross.bip'
    objOffset.snrImageName = fbase + '_snr.bip'
    objOffset.covImageName = fbase + '_cov.bip'
    print("offsetfield: ", objOffset.offsetImageName)
    print("gross offsetfield: ", objOffset.grossOffsetImageName)
    print("snr: ", objOffset.snrImageName)
    print("cov: ", objOffset.covImageName)

    try:
        offsetImageName = objOffset.offsetImageName.decode('utf8')
        grossOffsetImageName = objOffset.grossOffsetImageName.decode('utf8')
        snrImageName = objOffset.snrImageName.decode('utf8')
        covImageName = objOffset.covImageName.decode('utf8')
    except:
        offsetImageName = objOffset.offsetImageName
        grossOffsetImageName = objOffset.grossOffsetImageName
        snrImageName = objOffset.snrImageName
        covImageName = objOffset.covImageName

    print(offsetImageName)
    print('redo: ', inps.redo)
    if os.path.exists(offsetImageName) and not inps.redo:
        print('offsetfield file exists')
        return 0

    # generic control
    objOffset.numberWindowDownInChunk = inps.numWinDownInChunk
    objOffset.numberWindowAcrossInChunk = inps.numWinAcrossInChunk
    objOffset.useMmap = inps.usemmap
    objOffset.mmapSize = inps.mmapsize
    objOffset.setupParams()

    ## Set Gross Offset ###
    if inps.gross == 0:
        print("Set constant grossOffset")
        print("By default, the gross offsets are zero")
        print("You can override the default values here")
        gross_offset_down = inps.azshift
        gross_offset_across = inps.rgshift
        objOffset.setConstantGrossOffset(gross_offset_down, gross_offset_across)

    else:
        print("Set varying grossOffset")
        print("By default, the gross offsets are zero")
        print("You can override the default grossDown and grossAcross arrays here")
        objOffset.setVaryingGrossOffset(np.zeros(shape=grossDown.shape,dtype=np.int32),
                                        np.zeros(shape=grossAcross.shape,dtype=np.int32))

    # check
    objOffset.checkPixelInImageRange()

    # Run the code
    print('Running PyCuAmpcor')

    objOffset.runAmpcor()
    print('Finished')

    sar.finalizeImage()
    sim.finalizeImage()

    # Finalize the results
    # offsetfield
    outImg = isceobj.createImage()
    outImg.setDataType('FLOAT')
    outImg.setFilename(offsetImageName)
    outImg.setBands(2)
    outImg.scheme = 'BIP'
    outImg.setWidth(objOffset.numberWindowAcross)
    outImg.setLength(objOffset.numberWindowDown)
    outImg.setAccessMode('read')
    outImg.renderHdr()

    # gross offsetfield
    outImg = isceobj.createImage()
    outImg.setDataType('FLOAT')
    outImg.setFilename(grossOffsetImageName)
    outImg.setBands(2)
    outImg.scheme = 'BIP'
    outImg.setWidth(objOffset.numberWindowAcross)
    outImg.setLength(objOffset.numberWindowDown)
    outImg.setAccessMode('read')
    outImg.renderHdr()

    # snr
    snrImg = isceobj.createImage()
    snrImg.setFilename(snrImageName)
    snrImg.setDataType('FLOAT')
    snrImg.setBands(1)
    snrImg.setWidth(objOffset.numberWindowAcross)
    snrImg.setLength(objOffset.numberWindowDown)
    snrImg.setAccessMode('read')
    snrImg.renderHdr()

    # cov
    covImg = isceobj.createImage()
    covImg.setFilename(covImageName)
    covImg.setDataType('FLOAT')
    covImg.setBands(3)
    covImg.scheme = 'BIP'
    covImg.setWidth(objOffset.numberWindowAcross)
    covImg.setLength(objOffset.numberWindowDown)
    covImg.setAccessMode('read')
    covImg.renderHdr()

    return


def prepareGeometry(full_dir, out_dir, match_win_len, match_win_wid, search_win_len, search_win_wid,
                    step_len, step_wid, margin, fbases=['hgt','lat','lon','los','shadowMask','waterMask']):
    """Generate multilooked geometry datasets in the same grid as the estimated offset field
    from the full resolution geometry datasets.
    """
    from osgeo import gdal

    print('-'*50)
    print('generate the corresponding multi-looked geometry datasets using gdal ...')
    in_files = [os.path.join(full_dir, '{}.rdr.full'.format(i)) for i in fbases]
    in_files = [i for i in in_files if os.path.isfile(i)]
    if len(in_files) == 0:
        raise ValueError('No full resolution geometry file found in: {}'.format(full_dir))

    fbases = [os.path.basename(i).split('.')[0] for i in in_files]
    out_files = [os.path.join(out_dir, '{}.rdr'.format(i)) for i in fbases]
    os.makedirs(out_dir, exist_ok=True)

    for i in range(len(in_files)):
        in_file = in_files[i]
        out_file = out_files[i]

        # input file size
        ds = gdal.Open(in_file, gdal.GA_ReadOnly)
        in_wid = ds.RasterXSize
        in_len = ds.RasterYSize

        # starting column/row number
        sx = margin + search_win_wid + int(match_win_wid / 2)
        sy = margin + search_win_len + int(match_win_len / 2)

        out_wid = int((in_wid - sx * 2) / step_wid)
        out_len = int((in_len - sy * 2) / step_len)
        src_wid = out_wid * step_wid
        src_len = out_len * step_len
        src_win = [sx, sy, src_wid, src_len]
        print('read {} from file: {}'.format(src_win, in_file))

        # write binary data file
        print('write file: {}'.format(out_file))
        opts = gdal.TranslateOptions(format='ENVI',
                                     width=out_wid,
                                     height=out_len,
                                     srcWin=src_win,
                                     noData=0)
        gdal.Translate(out_file, ds, options=opts)
        ds = None

        # write VRT file
        print('write file: {}'.format(out_file+'.vrt'))
        ds = gdal.Open(out_file, gdal.GA_ReadOnly)
        gdal.Translate(out_file+'.vrt', ds, options=gdal.TranslateOptions(format='VRT'))
        ds = None

    return


def main(iargs=None):
    inps = cmdLineParse(iargs)
    start_time = time.time()

    print(inps.outprefix)
    outDir = os.path.dirname(inps.outprefix)
    os.makedirs(outDir, exist_ok=True)

    # estimate offset
    estimateOffsetField(inps.reference, inps.secondary, inps)

    # generate geometry
    if inps.full_geometry_dir and inps.out_geometry_dir:
        prepareGeometry(inps.full_geometry_dir, inps.out_geometry_dir,
                        match_win_len=inps.winhgt,
                        match_win_wid=inps.winwidth,
                        search_win_len=inps.srchgt,
                        search_win_wid=inps.srcwidth,
                        step_len=inps.skiphgt,
                        step_wid=inps.skipwidth,
                        margin=inps.margin)

    m, s = divmod(time.time() - start_time, 60)
    print('time used: {:02.0f} mins {:02.1f} secs.\n'.format(m, s))
    return

if __name__ == '__main__':
    main(sys.argv[1:])
