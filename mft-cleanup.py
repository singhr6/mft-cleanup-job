from zbpackage import email_utils
from zbpackage import jobs
from zbpackage import argos_utils
from zbpackage import log
import time
from datetime import datetime
import os
import socket
import yaml
import shutil

try:
    # initializing some variables
    env = ''
    job_name = ''
    email_from = ''
    email_to = ''
    email_subject = ''
    email_flag = 'Y'
    deleted_dir = ''
    flag = 0
    cleanup_dir = ''
    job_runtime = ''
    team = ''
    retention = 10
    current_time = time.time()
    error_flag = 'N'
    now = datetime.now()
    strtime = str(now).split(" ")
    job_runtime = strtime[0] + "T" + strtime[1].split(".")[0] + "Z"
    #logger = log.set_logger()

    # Reading the config yaml file and setting variables with values from the config file
    stream = open(config_path, 'r')
    docs = yaml.load_all(stream, Loader=yaml.FullLoader)

    #logger.info("setting the variables.")
    for doc in docs:
        for k, v in doc.items():
            if k == 'cleanup-dir':
                cleanup_dir = v
            if k == 'env':
                env = v
            if k == 'retention':
                retention = v
            if k == 'job-name':
                job_name = v
            if k == 'email-from':
                email_from = v
            if k == 'email-to':
                email_to = v
            if k == 'email-subject':
                email_subject = v
            if k == 'email-flag':
                email_flag = v
            if k == 'team':
                team = v


    # Checking directory timestamp and deciding to delete
    past_days_time = current_time - int(retention) * 86400
    for dir in cleanup_dir:
        dir_name = dir.strip()


    # setting the email body content for the email. Email is sent only if email flag is Y in the config file.
    if flag == 0:
        #logger.info("There were no files eligible for deletion process")
        email_body = "No directory was deleted" + "\n\nThanks," + "\n" + team.upper() + " Team"
    else:
        email_body = "Following directories were deleted. \n" + deleted_dir + "\n\nThanks," + "\n" + team.upper() + " Team"

    # Sending email with list of files that got deleted.
    if email_flag == 'Y':
        email_utils.send_mail(email_from, email_to, email_subject, email_body)
        #logger.info("Email sent.")

    return "success"


except Exception as e:
    #logger.error("Exception was raised. Exception message : " + str(e))
    error_flag = 'Y'
    exception_msg="There was exception while run the job. Exception is is " + str(e)
    email_utils.send_mail(email_from, email_to, email_subject + " - failed", exception_msg)
    return exception_msg

finally:
    # Update the job status in mongodb job_status collection.
    if (error_flag == 'Y'):
        jobs.send_jobstatus(job_name, "failed", job_runtime, '', socket.gethostname())
        #logger.info("Argos and MongoDB status record updated")
    else:
        jobs.send_jobstatus(job_name, "successful", job_runtime, '', socket.gethostname())
        #logger.info("Argos and MongoDB status record updated")