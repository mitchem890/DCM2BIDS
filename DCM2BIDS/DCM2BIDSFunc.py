import os
import json
import glob
import ConfigReader as cr
from operator import attrgetter
import logging
import RunShellFunc as RS
from abc import ABCMeta, abstractmethod
import re

# Scan Object will be applied to every scan you have


class Scan(object):
    __metaclass__ = ABCMeta

    def __init__(self, scan_number, nifti_file, json_file, bids_naming):
        self.scan_number = scan_number
        self.nifti_file = nifti_file
        self.json_file = json_file
        self.bids_naming = bids_naming

    def direction_pair(self):
        if self.phaseEncodingDirection == 'i':
            return ''
        elif self.phaseEncodingDirection == 'i-':
            return ''
        elif self.phaseEncodingDirection == 'j':
            return 'PA'
        elif self.phaseEncodingDirection == 'j-':
            return 'AP'
        elif self.phaseEncodingDirection == 'k':
            return ''
        elif self.phaseEncodingDirection == 'k-':
            return ''

    @abstractmethod
    def summary(self):
        '''To override'''
        pass


class Functional(Scan):

    __metaclass__ = ABCMeta

    def __init__(self, scan_number, nifti_file, json_file, bids_naming, task_name, run_number):
        Scan.__init__(self, scan_number, nifti_file, json_file, bids_naming)

        with open(self.json_file) as f:
            data = json.load(f)
        self.phaseEncodingDirection = data['PhaseEncodingDirection']
        self.sliceThickness = data['SliceThickness']
        self.sliceSpacing = data['SpacingBetweenSlices']
        self.TR = data['RepetitionTime']

        self.task_name = task_name
        self.run_number = run_number
        self.bids_folder = 'func'
        self.create_bids_name()

    def is_isotropic(self):
        if self.sliceSpacing == self.sliceThickness:
            return True
        else:
            return False

    def is_rest(self):
        if 'Rest' in self.task_name or 'rest' in self.task_name:
            return True
        else:
            return False

    def create_bids_name(self):
        self.bids_naming=str(self.bids_naming).replace('[task]', self.task_name)
        self.bids_naming=str(self.bids_naming).replace('[MB]', str(self.MBAccFactor))
        self.bids_naming=str(self.bids_naming).replace('[VoxSize]', str(self.sliceSpacing)).replace('.', 'p')
        self.bids_naming = str(self.bids_naming).replace('[DIR]', self.direction_pair())
        self.bids_naming = str(self.bids_naming).replace('[dir]', self.direction_pair().lower())
        self.bids_naming=str(self.bids_naming).replace('[runNum]', str(self.run_number))

    def edit_json(self):
        with open(self.json_file) as f:
            data = json.load(f)

        dict = {"TaskName": self.task_name}
        data.update(dict)

        with open(self.json_file, 'w') as f:
            json.dump(data, f)


class Bold(Functional):

    def __init__(self, scan_number, nifti_file, json_file, bids_naming, task_name, run_number, expected_run_length):

        self.json_file = json_file
        self.expected_run_length = expected_run_length
        with open(self.json_file) as f:
            data = json.load(f)
        self.MBAccFactor = data['MultibandAccelerationFactor']
        Functional.__init__(self, scan_number, nifti_file, json_file, bids_naming, task_name, run_number)
        self.actual_run_length = self.get_actual_run_length()

    def get_actual_run_length(self):

        actual_run_length = RS.run_shell_command('3dinfo -nv ' + self.nifti_file, return_output=True)
        if not actual_run_length:
            print('Error Getting Run Lengths')
            exit()
        else:
            return actual_run_length

    def is_run_length_okay(self):
        if self.actual_run_length == self.expected_run_length or self.expected_run_length == '*':
            return True
        else:
            return False

    def summary(self):


        if not self.is_run_length_okay():
            print("ISSUE with " + self.bids_naming + " run length please Check!!!!!")
            print("Found: " + self.actual_run_length)
            print("Expected: " + self.expected_run_length)

        summary_string = \
            'Func Name: ' + self.bids_naming + '\n' \
            + 'Func Folder: ' + self.bids_folder + '\n' \
            + 'Func Scan Number: ' + self.scan_number + '\n' \
            + 'Task Name: ' +self.task_name + '\n' \
            + 'Func Direction: ' + str(self.direction_pair()) + '\n' \
            + 'Run Number: ' + str(self.run_number) + '\n' \
            + 'Is Isotropic: ' + str(self.is_isotropic()) + '\n' \
            + 'Voxel Size: ' + str(self.sliceSpacing) + 'x' + str(self.sliceThickness) + '\n' \
            + 'Repitition Time: ' + str(self.TR) + '\n' \
            + 'Expected Run Length: ' + str(self.expected_run_length) + '\n' \
            + 'Actual Run Length: ' + str(self.actual_run_length) + '\n'

        return summary_string


class SBref(Functional):

    def __init__(self, scan_number, nifti_file, json_file, bids_naming, bold):
        self.MBAccFactor = bold.MBAccFactor
        Functional.__init__(self, scan_number, nifti_file, json_file, bids_naming, bold.task_name, bold.run_number)

    def summary(self):
        summary_string = \
            'Func Name: ' + self.bids_naming + '\n' \
            + 'Func Folder: ' + self.bids_folder + '\n' \
            + 'Func Scan Number: ' + self.scan_number + '\n' \
            + 'Task Name: ' +self.task_name + '\n' \
            + 'Func Direction: ' + str(self.direction_pair()) + '\n' \
            + 'Run Number: ' + str(self.run_number) + '\n' \
            + 'Is Isotropic: ' + str(self.is_isotropic()) + '\n' \
            + 'Voxel Size: ' + str(self.sliceSpacing) + 'x' + str(self.sliceThickness) + '\n' \
            + 'Repitition Time: ' + str(self.TR) + '\n'

        return summary_string


class FMap(Scan):

    def __init__(self, scan_number, nifti_file, json_file, bids_naming):
        Scan.__init__(self, scan_number, nifti_file, json_file, bids_naming)

        with open(self.json_file) as f:
            data = json.load(f)
        self.phaseEncodingDirection = data['PhaseEncodingDirection']
        self.sliceThickness = data['SliceThickness']
        self.sliceSpacing = data['SpacingBetweenSlices']
        self.TR = data['RepetitionTime']
        self.bids_naming = bids_naming
        self.run_number = 0
        self.bids_folder = 'fmap'

    def is_isotropic(self):
        if self.sliceSpacing == self.sliceThickness:
            return True
        else:
            return False

    def set_effective_range(self, fmaps):
        current_effective_range = 1000
        for fmap in fmaps:
            if (fmap.phaseEncodingDirection == self.phaseEncodingDirection) and (int(fmap.scan_number) > int(self.scan_number)) and (int(fmap.scan_number) < current_effective_range):
                current_effective_range = int(fmap.scan_number)
        self.effective_range = current_effective_range

    def create_bids_name(self):
        self.bids_naming = str(self.bids_naming).replace('[VoxSize]', str(self.sliceSpacing).replace('.', 'p'))
        self.bids_naming = str(self.bids_naming).replace('[DIR]', self.direction_pair())
        self.bids_naming = str(self.bids_naming).replace('[dir]', self.direction_pair().lower())
        self.bids_naming = str(self.bids_naming).replace('[runNum]', str(self.run_number))


    def set_run_number(self, fmaps):
        sameEncodingFmaps = (x for x in fmaps if x.phaseEncodingDirection == self.phaseEncodingDirection)
        max_run_number = max(sameEncodingFmaps, key=attrgetter('run_number'))
        self.run_number = max_run_number.run_number + 1

    def set_intended_for(self, bolds):
        intended_for = []
        if '-' in self.phaseEncodingDirection:
            desired_PE = str(self.phaseEncodingDirection).replace('-', '')
        else:
            desired_PE = str(self.phaseEncodingDirection) + '-'
        for bold in bolds:
            if (str(bold.phaseEncodingDirection) == desired_PE) \
                    and (int(bold.scan_number) < int(self.effective_range)) \
                    and (int(bold.scan_number) > int(self.scan_number)):
                intended_for.append(bold)

        self.intended_for = intended_for

    def summary(self):
        summary_string = \
            'FMap Name: ' + self.bids_naming + '\n' \
            + 'Fmap Folder: ' + self.bids_folder + '\n' \
            + 'FMap Direction: ' + str(self.direction_pair()) + '\n' \
            + 'Run Number: ' + str(self.run_number) + '\n' \
            + 'Is Isotropic: ' + str(self.is_isotropic()) + '\n' \
            + 'Voxel Size: ' + str(self.sliceSpacing) + 'x' + str(self.sliceThickness) + '\n' \
            + 'Repitition Time: ' + str(self.TR) + '\n' \
            + 'Intended For: ' + '\n'
        for bold in self.intended_for:
            summary_string += (bold.bids_naming + '\n')
        return summary_string


class Anatomical(Scan):

    def __init__(self, scan_number, nifti_file, json_file, bids_naming, type):
        Scan.__init__(self, scan_number, nifti_file, json_file, bids_naming)
        self.bids_folder = 'anat'
        self.normalized = self.is_normalized()
        self.defaced = False
        self.type = type
        self.create_bids_name()

    def is_normalized(self):
        with open(self.json_file) as f:
            data = json.load(f)

        if 'NORM' in data['ImageType']:
            return True
        else:
            return False

    def create_bids_name(self):
        self.bids_naming = str(self.bids_naming).replace('[anat]', self.type)

    def summary(self):
        summary_string = \
            'Anat Name: ' + self.bids_naming + '\n' \
            + 'Anat Scan Number: ' + self.scan_number + '\n' \
            + 'Anat Type: ' + self.type + '\n' \
            + 'Anat Normalized: ' + str(self.is_normalized()) + '\n' \
            + 'Anat Defaced: ' + str(self.defaced) + '\n'
        return summary_string


class Session(object):

    def __init__(self, name, anats, bolds, sbrefs, fmaps):
        self.name = name
        self.anats = sorted(anats, key=lambda x: int(x.scan_number))
        self.bolds = sorted(bolds, key=lambda x: int(x.scan_number))
        self.sbrefs = sorted(sbrefs, key=lambda x: int(x.scan_number))
        self.fmaps = sorted(fmaps, key=lambda x: int(x.scan_number))

        self.bids_folder = 'ses-' + name

        if all(x.MBAccFactor == self.bolds[0].MBAccFactor for x in self.bolds):
            self.MBAccFactor = self.bolds[0].MBAccFactor

        for fmap in fmaps:
            fmap.set_effective_range(fmaps)
            fmap.set_intended_for(bolds)
            fmap.set_run_number(fmaps)
            fmap.create_bids_name()


        for scan in anats+bolds+sbrefs+fmaps:
            self.create_bids_name(scan)

    def create_bids_name(self, scan):
        scan.bids_naming = str(scan.bids_naming).replace('[MB]', str(self.MBAccFactor))
        scan.bids_naming = str(scan.bids_naming).replace('[session]', self.name)

    def edit_func_json(self, func):
        with open(func.json_file) as f:
            data = json.load(f)

        task_field = {"TaskName": func.task_name}
        data.update(task_field)

        with open(func.json_file, 'w') as f:
            json.dump(data, f, indent=2)

    def edit_fmap_json(self, fmap):
        with open(fmap.json_file) as f:
            data = json.load(f)
        intended_for_list = []
        for scan in fmap.intended_for:
            intended_for_list.append(os.path.join(self.bids_folder,scan.bids_folder,scan.bids_naming + '.nii.gz'))
        intended_for_dict = {"IntendedFor": intended_for_list}
        data.update(intended_for_dict)

        with open(fmap.json_file, 'w') as f:
            json.dump(data, f, indent=2)

    def summary(self):
        summary_string = \
            'Session Name: ' + self.name + '\n' \
            + 'Session Folder: ' + self.bids_folder + '\n' \
            + 'Number of Anats: ' +str(len(self.anats))+ '\n' \
            + 'Number Of Bolds: ' + str(len(self.bolds)) + '\n' \
            + 'Number Of SBRefs: ' + str(len(self.sbrefs)) + '\n' \
            + 'Number Of Fmaps: ' + str(len(self.fmaps)) + '\n'
        return summary_string


class Subject(object):

    def __init__(self, name, sessions, output_dir):
        self.name = name
        self.sessions = sorted(sessions, key=lambda x: str(x.name))
        self.output_dir = output_dir
        self.bids_folder = 'sub-' + name

        for session in sessions:
            for scan in session.anats + session.bolds + session.sbrefs + session.fmaps:
                self.create_bids_name(scan)
                self.move_files(session, scan)
        for session in sessions:
            for func in session.bolds + session.sbrefs:
                session.edit_func_json(func)

            for fmap in session.fmaps:
                session.edit_fmap_json(fmap)

    def create_bids_name(self, scan):
        scan.bids_naming = str(scan.bids_naming).replace('[subject]', self.name)

    def move_files(self, session, scan):

        origin = scan.nifti_file
        destination = os.path.join(self.output_dir, self.bids_folder, session.bids_folder, scan.bids_folder, scan.bids_naming+'.nii.gz')
        print("origin: " + origin + '\nDestination: ' + destination)
        os.rename(origin, destination)
        scan.nifti_file = destination

        origin = scan.json_file
        destination = os.path.join(self.output_dir, self.bids_folder, session.bids_folder, scan.bids_folder, scan.bids_naming+'.json')
        os.rename(origin, destination)
        scan.json_file = destination

    def summary(self):
        summary_string = \
            'Subject Name: ' + self.name + '\n' \
            + 'Subject Folder: ' + self.bids_folder + '\n' \
            + 'Number of Sessions: ' + str(len(self.sessions)) + '\n'
        return summary_string


# Run PyDeface on the provided scan and place.

def cleanup(path):
    os.chdir(path)

    for f in glob.glob("*.nii.gz"):
        os.remove(f)
    for f in glob.glob("*.json"):
        os.remove(f)


def deface(anat):

    print('Running pyDeface on the the following: ' + anat.type + '\nlocated at: ' + anat.nifti_file)
    print('This may take a few minutes')

    if RS.run_shell_command('pydeface ' + anat.nifti_file + ' --outfile ' + anat.nifti_file + ' --force '):
        #subprocess.Popen(['/home/mitchell/anaconda2/bin/pydeface', anat.nifti_file, '--outfile', anat.nifti_file, '--force'], stdout=subprocess.PIPE, env=my_env).wait()
        anat.defaced = True
        return

    else:
        print("Error Running PyDeface")
        exit()


def conversion(input_path, out_path):
    print('Running Conversion with input path: ' + input_path + ' and output path ' + out_path)
    print('This may take a few minutes')

    if RS.run_shell_command('dcm2niix -3 -b y -z y -o ' + out_path + ' -f %t_%p_%s ' + input_path):
        print("Finished Running Conversion")
        return

    else:
        print("Error Running dcm2niix")
        exit()


def build_file_directory(output_path, subject, session, addSession=False):
    if not addSession:
        os.mkdir(os.path.join(output_path, 'BIDS'))
        os.mkdir(os.path.join(output_path, 'BIDS', 'sub-'+subject))
    os.mkdir(os.path.join(output_path, 'BIDS', 'sub-'+subject,  'ses-' + session))
    os.mkdir(os.path.join(output_path, 'BIDS', 'sub-'+subject,  'ses-' + session, 'anat'))
    os.mkdir(os.path.join(output_path, 'BIDS', 'sub-'+subject,  'ses-' + session, 'fmap'))
    os.mkdir(os.path.join(output_path, 'BIDS', 'sub-' + subject, 'ses-' + session, 'func'))


def create_scan_summary(subject):
    print('Creating Scan Summary: ')


    logging.info(subject.summary())
    for session in subject.sessions:
        logging.info(session.summary())
        for scan in session.anats + session.bolds+session.sbrefs+session.fmaps:
            logging.info(scan.summary())


def get_nifti_json(path, scan_number):
    os.chdir(path)
    json = glob.glob('*_' + str(scan_number) + '.json')
    nifti = glob.glob('*_' + str(scan_number) + '.nii.gz')
    return os.path.join(path, nifti[0]), os.path.join(path, json[0])


def build_anats(configFile, outputDir):
    AnatomicalScans = []
    if cr.use_scans(configFile, 'Anats'):
        print(cr.use_scans(configFile, 'Anats'))
        AnatList = cr.get_list(configFile, 'ANAT')

        for Anat in AnatList:
            scanNumber = cr.get_anat_scan(configFile, Anat)[0]
            nifti, json = get_nifti_json(outputDir, scanNumber)
            bids_naming = cr.get_anat_naming(configFile)
            AnatomicalScans.append(Anatomical(scanNumber, nifti, json, bids_naming, Anat))
    return AnatomicalScans


def build_funcs(configFile, outputDir):
    BoldScans = []
    SBRefScans = []
    use_sbrefs = cr.use_scans(configFile, 'SBRefs')
    if cr.use_scans(configFile, 'Bolds'):

        TaskList = cr.get_list(configFile, 'FUNC')

        for Task in TaskList:

            bold_scans, expectedTRs = cr.get_bold_scans(configFile, Task)
            bold_naming = cr.get_bold_naming(configFile)

            if bold_scans[0] == 'auto':
                regex = cr.get_regular_expression(configFile, 'FUNC', Task)
                bold_scans = auto_get_scan_num(outputDir, regex, 'bold')
                print("For task: " + Task + " found scans: " + str(bold_scans))

            if use_sbrefs:

                sbref_naming = cr.get_sbref_naming(configFile)
                sbref_scans = cr.get_sbref_scans(configFile, Task)
                if sbref_scans[0] == 'auto':
                    regex = cr.get_regular_expression(configFile, 'FUNC', Task)
                    sbref_scans = auto_get_scan_num(outputDir, regex, 'sbref')
                    print("For SBRef: " + Task + " found scans: " + str(sbref_scans))

            for i in range(0, len(bold_scans)):

                nifti, json = get_nifti_json(outputDir, bold_scans[i])
                BoldScans.append(Bold(bold_scans[i], nifti, json, bold_naming, Task, (i + 1), expectedTRs[i]))
                if use_sbrefs:
                    nifti, json = get_nifti_json(outputDir, sbref_scans[i])
                    SBRefScans.append(SBref(sbref_scans[i], nifti, json, sbref_naming, BoldScans[-1]))


    return BoldScans, SBRefScans


def build_fmaps(configFile, outputDir):
    fmaps = []
    if cr.use_scans(configFile, 'FMaps'):
        fmap_scans = cr.get_fmap_scans(configFile)
        fmap_naming = cr.get_fmap_naming(configFile)

        if fmap_scans[0] == 'auto':
            regex = cr.get_regular_expression(configFile, 'FMAP', 'fmap')
            fmap_scans = auto_get_scan_num(outputDir, regex, 'fmap')
            print("For fmaps found scans: " + str(fmap_scans))

        for i in range(0, len(fmap_scans)):
            nifti, json = get_nifti_json(outputDir, fmap_scans[i])
            fmaps.append(FMap(fmap_scans[i], nifti, json, fmap_naming))

    return fmaps


def auto_get_scan_num(directory, pattern, type):

    all_files = [f for f in os.listdir(directory) if re.match(pattern, f)]
    wanted_files = []
    for file in all_files:

        run_length = RS.run_shell_command('3dinfo -nv ' + os.path.join(directory, file), return_output=True)
        if type is 'bold' and int(run_length) > 1:
            wanted_files.append(file)
        elif (type is 'sbref') and int(run_length) == 1:
            wanted_files.append(file)
        elif type is 'fmap':
            wanted_files.append(file)

    scan_numbers = [s.split('_')[-1].split('.')[0] for s in wanted_files]
    int_scan_numbers = [int(s) for s in scan_numbers]
    int_scan_numbers.sort()
    scan_numbers = [str(s) for s in int_scan_numbers]
    return scan_numbers

