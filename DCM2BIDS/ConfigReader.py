import configparser


def deface_anats(configfile):
    config = ConfigParser.ConfigParser()
    config.read(configfile)
    param = 'defaceAnats'
    deface = config.get('DEFAULT', param)
    return deface


def use_scans(configfile, scan_type):
    config = configparser.ConfigParser()
    config.read(configfile)
    param = 'use' + scan_type
    useScans = config.get('DEFAULT', param)
    if str(useScans).lower() == 'true':
        return True
    else:
        return False



def get_list(configfile, section):
    config = configparser.ConfigParser()
    config.read(configfile)
    ListName = section.lower().title() + 'List'
    list = [str(i) for i in config.get(section, ListName).split()]
    return list


def get_anats(configfile):
    config = configparser.ConfigParser()
    config.read(configfile)
    anat_list = [str(i) for i in config.get('ANAT', 'AnatList').split()]
    return anat_list


def get_anat_scan(configfile, anat):
    config = configparser.ConfigParser()
    config.read(configfile)
    anat_scan = [str(i) for i in config.get('ANAT', anat).split()]
    return anat_scan


def get_anat_naming(configfile):
    config = configparser.ConfigParser()
    config.read(configfile)
    anat_naming = config.get('ANAT', 'AnatNaming').split()[0]
    return anat_naming


def get_tasks(configfile):
    config = configparser.ConfigParser()
    config.read(configfile)
    task_list = [str(i) for i in config.get('FUNC', 'FuncList').split()]
    return task_list


def get_task_scans(configfile, task):
    config = configparser.ConfigParser()
    config.read(configfile)
    bold_scans = [str(i) for i in config.get('FUNC', task+'-Bold').split()]
    sbref_scans = [str(i) for i in config.get('FUNC', task+'-SBRef').split()]
    expectedTRs = [str(i) for i in config.get('FUNC', task + '-ExpectedNumOfTRs').split()]
    return bold_scans, sbref_scans, expectedTRs


def get_bold_scans(configfile, task):
    config = configparser.ConfigParser()
    config.read(configfile)
    bold_scans = [str(i) for i in config.get('FUNC', task + '-Bold').split()]
    expectedTRs = [str(i) for i in config.get('FUNC', task + '-ExpectedNumOfTRs').split()]
    return bold_scans, expectedTRs


def get_sbref_scans(configfile, task):
    config = configparser.ConfigParser()
    config.read(configfile)
    sbref_scans = [str(i) for i in config.get('FUNC', task + '-SBRef').split()]
    return sbref_scans


def get_task_naming(configfile):
    config = configparser.ConfigParser()
    config.read(configfile)
    bold_naming = config.get('FUNC', 'BoldNaming').split()[0]
    sbref_naming = config.get('FUNC', 'SBRefNaming').split()[0]
    return bold_naming, sbref_naming


def get_bold_naming(configfile):
    config = configparser.ConfigParser()
    config.read(configfile)
    bold_naming = config.get('FUNC', 'BoldNaming').split()[0]
    return bold_naming


def get_sbref_naming(configfile):
    config = configparser.ConfigParser()
    config.read(configfile)
    sbref_naming = config.get('FUNC', 'SBRefNaming').split()[0]
    return sbref_naming


def get_fmap_scans(configfile):
    config = configparser.ConfigParser()
    config.read(configfile)
    fmap_scans = [str(i) for i in config.get('FMAP', 'fmap').split()]
    return fmap_scans


def get_fmap_naming(configfile):
    config = configparser.ConfigParser()
    config.read(configfile)
    fmap_naming = config.get('FMAP', 'FMapNaming').split()[0]
    return fmap_naming


def get_io_directories(configfile):
    config = configparser.ConfigParser()
    config.read(configfile)
    input_path=config.get('DEFAULT', 'DicomPath')
    output_path=config.get('DEFAULT', 'outputPath')
    return input_path, output_path


def get_subject(configfile):
    config = configparser.ConfigParser()
    config.read(configfile)
    subject=config.get('DEFAULT', 'subject')
    return subject


def get_session(configfile):
    config = configparser.ConfigParser()
    config.read(configfile)
    session = config.get('DEFAULT', 'session')
    return session

def get_regular_expression(configfile, header ,task):
    config = configparser.ConfigParser()
    config.read(configfile)
    regex = config.get(header, task + '-RegEx')
    return regex

def run_processing(configfile, param):
    config = configparser.ConfigParser()
    config.read(configfile)
    result = config.get('DEFAULT', param)

    if str(result).lower() == 'true':
        return True
    else:
        return False

