""" Module for preprocess HLS data for Tmask

    Args:
        -p (pattern): searching pattern
        -b (batch): batch process, thisjob and totaljob
        -R (recursive): recursive when seaching files
        --overwrite: overwrite or not
        ori: origin
        des: destination

"""
import os
import sys
import argparse

from osgeo import gdal

from ...io import stackGeo, stack2array, array2stack, ln2tn
from ...common import constants as cons
from ...common import log, get_files, manage_batch


def prepare_tmask(pattern, ori, des, overwrite=False, recursive=False,
                    batch=[1,1]):
    """ converting sentinel images to stacked images

    Args:
        pattern (str): searching pattern, e.g. *B01.jp2
        ori (str): place to look for inputs
        des (str): place to save outputs
        overwrite (bool): overwrite or not
        recursive (bool): recursive when searching file, or not
        batch (list, int): batch processing, [thisjob, totaljob]

    Returns:
        0: successful
        1: error due to des
        2: error when searching files
        3: found no file

    """
    # check if output exists, if not try to create one
    if not os.path.exists(des):
        log.warning('{} does not exist, trying to create one.'.format(des))
        try:
            os.makedirs(des)
        except:
            log.error('Cannot create output folder {}'.format(des))
            return 1

    # locate files
    log.info('Locating files...'.format(ori))
    try:
        hls_list = get_files(ori, pattern, recursive)
        n = len(hls_list)
    except:
        log.error('Failed to search for {}'.format(pattern))
        return 2
    else:
        if n == 0:
            log.error('Found no {}'.format(pattern))
            return 3
        else:
            log.info('Found {} files.'.format(n))

    # handle batch processing
    if batch[1] > 1:
        log.info('Handling batch process...')
        hls_list = manage_batch(hls_list, batch[0], batch[1])
        n = len(hls_list)
        log.info('{} files to be processed by this job.'.format(n))

    # loop through all files
    count = 0
    log.info('Start processing files...')
    for img in hls_list:
        log.info('Processing {}'.format(img[1]))
        try:
            geo = stackGeo(os.path.join(img[0], img[1]))
            array = stack2array(os.path.join(img[0], img[1]), cons.T_BANDS)
            if not os.path.exists(os.path.join(des, ln2tn(img[1]))):
                os.makedirs(os.path.join(des, ln2tn(img[1])))
            bands = ['GREEN', 'NIR', 'SWIR', 'FMASK']
            array[array == -1000] = -9999
            if array2stack(array, geo, os.path.join(des, ln2tn(img[1]),
                            '{}_SFstack'.format(ln2tn(img[1]))), bands,
                            cons.NODATA, gdal.GDT_Int16, overwrite, 'ENVI',
                            ['INTERLEAVE=BIP']) == 0:
                count += 1
            else:
                log.warning('Failed to write output for {}'.format(img[1]))
        except:
            log.warning('Failed to process {}'.format(img[1]))

    # done
    log.info('Process completed.')
    log.info('Successfully processed {}/{} files.'.format(count, n))
    return 0


if __name__ == '__main__':
    # parse options
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--pattern', action='store', type=str,
                        dest='pattern', default='*B01.jp2',
                        help='searching pattern')
    parser.add_argument('-b', '--batch', action='store', type=int, nargs=2,
                        dest='batch', default=[1,1],
                        help='batch process, [thisjob, totaljob]')
    parser.add_argument('-R', '--recursive', action='store_true',
                        help='recursive or not')
    parser.add_argument('--overwrite', action='store_true',
                        help='overwrite or not')
    parser.add_argument('ori', default='./', help='origin')
    parser.add_argument('des', default='./', help='destination')
    args = parser.parse_args()

    # check arguments
    if not 1 <= args.batch[0] <= args.batch[1]:
        log.error('Invalid batch inputs: [{}, {}]'.format(args.batch[0],
                    args.batch[1]))
        sys.exit(1)

    # print logs
    log.info('Start prepare HLS data for Tmask...')
    log.info('Running job {}/{}'.format(args.batch[0], args.batch[1]))
    log.info('Looking for {}'.format(args.pattern))
    log.info('In {}'.format(args.ori))
    log.info('Saving in {}'.format(args.des))
    if args.recursive:
        log.info('Recursive seaching.')
    if args.overwrite:
        log.info('Overwriting old files.')

    # run function to prepare HLS data for Tmask
    prepare_tmask(args.pattern, args.ori, args.des, args.overwrite,
                    args.recursive, args.batch)
