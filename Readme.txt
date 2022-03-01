To run mft cleanup python job, please follow below steps

1. Make sure to run below command to install all python package
   pip install -r requirements.txt

2. Make sure config file is accurate and point to right directory and environment

3. This job used some modules from zbpackage. zbpackage is already part of virtual environment (venv->Lib->site-packages)

3. Test the python file manually before configuring as window job
   python mft-cleanup-job.py

