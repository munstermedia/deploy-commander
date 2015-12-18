# api.py
import os
import falcon
import time
import threading
import subprocess
import json
import smtplib
import subprocess

from os.path import isfile, join
from os import listdir

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from fabric.api import env

from config import init


env.home_path = os.environ['DC_HOME_PATH']

# Init default config
init()

def output_to_text(output, payload_data):
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
           <div style="float:right;position:absolute;right:20px;"><img src="%(user_avatar)s" /><br /><a href="%(user_home)s">%(author_name)s</a></div>
           <div style="font-family: Monospace;white-space:pre;width:98ch;">%(output)s</div>'
           </body>
           </html>""" % params

    return html

def run_command(payload_data, project, environment):

    go = 'go:%(project)s,%(environment)s' % {'environment':environment,
                                             'project':project}

    command = os.path.join(os.environ['DC_VIRTUALENV_PATH'], 'bin', 'deploy-commander')
    #execute = "(cd %s && (%s %s run:deploy-app))" % (os.environ['DC_HOME_PATH'], command, go)

    run = 'run:deploy-app'


    os.chdir(os.environ['DC_HOME_PATH'])
    
    # Make dir
    output_dir = os.path.join(os.environ['DC_HOME_PATH'], 'logs', 'build', 'output')
                     
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    output_path_file = os.path.join(output_dir, "%s.output" % int(time.time()))
    
    output_log = open(output_path_file, 'w+')


    lockfile_dir = os.path.join(os.environ['DC_HOME_PATH'], 'lockfiles')
    
    if not os.path.exists(lockfile_dir):
        os.makedirs(lockfile_dir)

    lockfile_path_file =  os.path.join(lockfile_dir, ('%s-%s-%s.pid' % (project, environment, 'deploy-app')))

    # For now just kill old process, and start a new one
    if os.path.isfile(lockfile_path_file):
        with open(lockfile_path_file) as log_file:
            pid=log_file.read()
        
        print "Lockfile with pid#%s exists, kill process and remove file" % (pid)
        kill = subprocess.Popen(['kill', pid], stdout=output_log, stderr=output_log)
        kill.wait()


    process = subprocess.Popen([command, go, run], stdout=output_log, stderr=output_log)

    lock = open(lockfile_path_file, 'w+')
    lock.write(str(process.pid));
    lock.close()

    print "PID:", process.pid
    return_code = process.wait()
    os.remove(lockfile_path_file)

    # If process is killed, don't mail!
    if return_code != -15:
        with open(output_path_file) as raw_output_fp:
            raw_output = raw_output_fp.read()
            html_body  = output_to_html(raw_output, payload_data)
            plain_body = output_to_text(raw_output, payload_data)
            mail_log(html_body=html_body,
                     plain_body=plain_body,
                     error=process.returncode)
    # Cleanup log files
    cleanup_folder(path=output_dir)

def mail_log(html_body, plain_body, error=False):
    # Make dir file html
    html_dir = os.path.join(os.environ['DC_HOME_PATH'], 'logs', 'build', 'html')
                     
    if not os.path.exists(html_dir):
        os.makedirs(html_dir)

    html_log = open(os.path.join(html_dir, "%s.html" % int(time.time())), 'w+')
    html_log.write(html_body)
    html_log.close()
    
    
    # Make dir file plain
    text_dir = os.path.join(os.environ['DC_HOME_PATH'], 'logs', 'build', 'txt')
                     
    if not os.path.exists(text_dir):
        os.makedirs(text_dir)

    text_log = open(os.path.join(text_dir, "%s.txt" % int(time.time())), 'w+')
    text_log.write(plain_body)
    text_log.close()

    if 'mail' in env and env['mail']:
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
        if error:
            msg['Subject'] = 'Deploy Commander failed task'
            msg['X-Priority'] = '2'
        else:
            msg['Subject'] = 'Deploy Commander task executed'
        
        msg.attach(MIMEText(plain_body, 'text'))
        msg.attach(MIMEText(html_body, 'html'))
        
        # Create sendmail
        s = smtplib.SMTP(mail_config['host'], str(mail_config['port']))
        s.login(mail_config['user'], mail_config['password'])
        
        s.sendmail(email_from, mail_config['to'], msg.as_string())
        s.quit()
    
def cleanup_folder(path, max_files = 10):
    """
    Cleanup old files (logs)
    """
    onlyfiles = [ f for f in listdir(path) if isfile(join(path,f)) ]
        
    onlyfiles = sorted(onlyfiles, reverse=False)
        
    if (len(onlyfiles) > max_files):
        for remove_file in onlyfiles[0:-max_files]:
            os.remove(os.path.join(path, remove_file))

class BitbucketWebhookResource:
    def on_post(self, req, resp):
        """Handles POST requests"""
        # Try to read the payload
        try:
            raw_json = str(req.stream.read())
        except Exception as ex:
            raise falcon.HTTPError(falcon.HTTP_400, 'Error', ex.message)
        
        # Write log file
        file = "%s.json" % int(time.time())
        
        dir = os.path.join(os.environ['DC_HOME_PATH'], 'logs', 'bitbucket', 'webhook')
                     
        if not os.path.exists(dir):
            os.makedirs(dir)
        
        log_file = open(os.path.join(dir, file), 'w+')
        log_file.write(str(raw_json))
        log_file.close()
        
        data = json.loads(raw_json)
        
        payload_data = {}
        if data.has_key('pullrequest'):
            try:
                payload_data = {'title':data['pullrequest']['title'],
                                'description':data['pullrequest']['description'],
                                'branch':data['pullrequest']['destination']['branch']['name'],
                                'project':data['pullrequest']['destination']['repository']['name'],
                                'user_avatar':data['pullrequest']['author']['links']['avatar']['href'],
                                'user_home':data['pullrequest']['author']['links']['html']['href'],
                                'author_name':data['pullrequest']['author']['display_name']}
            except:
                print("Invalid params?")
        
            # How to map branch to environment
            environment_mapping = {'develop':'testing',
                                   'release':'staging'}
            
            if (environment_mapping.has_key(payload_data['branch'])):
                environment = environment_mapping[payload_data['branch']]
                project     = payload_data['project']
                
                #Start deploy commander thread
                thread = threading.Thread(name='worker', target=run_command, args=(payload_data, project, environment))
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

# new version of hook
bitbucket_webhook =  BitbucketWebhookResource()

root_resource = RootResource()

# Read the configuration
app.add_route('/api/v1/config', ConfigResource())

# Bitbucket pull request post hook
app.add_route('/api/v1/bitbucket/webhook', bitbucket_webhook)

# Yust add a root responsive
app.add_route('/', root_resource)