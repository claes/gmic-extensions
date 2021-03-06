#!/usr/bin/python
#
# Wrapper script around dcraw and G'MIC
#
# Copyright Claes Holmerson 2010, GPL licensed (see COPYING for details)
#

import sys
import os
import subprocess
import argparse

GMICRAW_HOME = sys.path[0]
CAMERA_PROFILE = os.path.join(GMICRAW_HOME, 'Profiles', 'Camera', 'icc-profiles-canon-eos400d', 'canon_eos400d_faithful.icc')
GMIC_EXTENSION = os.path.join(GMICRAW_HOME, 'gmicext.gmic')    

DCRAW_SATURATION=3726

def main(argv=None):
    if argv is None:
        argv = sys.argv
        
    start_of_gmic_args = argv.index('-i')
    dcraw_args_iter = iter(argv[1:start_of_gmic_args])
    gmic_args = argv[start_of_gmic_args + 2:]
    raw_file = argv[start_of_gmic_args + 1]
    
    linearity_defined = False
    whitebalance_defined = False
    size_defined = False
    input_profile_defined = False
    saturation_defined = False
    dcraw_args = []

    # Use same option names as dcraw uses
    while True:
        try:
            dcraw_arg = dcraw_args_iter.next()
            if dcraw_arg == '-6' and not linearity_defined:
                print '16 bit non-linear processing'
                dcraw_args.append(dcraw_arg)
                linearity_defined = True
            if dcraw_arg == '-4' and not linearity_defined:
                print '16 bit linear processing'
                dcraw_args.append(dcraw_arg)
                linearity_defined = True
            if dcraw_arg == '-h' and not size_defined:
                print 'Half size image'
                dcraw_args.append(dcraw_arg)
                size_defined = True
            elif dcraw_arg == '-a' and not whitebalance_defined:
                print 'Auto white balance'
                dcraw_args.append(dcraw_arg)
                whitebalance_defined = True
            elif dcraw_arg == '-w' and not whitebalance_defined:
                print 'Camera white balance'
                dcraw_args.append(dcraw_arg)
                whitebalance_defined = True
            elif dcraw_arg == '-S' and not saturation_defined:
                print 'Saturation'
                dcraw_args.append(dcraw_arg)
                dcraw_args.append(dcraw_args_iter.next())
                saturation_defined = True
            elif dcraw_arg == '-H':
                print 'Highlight handling'
                dcraw_args.append(dcraw_arg)
                dcraw_args.append(dcraw_args_iter.next())
            elif dcraw_arg == '-p':
                print 'Camera ICC profile'
                dcraw_args.append(dcraw_arg)
                dcraw_args.append(dcraw_args_iter.next())
            elif dcraw_arg == '-K':
                print 'Darkframe'
                dcraw_args.append(dcraw_arg)
                dcraw_args.append(dcraw_args_iter.next())
            elif dcraw_arg == '-k':
                print 'Darkness'
                dcraw_args.append(dcraw_arg)
                dcraw_args.append(dcraw_args_iter.next())
            elif dcraw_arg == '-i':
                print 'Interpolation. 0=bilinear 1=VNG 2=PPG 3=AHD'
                dcraw_args.append(dcraw_arg)
                dcraw_args.append(dcraw_args_iter.next())
        except StopIteration:
            break

    # Defaults
    if not whitebalance_defined:
        dcraw_args.append('-6') 
    if not linearity_defined:
        dcraw_args.append('-w') 
    if not input_profile_defined:
        dcraw_args.append('-p')
        dcraw_args.append(CAMERA_PROFILE)
    if not saturation_defined:
        dcraw_args.append('-S')
        dcraw_args.append(str(DCRAW_SATURATION))

    processImage(raw_file, dcraw_args, gmic_args)

def processImage(raw_file, dcraw_args, gmic_args):
    
    dcraw_command = ['dcraw']
    dcraw_command.extend(dcraw_args)
    dcraw_command.extend([ '-c', '-6', raw_file])
    gmic_command = ['gmic', '-m', GMIC_EXTENSION, '-.ppm']
    gmic_command.extend(gmic_args)

    print str(dcraw_command)
    print str(gmic_command)
    dcraw_exe = subprocess.Popen(dcraw_command, stdout=subprocess.PIPE)
    gmic_exe = subprocess.Popen(gmic_command, stdin=dcraw_exe.stdout, stdout=subprocess.PIPE)
    print("Processing")
    output = gmic_exe.communicate()[0]
    

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception, e:
        print ("An error occured")
        sys.exit(1)
    except KeyboardInterrupt:
        print "Interrupted"
        sys.exit(1)
