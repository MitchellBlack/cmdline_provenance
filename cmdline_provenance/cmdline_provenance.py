import os
import sys
import datetime
import git

import json
import os.path
import re
import ipykernel
import requests

from requests.compat import urljoin
from notebook.notebookapp import list_running_servers

def get_notebook_name():
    """
    Return the full path of the jupyter notebook.
    Code sourced from https://github.com/jupyter/notebook/issues/1000 
    """
    kernel_id = re.search('kernel-(.*).json',
                          ipykernel.connect.get_connection_file()).group(1)
    servers = list_running_servers()
    for ss in servers:
        response = requests.get(urljoin(ss['url'], 'api/sessions'),
                                params={'token': ss.get('token', '')})
        for nn in json.loads(response.text):
            if nn['kernel']['id'] == kernel_id:
                relative_path = nn['notebook']['path']
                return os.path.join(ss['notebook_dir'], relative_path)

def get_current_entry(git_repo=None,ipynb=False):
    """Create a record of the current command line entry.
   
    Kwargs:
      git_repo (str): Location of git repository associated with script executed at command line
   
    Returns:
      str. Latest command line record
   
    """
 
    time_stamp = datetime.datetime.now().strftime("%a %b %d %H:%M:%S %Y")
   
    if ipynb:
        exe = !which jupyter
        exe = exe[0]
        args = " ".join(['notebook',get_notebook_name()])
    else:
        exe = sys.executable
        args = " ".join(sys.argv)
   
    if git_repo:
        git_hash = git.Repo(git_repo).heads[0].commit
        git_text = " (Git hash: %s)" %(str(git_hash)[0:7])
    else:
        git_text = ''
       
    entry = """%s: %s %s%s""" %(time_stamp, exe, args, git_text)
   
    return entry
    
def new_log(infile_history=None, extra_notes=None, git_repo=None):
    """Create a new command line log/history.
    
    Kwargs:
      infile_history (dict): keys are input file names and values are the logs for those files 
      
      extra_notes (list): List containing strings of extra information  (output is one list item per line)
      
      git_repo (str): Location of git repository associated with script executed at command line
      
    Returns:
      str. Command line log
      
    """
    
    log = ''
        
    current_entry = get_current_entry(git_repo=git_repo, ipynb=ipynb)
    log += current_entry + '\n'
    
    if extra_notes:
        log += 'Extra notes: \n'
        for line in extra_notes:
            log += line + '\n'
    
    if infile_history:
        assert type(infile_history) == dict
        nfiles = len(list(infile_history.keys()))
        for fname, history in infile_history.items():
            if nfiles > 1:
                log += 'History of %s: \n %s \n' %(fname, history)
            else:
                log += '%s \n' %(history)
    
    return log


def read_log(fname):
    """Read a log file.
    
    Args:
      fname (str): Name of log file
      
    Returns:
      str. Command line log
    
    """
   
    log_file = open(fname, 'r')
    log = log_file.read()
    
    return log

    
def write_log(fname, cmd_log):
    """Write an updated command line log/history to a text file.
    
    Args:
      fname (str): Name of output file
      
      cmd_log (str): Command line log produced by new_log()
    
    """
   
    log_file = open(fname, 'w')
    log_file.write(cmd_log) 
    log_file.close()
