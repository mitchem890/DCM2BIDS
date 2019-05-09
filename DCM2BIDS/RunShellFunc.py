import logging
import subprocess
import shlex
import os


def run_shell_command(command_line, return_output=False):

    command_line_args = shlex.split(command_line)

    logging.info('\nSubprocess: "' + command_line + '"')

    try:

        os.environ["PATH"] = "/opt/fsl-5.0.10/bin" + os.pathsep + '/opt/afni-latest' + os.pathsep \
                             + '/usr/lib' + os.pathsep + os.environ["PATH"]
        my_env = os.environ.copy()
        my_env['FSLDIR'] = "/usr/share/fsl/5.0"
        my_env['LD_LIBRARY_PATH'] = '/usr/lib'
        my_env['FSLOUTPUTTYPE'] = 'NIFTI_GZ'

        command_line_process = subprocess.Popen(
            command_line_args,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            env=my_env
        )

        process_output, _ = command_line_process.communicate()
        command_line_process.wait()
        # process_output is now a string, not a file,
        # you may want to do:
        # process_output = StringIO(process_output)
        logging.info(process_output)
        if command_line_process.returncode != 0:

            logging.info('An Error Occured, Execption Code: ' + str(command_line_process.returncode))
            logging.info('Subprocess failed')
            return False

    except (OSError, subprocess.CalledProcessError) as exception:
        logging.info('Exception occured: ' + str(exception))
        logging.info('Subprocess failed')
        return False


    # no exception was raised
    logging.info('Subprocess finished\n')

    if return_output:
        output = ''.join(c for c in str(process_output) if c.isdigit())
        return output

    return True
