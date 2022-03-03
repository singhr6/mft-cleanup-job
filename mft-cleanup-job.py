import yaml
from zbpackage import jobs
from zbpackage import cleanup
from zbpackage import argos_utils
import time
from datetime import datetime
import socket
import logging
from logging.handlers import RotatingFileHandler

try:

    #initialize logger
    Log_Format = "%(asctime)s — %(name)s — %(levelname)s — %(funcName)s:%(lineno)d — %(message)s"
    logging.basicConfig(handlers=[RotatingFileHandler('./log/mft-cleanup-logfile.log', maxBytes=20480, backupCount=2)],
                        format=Log_Format,
                        level=logging.INFO)

    logging.info("------Initiating Cleanup Job for EDI logs------.")

    # initializing some variables
    job_name = ''
    deleted_dir = ''
    flag = 0
    cleanup_dir = ''
    job_runtime = ''
    retention = 10
    current_time = time.time()
    error_flag = 'N'
    now = datetime.now()
    strtime = str(now).split(" ")
    job_runtime = strtime[0] + "T" + strtime[1].split(".")[0] + "Z"

    logging.info("Loading config data.")
    stream = open("config.yaml", 'r')
    docs = yaml.load_all(stream, Loader=yaml.FullLoader)
    for doc in docs:
        for k, v in doc.items():
            if k == 'cleanup-dir':
                cleanup_dir = v
            if k == 'retention':
                retention = v
            if k == 'job-name':
                job_name = v

    # Checking directory timestamp and deciding to delete
    past_days_time = current_time - int(retention) * 86400
    for dir in cleanup_dir:
        dir_name = dir.strip()
        logging.info("Cleaning up dir : " + dir_name)
        cleanup_output=cleanup.file_cleanup(dir_name, retention)
        if (cleanup_output == "success"):
            logging.info("Cleanup complete for dir : " + dir_name)
        else:
            raise Exception(cleanup_output)


except Exception as e:
    error_flag='Y'
    logging.error("Exception message : " + str(e))


finally:
    # Update the job status in mongodb job_status collection.
    if (error_flag == 'Y'):
        jobs.send_jobstatus(job_name, "failed", job_runtime, '', socket.gethostname())
        argos_utils.update_influxdb('job_status','job','mft_cleanup',2)
        logging.info("Argos and MongoDB status record updated")
    else:
        jobs.send_jobstatus(job_name, "successful", job_runtime, '', socket.gethostname())
        argos_utils.update_influxdb('job_status','job','mft_cleanup',0)
        logging.info("Argos and MongoDB status record updated")