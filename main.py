import json
import os
import sys
import requests
import subprocess as s

def print_help():
    print(f'\nThis program helps you with github\n\n\
usage: {sys.argv[0]} command options\n\n\
COMMANDS:\n\
    config:           Configuring logging data\n\
    run:              Pushing into github\n\
    init:             Creating json file\n\n\
"config" OPTIONS:\n\
    user (str):       Login to github.com\n\
    password (str):   Password to github.com\n\
    full command should look like this: {sys.argv[0]} config login,password')

with open('C:\\Program Files\\gitAuto\\config.json') as f:
    config = json.loads(f.read())

class cl:
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

def pc(t,c,error=False):
    print(c+t+cl.ENDC)
    if error:
        print_help()

def wrFile(data):
    with open('git.json', 'w') as f:
        f.write(json.dumps(data, indent=4))

def add_files(cnf, file):
    if file not in cnf['excludes'] and file.split('.')[1] not in cnf['exclude_exts']:
        os.system(f'git add {file}')

try:
    if sys.argv[1] == 'config':
        try:
            with open('C:\\Program Files\\gitAuto\\config.json','w') as f:
                config["user"]=sys.argv[2].split(',')[0]
                config['password']=sys.argv[2].split(',')[1]
                f.write(json.dumps(config))
        except:
            with open('C:\\Program Files\\gitAuto\\config.json','w') as f:
                f.write(json.dumps({"user":config['user'],"password":config["password"]}))
            pc('FATAL: data is not specified',cl.FAIL,error=True)
    elif sys.argv[1] == 'init':
        try:
            repoName = os.path.split(os.path.abspath(__file__))[0].split('\\')
            data = {'excludes':['git.json'],
                    'exclude_exts':['spec','exe','apk'],
                    'exclude_dirs':["__pycahce__","build","dist","tests"],
                    'commit':'inital',
                    'name':repoName[len(repoName)-1],
                    'remote':f"https://github.com/{config['user']}/{repoName[len(repoName)-1]}"}
            wrFile(data)
            pc('git.json file created. You can customize it', cl.OKGREEN)
        except IndexError:
            pc(f'FATAL: You must specify github user: {sys.argv[0]} init [user]', cl.FAIL, error=True)
    elif sys.argv[1] == 'run':
        if config['password'] and config["user"]:
            if os.access("git.json", os.R_OK):
                with open('git.json', 'r') as f:
                    cnf = json.loads(f.read())
                r = requests.get(f"https://api.github.com/users/{config['user']}/repos").json()
                flag = False
                for rs in r:
                    if rs["name"]==cnf['name']:
                        pc('INFO: Remote repo exists',cl.OKGREEN)
                        flag = True
                        break
                if not flag:
                    pc('WARNING: Remote repo does not exists\nAttempting to create',cl.WARNING)
                    private = str(cnf['private']).lower()
                    s.run(['curl', '-u', f'{config["user"]}:{config["password"]}', '-d', '{"name":\"'+cnf['name']+'}', 'https://api.github.com/user/repos'])
                os.system('git init .')
                pc('INFO: git repo initialized', cl.OKGREEN)
                for file in os.listdir():
                    try:
                        add_files(cnf, file)
                    except IndexError:
                        if file not in cnf['exclude_dirs']:
                            os.chdir(file)
                            for file in os.listdir():
                                add_files(cnf, file)
                            os.chdir('../')
                pc('INFO: files added to repo',cl.OKGREEN)
                os.system(f"git commit -m \"{cnf['commit']}\"")
                pc('INFO: files commited', cl.OKGREEN)
                os.system(f"git remote add origin {cnf['remote']}")
                pc('INFO: remote checked',cl.WARNING)
                os.system('git push -u origin master')
                pc('INFO: files pushed to repo',cl.OKGREEN)
                pc('Success, quitting', cl.WARNING)
            else:
                pc(f'FATAL: There is no git.json file.',cl.FAIL, error=True)
                pc('You can generate it by using `{sys.argv[0]} init [user]` command',cl.WARNING)
        else:
            pc('FATAL: Login or password are not specified in config.json file',cl.FAIL,error=True)
    else:
        pc('FATAL: This command is not recognized',cl.FAIL, error=True)
except IndexError:
    pc('FATAL: You must specify command', cl.FAIL, error=True)
