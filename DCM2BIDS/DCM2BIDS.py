import DCM2BIDSFunc as D2B
import os
import ConfigReader as cr
import logging
import argparse
import shutil

parser = argparse.ArgumentParser()
parser.add_argument('--configFile', '-c', help='The .ini which describes how to translate the dicoms')
parser.add_argument('--inputDir', '-i', help='The input directory where the dicoms live')
parser.add_argument('--outputDir', '-o', help='Where the BIDS directory should be placed')
parser.add_argument('--overwrite', help='If there is a previously existing BIDS directory overwrite', action="store_true")
parser.add_argument('--addSession', '-s', help='fi there is a folder there a session will be added', action="store_true")
parser.add_argument('--cleanup', help='Clean up the unused niftis from the BIDS folder', action="store_true")

args = parser.parse_args()

configFile = args.configFile
inputDir = args.inputDir
outputDir = args.outputDir

#configFile = '/mnt/mydata/4001_BIDS_config.ini'

if not os.path.exists(configFile):
    print('ConfigFile Does Not exist' + configFile + ' please check')
    exit()


#Get the Subject and session Name
subject_name = cr.get_subject(configFile)
session_name = cr.get_session(configFile)

if args.overwrite and os.path.isdir(os.path.join(outputDir, 'BIDS')) and not args.addSession:
    shutil.rmtree(os.path.join(outputDir, 'BIDS'))

#inputDir, outputDir = cr.get_io_directories(configFile)
if not os.path.isdir(inputDir):
    print('File Does not exist please check: ' + inputDir)
    exit()
if not os.path.isdir(outputDir):
    print('File Does not exist please check: ' + outputDir)
    exit()


logfilename = 'sub-' + str(subject_name) + '_' + 'ses-' + str(session_name) + '.log'
logfilename = os.path.join(outputDir, logfilename)
logging.basicConfig(level=logging.DEBUG, filename=logfilename, filemode='w', format='%(message)s')


#Build the BIDS Structure
if cr.run_processing(configFile, 'buildBIDSDirectories'):

    D2B.build_file_directory(outputDir, subject_name, session_name, args.addSession)
outputDir = os.path.join(outputDir, 'BIDS')


#Convert all the Available Dicoms
if cr.run_processing(configFile, 'dcm2niix'):
    D2B.conversion(inputDir, outputDir)


# Build the Anatomical scans info
AnatomicalScans = D2B.build_anats(configFile, outputDir)
if cr.run_processing(configFile, 'defaceAnats'):
    for Anat in AnatomicalScans:
        D2B.deface(Anat)

# Build the Tasks scan info
BoldScans, SBrefScans = D2B.build_funcs(configFile, outputDir)


# Build the fmap scans info
FmapScans = D2B.build_fmaps(configFile, outputDir)

#Build the sessions
sessions=[]
sessions.append(D2B.Session(session_name, AnatomicalScans, BoldScans, SBrefScans, FmapScans))

#Build the Subject
subject = D2B.Subject(subject_name, sessions, outputDir)

if args.cleanup:
    D2B.cleanup(outputDir)

D2B.create_scan_summary(subject)