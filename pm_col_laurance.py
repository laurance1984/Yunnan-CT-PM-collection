#! /usr/bin/env python
# Revision 1.3 by laurance.gao@ericsson.com 20170621
import time
import datetime
import sys, os
import logging
import glob
from logging.handlers import RotatingFileHandler


# If collection delay time is over 15 mins, set it to 1; otherwise set it to 0
delay_flag = 0
# Prefix and surfix of output tar files
output_fix = ["Ericsson_PM_", ".tar.gz"]
# Time period for file to be collected
mtime_inmins = 13

# Record the time script starts running
curr_time = time.time()
curr_min = time.strftime("%M")
curr_min_dl = (int(curr_min)) % 15
datetime.timedelta(minutes=5)
rop_start_sec = datetime.datetime.now() - datetime.timedelta(minutes=(15 + 15 * delay_flag + int(curr_min_dl)))
rop_end_sec = datetime.datetime.now() - datetime.timedelta(minutes=(15 * delay_flag + int(curr_min_dl)))
rop_start_date = rop_start_sec.strftime("%Y%m%d")
rop_start_str = rop_start_sec.strftime("%H%M")
rop_end_str = rop_end_sec.strftime("%H%M")
file_pattern = rop_start_date + '.' + rop_start_str
tarfile_pattern = output_fix[0] + rop_start_date + rop_start_str + "-" + rop_end_str + output_fix[1]

work_dir = "/var/opt/ericsson/nms_umts_pms_seg/segment1/XML/"
output_dir = "/var/opt/ericsson/sgw/outputfiles/pmfiles/"
log_dir = "/var/opt/ericsson/pmcol/log/"       

logging.basicConfig(level=logging.INFO,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                filename= log_dir + 'pm_col.log',
                filemode='a')

################################################################################################
# Define a RotatingFileHandler, which has 5 rotating log files with each 10M in maximum
#Rthandler = RotatingFileHandler(log_dir + 'pm_col.log', maxBytes = 10*1024*1024, backupCount = 5)
#Rthandler.setLevel(logging.INFO)
#formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
#Rthandler.setFormatter(formatter)
#logging.getLogger('').addHandler(Rthandler)
################################################################################################

# Under 3rd sub-directory of work_dir, filter out files matching file_pattern, 
def make_files_list(target_dir, regx, delay):
    # if dir is not a directory, exit with error
    if not os.path.isdir(target_dir):
        logging.error(target_dir + ' is not a valid dir to walk !!!')
        logging.error('Exit without file search and packaging!')
        sys.exit() 
    # loop on all files and select files matching file_pattern
    try: 
        files = glob.glob(target_dir + '*/*/A' + regx + '*statsfile.xml')
        for filename in files:
            mod_time = os.path.getmtime(filename)
            logging.debug (curr_time - mod_time)
            if (delay < curr_time - mod_time or curr_time - mod_time < 0):
                files.remove(filename)
                logging.info ("Some file is not chosen due to large delay!")
    except Exception as e:
        logging.error (e)
        logging.error ("PM file search and archieve for current ROP failed with exception!")
    return files[:]

if __name__ == '__main__':
    logging.info ("====== Program start! ======")

    if delay_flag:
        logging.debug ("PM Recollection:")
    logging.debug("PM collection:")
    logging.debug ("ROP start time is " + rop_start_str)
    logging.debug ("ROP end time is " + rop_end_str)
    logging.debug ("File pattern is " + file_pattern)

    file_list = make_files_list(work_dir, file_pattern, mtime_inmins*60)
        
    if not file_list:
        logging.info ("No file to be collected, exit!")
        exit
    if file_list:
        logging.info ("There are " + str(len(file_list)) + " files to be zipped")
        logging.info ("Start creating tar.gz file...")
        try:            
            cmd = '/usr/sfw/bin/gtar -zcpf ' + output_dir + tarfile_pattern + ' ' + ' '.join(file_list) 
            os.system(cmd)
            logging.info ("Tar file " + tarfile_pattern + " has been created!")
        except Exception as e:
            logging.error (e)
            logging.error ("Tar file failed with exception!")                                   
    logging.info ("======  Program end!  ======")
