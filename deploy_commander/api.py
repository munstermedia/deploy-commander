# api.py
import os
import falcon
import time
import threading
import subprocess
import json
import smtplib

from os.path import isfile, join
from os import listdir

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from fabric.api import env

from config import init

env.home_path = os.environ['DC_HOME_PATH']

# Init default config
init()

def output_to_text(output):
    """
    Format command line output to text
    """
    output = output.replace('[0m', '')
    output = output.replace('[32m', '')
    output = output.replace('[31m', '')
    output = output.replace('[33m', '')
    
    return output

def output_to_html(output, payload_data):
    """
    Format command line output to html
    """
    output = output.replace('[0m', '</span>')
    output = output.replace('[32m', '<span style="color:green;">')
    output = output.replace('[31m', '<span style="color:red;">')
    output = output.replace('[33m', '<span style="color:yellow;">')
        
    output = output.replace('\n', '<br />')
    
    
    params = {'output': output}
    params.update(payload_data)
    
    html = """
        <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
           <html xmlns="http://www.w3.org/1999/xhtml">
           <head>
           <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
           <title>Deploy Commander</title>
           <style type="text/css">
           body{
               background-color:black;
               color:white;
           }
           </style>
           <body>
           <div style="float:right;position:absolute;"><img src="%(user_avatar)s" /></div>
           <div style="font-family: Monospace;white-space:pre;width:98ch;">%(output)s</div>'
           </body>
           </html>""" % params

    return html

def RunCommand(tasks, payload_data):
    """
    Runcommand wil take a list of task params and add 
    extra payload data for rendering template
    """
    # Change directory
    os.chdir(os.environ['DC_HOME_PATH'])
    
    # Fabric executable
    execute = os.path.join(os.environ['DC_VIRTUALENV_PATH'], 'bin', 'deploy-commander')
    
    call = [execute, '--abort-on-prompts']
    call.extend(tasks)
    process = subprocess.Popen(call, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    process.wait()
    
    # Make dir
    file = "%s.html" % int(time.time())
    dir = os.path.join(os.environ['DC_HOME_PATH'], 'logs', 'build', 'mail')
                     
    if not os.path.exists(dir):
        os.makedirs(dir)
    
    communicate = process.communicate()
    
    htmlBody = output_to_html(communicate[0] + communicate[1], payload_data)
    plainBody = output_to_text(communicate[0] + communicate[1])
    
    
    log_file = open(os.path.join(dir, file), 'w+')
    log_file.write(htmlBody)
    log_file.close()
    
    
    if 'mail' in env:
        """
        When mail isset in the config it will use the settings 
        for the smtp server
        """
        
        mail_config = env.mail
        
        email_from = mail_config['from']
        email_to = mail_config['to'][0]
        
        msg = MIMEMultipart('alternative')
        msg['From'] = email_from
        msg['To'] = email_to
        
        # Set important if there was an error!
        if process.returncode > 0:
            msg['Subject'] = 'Deploy Commander failed task'
            msg['X-Priority'] = '2'
        else:
            msg['Subject'] = 'Deploy Commander task executed'
        
        msg.attach(MIMEText(plainBody, 'text'))
        msg.attach(MIMEText(htmlBody, 'html'))
        
        # Create sendmail
        s = smtplib.SMTP(mail_config['host'], str(mail_config['port']))
        s.login(mail_config['user'], mail_config['password'])
        
        s.sendmail(email_from, mail_config['to'], msg.as_string())
        s.quit()
    
    # Cleanup log files
    cleanup_folder(path=dir)
    
def cleanup_folder(path, max_files = 10):
    """
    Cleanup old files (logs)
    """
    onlyfiles = [ f for f in listdir(path) if isfile(join(path,f)) ]
        
    onlyfiles = sorted(onlyfiles, reverse=False)
        
    if (len(onlyfiles) > max_files):
        for remove_file in onlyfiles[0:-max_files]:
            os.remove(os.path.join(path, remove_file))

class BitbucketHookResource:
    def on_post(self, req, resp):
        """Handles POST requests"""
        # Try to read the payload
        try:
            raw_json = str(req.stream.read())
        except Exception as ex:
            raise falcon.HTTPError(falcon.HTTP_400, 'Error', ex.message)
        
        # Write log file
        file = "%s.json" % int(time.time())
        
        dir = os.path.join(os.environ['DC_HOME_PATH'], 'logs', 'bitbucket', 'pullrequesthook')
                     
        if not os.path.exists(dir):
            os.makedirs(dir)
        
        log_file = open(os.path.join(dir, file), 'w+')
        log_file.write(str(raw_json))
        log_file.close()
        
        data = json.loads(raw_json)
        
        payload_data = {}
        if data.has_key('pullrequest_merged'):
            try:
                payload_data = {'title':data['pullrequest_merged']['title'],
                                'description':data['pullrequest_merged']['description'],
                                'branch':data['pullrequest_merged']['destination']['branch']['name'],
                                'project':data['pullrequest_merged']['destination']['repository']['name'],
                                'user_avatar':data['pullrequest_merged']['author']['links']['avatar']['href']}
            except:
                print("Invalid params?")
        
        # How to map branch to environment
        environment_mapping = {'develop':'testing',
                               'release':'staging'}
        
        if (environment_mapping.has_key(payload_data['branch'])):
            go = 'go:%(project)s,%(environment)s' % {'environment':environment_mapping[payload_data['branch']],
                                                     'project':payload_data['project']}
            # Start deploy commander thread
            command_tasks = [go,'run:deploy-app']
            thread = threading.Thread(name='worker', target=RunCommand, args=(command_tasks, payload_data))
            thread.start()

        
        # Cleanup log files
        cleanup_folder(path=dir)
            
        
        resp.status = falcon.HTTP_200  # This is the default status
        resp.body = ('{"status":"ok"}')

class RootResource:
    def on_get(self, req, resp):
        """Handles root get requests"""
        resp.status = falcon.HTTP_200  # This is the default status
        resp.body = '{"status":"ok"}'

class ConfigResource:
    def on_get(self, req, resp):
        file = req.get_param('file', True)
        
        try:
            config_file = open(os.path.join(os.environ['DC_HOME_PATH'], 'config', file), 'r')
        except IOError:
            raise falcon.HTTPBadRequest(
                'Missing config',
                'The config `%s` cannot be found!' % file)

        """Handles root get requests"""
        resp.status = falcon.HTTP_200  # This is the default status
        resp.body = config_file.read()

# falcon.API instances are callable WSGI apps
app = falcon.API()

bitbucket_hook = BitbucketHookResource()
root_resource = RootResource()

# Read the configuration
#app.add_route('/api/1.0/config', ConfigResource())

# Bitbucket pull request post hook
app.add_route('/api/1.0/bitbucket/pullrequestposthook', bitbucket_hook)

# Yust add a root responsive
app.add_route('/', root_resource)