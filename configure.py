import json
import os
import subprocess

CONFIG_FILENAME = 't0-dev.conf'
FROTZ_DIR = './ext/frotz'
DFROTZ_PATH = os.path.join(FROTZ_DIR, 'dfrotz')
DFROTZ_COMPILE_COMMAND = 'make dfrotz'

def find_on_path(filename):
    for dirname in os.getenv('PATH', '').split(':'):
        path = os.path.join(dirname, filename)
        if os.path.exists(path):
            return path

    return None

def main():
    config = {}

    for program in ['dosbox', 'dfrotz', 'inform']:
        print('Searching for '+program+' on PATH... ', end='')
        config[program] = find_on_path(program)

        if config[program] is None:
            print('not found')
        else:
            print(config[program])

    if config['dfrotz'] is None:
        print('Searching for dfrotz in '+DFROTZ_PATH+'... ', end='')
        if os.path.exists(DFROTZ_PATH):
            print(DFROTZ_PATH)
            config['dfrotz'] = DFROTZ_PATH
        else:
            print('not found')

    if config['dfrotz'] is None:
        print('Attempting to compile dfrotz ('+DFROTZ_COMPILE_COMMAND+'...')

        current_dir = os.getcwd()
        os.chdir(FROTZ_DIR)
        result = subprocess.call(DFROTZ_COMPILE_COMMAND.split())
        os.chdir(current_dir)

        if result==0:
            if os.path.exists(DFROTZ_PATH):
                config['dfrotz'] = DFROTZ_PATH
                print('...done.')
            else:
                # Weird. The compilation succeeded but
                # the binary isn't there
                print('...failed: no '+DFROTZ_PATH)
        else:
            print('...failed: {0}'.format(result))

    problems = 0
    for v in config.values():
        if v is None:
            problems += 1

    if problems!=0:
        print('{0} problems found; can\'t continue.'.format(problems))
    else:
        print('Saving config to '+CONFIG_FILENAME+'... ', end='')
        with open(CONFIG_FILENAME, 'w') as f:
            json.dump(config, f, indent=2)

        print('done.')

if __name__=='__main__':
    main()
