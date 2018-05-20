import subprocess
import select
import os
import os.path
import argparse
import sys
import tempfile
import glob
import time
import signal
import re
import json

def copy_in_original(source, target):

	# The target given is a directory for drives.
	# Everything we're doing is on drive C,
	# so just create that.
	target = os.path.join(target, 'c')
	os.mkdir(target)

	for filename in [
		'HINT.DAT',
		'T-0.DAT',
		'T-ZERO.DAT',
		'T-ZERO.EXE',
		'dosemu.conf',
		]:

		source_filename = os.path.join(source, filename)
		target_filename = os.path.join(target, filename)

		contents = open(source_filename).read()
		open(target_filename, 'wb').write(contents)

###########################

class Implementation(object):

    def __init__(self):
        self._monitors = []
        self._prompt = '>'
        self._command_count = 0

    def addMonitor(self, monitor):
	self._monitors.append(monitor)
	monitor.setImplementation(self)

    def read(self):

            buffer = ''
            timeout_count = 0

            while True:

		ready = select.select(
			[self._emu.stdout],
			[], # wlist
			[], # xlist
                        4, # timeout in seconds
		)

		if self._emu.stdout in ready[0]:
			received = self._emu.stdout.read(1)
                        buffer += received

			if buffer.endswith('\n'):
			    buffer = buffer[:-1]+'\r\n'

                        if buffer.endswith('***MORE***'):
                            buffer = buffer[:-10]
                            self._emu.stdin.write('\r\n')

                        if buffer.endswith(self._prompt):
                            # got it; return, but strip the prompt
                            return buffer[:-len(self._prompt)]
                else:
                    # we timed out

                    timeout_count += 1

                    if timeout_count>3:
                        print '(too many timeouts; giving up)'
                        return buffer
                    else:
                        print '(timeout, sending CR)'
                        self._emu.stdin.write('\r\n')

    def write(self, command):
	self._emu.stdin.write(command + '\r\n')

    def run(self):
		print 'Beginning run.'

		startupText = self.read()
		self._pushToMonitors('', '')

    def _pushToMonitors(self, command, response):
        for monitor in self._monitors:
            monitor.handle(
                    self._command_count,
                    command,
                    response)

    def do(self,
		command,
		expect=None):

                self._command_count += 1

		self.write(command)
		response = self.read()

                checking_response = re.sub(r'\s+', ' ', response)

		if expect is not None and not expect in checking_response:
			self.close()
			raise ValueError('"%s" was not found in:\n=== %s\n%s' % (
				expect,
				command,
				checking_response))

		self._pushToMonitors(command, response)
		return response

    def close(self):
	for monitor in self._monitors:
	    monitor.close()

class DosVersion(Implementation):

    # Number of seconds to wait for the game to start up.
    SLEEP_WAIT = 14

    def __init__(self):

        Implementation.__init__(self)

	self._emu = None
        self._prompt = '>>'
	self._rlist = [sys.stdin]

	self._contents_dir = tempfile.mkdtemp(prefix='temp_t0dos')

	# FIXME: original directory should be configurable
	copy_in_original(source='orig', target=self._contents_dir)

	self._emu = subprocess.Popen(
		args = [
			'dosemu',
			'-f'+os.path.join(self._contents_dir, 'c', 'dosemu.conf'),
			'-quiet',
			'-dumb',
			'--Fimagedir',
			self._contents_dir,
			'T-ZERO',
			],
		stdin = subprocess.PIPE,
                stdout = subprocess.PIPE,
                )

        def sigterm_handler(signum, frame):
    	    print '--- SIGTERM received ---'
	    emu.close()
	    sys.exit()

        # XXX why is this not set on the child process?
        signal.signal(signal.SIGTERM, sigterm_handler)

	time.sleep(1)

	for startup_command in [
			'T-ZERO',
			'',
			'SCRIPT',
		]:

		self._emu.stdin.write(startup_command+'\r\n')

		if startup_command=='T-ZERO':
			print
			print 'Now sleeping for', self.SLEEP_WAIT, 'seconds while the game starts up.'
			print
			time.sleep(self.SLEEP_WAIT)
			print 'Sleep finished.'
		else:
			time.sleep(1)



    def close(self):
	print 'Terminating process', self._emu.pid, 'here'
	self._emu.terminate()
	print 'Waiting...'
	self._emu.wait()

        Implementation.close(self)

class Z5Version(Implementation):

    def __init__(self):

        Implementation.__init__(self)

	self._rlist = [sys.stdin]
        self._prompt = '> >'

	self._emu = subprocess.Popen(
		args = [
			'dfrotz',
                        't-zero.z5',
			],
		stdin = subprocess.PIPE,
                stdout = subprocess.PIPE,
                )


class Monitor(object):
	"""
	A Monitor watches the game being played
	and interferes where it wants.
	"""
	def __init__(self):
		self._implementation = None

	def setImplementation(self, implementation):
		self._implementation = implementation

	def handle(self, command_number, command, response):
		raise NotImplementedError("Abstract method called")

	def close(self):
		pass

class GameScript(Monitor):
	"""
	This watches for the beginning of the game,
	then injects the commands to play the
	whole game through.
	"""

	def handle(self, command_number, command, reponse):
            if command_number==0:
		    # at the beginning of the run;
		    # start the playthrough
		    self.run()

class Playthrough(GameScript):
	"""
        Play the whole game through.
	"""

	def run(self):
		impl = self._implementation

		impl.do('inventory', expect = 'in your possession')
		impl.do('x slip', expect='walking papers')
		impl.do('read slip', expect='too near completion')
		impl.do('x compass', expect='cardinal')
		impl.do('x me', expect='fade into the woodwork')
		impl.do('x journal page', expect='cryptic')
		impl.do('x fatigues', expect='commodious')
		impl.do('x fob pocket', expect='just the right')
		impl.do('x thigh pocket', expect='mind of its own')

		# Field of Poppies

		impl.do('nw', expect='Field of Poppies')
		impl.do('x poppy', expect='dry husk')
		impl.do('get seed', expect='bursts')

		# Field of Stone

		impl.do('s', expect='Field of Stone')
		birdpoo = ''
		birdpoo += impl.do('leave no stone unturned', expect='prehistoric')
		birdpoo += impl.do('get claw', expect='Taken')
		birdpoo += impl.do('x tern', expect='tirelessly')

		while 'taking aim' not in birdpoo:
			birdpoo += impl.do('wait')

		impl.do('stone terns', expect='stoned')
		impl.do('get tern', expect='turn to stone')
		impl.do('get feather', expect='Taken')

		# off to the Coldhouse

		impl.do('se', expect='Desolate Field')
		impl.do('s', expect='Back of Museum')
		impl.do('e', expect='Greenhouse')
		impl.do('ne', expect='Coldhouse')

		# Coldhouse

		impl.do('pull lever', expect='arctic')
		impl.do('get token', expect='Taken')
		impl.do('get lever', expect='Taken')

		impl.do('sw', expect='Greenhouse')
		impl.do('e', expect='Shed')

		# Shed

		impl.do('x shelf', expect='splintery')
		impl.do('get extractor', expect='Taken')
		impl.do('get fixer-upper', expect='Taken')

		impl.do('w', expect='Greenhouse')
		impl.do('open door', expect='Opened')
		impl.do('n', expect='Caretaker\'s Cottage')

		# Cottage

		impl.do('get bell', expect='Taken')

		impl.do('e', expect='Pantry')

		# Pantry

		impl.do('get jar', expect='Taken')

		impl.do('w', expect='Caretaker\'s Cottage')
		impl.do('s', expect='Greenhouse')
		impl.do('se', expect='Fountain Court')
		impl.do('s', expect='Topiary')
		impl.do('e', expect='Topiary')

		# Topiary

		topiary_path = 'EESSENNNESWSESSWWWWNNESWSEEEEN'
                used_tools = set()

		for move in topiary_path:
			result = impl.do(move, 'to the Northwest')

			for line in result.split('\n'):
				words = line.split()

				if len(words)<4:
					continue

				if words[3]!='to' and words[4]!='the':
					continue

				monster = words[1]

				for (affix, tool) in ( ('latch', 'extractor'),
					('key', 'fixer-upper') ):

		    		    if affix not in monster:
                                        continue

                                    if tool in used_tools:
                                        continue

				    impl.do('pull '+monster+' with '+tool,
					expect='which now reads')

                                    used_tools.add(tool)

                                    if len(used_tools)==2:
                        	        impl.do('attach fixer-upper to extractor', expect='lightning')
		                        impl.do('get latchkey', expect='Taken')

                if len(used_tools)!=2:
                    # FIXME: we don't know for sure that
                    # the latch* and the *key are both
                    # on topiary_path. At some point
                    # we're going to need a better
                    # explore routine.
                    raise ValueError("Latchkey wasn't found; try again")

		impl.do('e', expect='Amazing Space')

		# Amazing Space

		impl.do('get orange', expect='Taken')

		impl.do('e', expect='Platform Over River')
		impl.do('ne', expect='Suspension Bridge')
		impl.do('snap suspenders', expect='retort')
		impl.do('ne', expect='Across the River')
		impl.do('e', expect='Junkyard')

		# Junkyard

		impl.do('call rag man Anagram', expect='proper name')
		impl.do('ask Anagram about violets', expect='wallflower')
		impl.do('dig in dump with claw', expect='debugged')
		impl.do('get ring', expect='swoops')
		impl.do('get code', expect='Taken')
		impl.do('get flag', expect='Taken')
		impl.do('give code to anagram', expect='wire-frame')

		impl.do('w', expect='Across the River')
		impl.do('sw', expect='Suspension Bridge')

		impl.do('snap suspenders', expect='retort')
		impl.do('tie loop to stanchion', expect='infinite')
		impl.do('snap suspenders', expect='retort')
		impl.do('d', expect='On the Rocks')

		# On the Rocks

		impl.do('get coaster', expect='Taken')

		impl.do('u', expect='Suspension Bridge')
		impl.do('snap suspenders', expect='retort')
		impl.do('sw', expect='Platform Over River')
		impl.do('sw', expect='English Garden')

		# English Garden

		rain = ''
		while 'dreary' not in rain:
			rain = impl.do('x rain')

		walrus = ''
		while 'walrus' not in walrus:
			walrus += impl.do('stand in rain')

		impl.do('get walrus', expect='Taken')
		impl.do('wear walrus', expect='earlobes')

		impl.do('get out of rain')
		impl.do('n', expect='Topiary of Time')
		impl.do('n', expect='Fountain Court')
		impl.do('nw', expect='Greenhouse')
		impl.do('nw', expect='Hothouse')

		# Hothouse

		impl.do('get salamander with coaster', expect='You now have')

		impl.do('se', expect='Greenhouse')
		impl.do('w', expect='Back of Museum')
		impl.do('sw', expect='West Side of Museum')
		impl.do('s', expect='Cornerstone')
		impl.do('se', expect='Museum Stairs')
		impl.do('n', expect='Portico of Museum')
		impl.do('unlock door with latchkey', expect='Unlocked')
		impl.do('open door', expect='Opened')

		# Museum

		impl.do('n', expect='Foyer')
		impl.do('n', expect='West-East')
		impl.do('open door', expect='Opened')
		impl.do('n', expect='Administrative')
		impl.do('get slow mirror', expect='Taken')
		impl.do('s', expect='West-East')

		impl.do('w', expect='Hall of Clocks')
		impl.do('n', expect='Counter-Clockwise')
		impl.do('jump counterclockwise', expect='Spiral Staircase')

		impl.do('open door', expect='Opened')
		impl.do('e', expect='Library')

		# Library
		impl.do('x plaque')
		impl.do('read plaque', expect='curl')
		impl.do('press red button', expect='darkroom')

		impl.do('read pink slip')
		impl.do('x blank book')
		impl.do('read blank book', expect="flutters")
		impl.do('tear flyleaf from blank book')

		impl.do('se', expect="Clockwise")
		impl.do('jump clockwise', expect="Computer Room")

		impl.do('n', expect='Green Room')

		# Green Room

		impl.do('open door', expect='lethal')
		impl.do('open jar', expect='pressure')
		impl.do('close jar', expect='Closed')

		impl.do('n', expect='Count-Down')
		impl.do('unlock north door with latchkey')
		impl.do('open north door')
                # If we go out here, we may meet Anagram;
                # this class should have provision for that
		#impl.do('n', expect='Count-Down')

		impl.do('s', expect='Green Room')
		impl.do('s', expect='Computer Room')
		impl.do('w', expect='South-North Hall')
		impl.do('s', expect='Supply Closet')
		impl.do('get vial', expect='Taken')
		impl.do('n', expect='South-North Hall')
		impl.do('n', expect='Turn in Hall')
		impl.do('w', expect='West-East Hall')
		impl.do('open door', expect='Opened')

class Logger(Monitor):

	def __init__(self,
		to_stdout = True,
		to_filename = None):

		super(Logger, self).__init__()

		self._to_stdout = to_stdout

		if to_filename is not None:
			self._logfile = open(to_filename, 'w')
		else:
		    	self._logfile = None

	def handle(self, command_number, command, response):

		content = '==== %4d == %s\n%s\n' % (
                        command_number,
			command,
			response)

		if self._to_stdout:
			print content

		if self._logfile is not None:
		    self._logfile.write(content)

	def close(self):
		if self._logfile is not None:
		    self._logfile.close()

MOVEMENTS = (
	'n', 'ne', 'e', 'se', 's', 'sw', 'w', 'nw',
	'up', 'down',
	'jump counterclockwise',
	'jump clockwise',
	)

class RoomNoticer(Monitor):

	def __init__(self):
		super(RoomNoticer, self).__init__()

		self._seenRooms = set()
                self._noticing = False

	def handle(self, command_number, command, response):

                if self._noticing:
                    self.notice(command_number, command, response)

		if not command.lower() in MOVEMENTS:
		    return

		response = response.replace('\r','').split('\n')

		# Either the room name is at the end
		# of the text, with blank lines around it
		# (in the case that we didn't just move)
		# or it's on the first nonblank line
		# (in the case that we did).

                if '. ' in response:
                    # this is Frotz-style
                    roomName = response[response.index('. ')+1]
                else:
		    roomName = response[response.index('')+1]

                self._noticing = True
		self._enterRoom(name=roomName,
			firstTime = not roomName in self._seenRooms)
                self._noticing = False

		self._seenRooms.add(roomName)

	def _enterRoom(self, name, firstTime):
	    print 'Room name is "%s". First? %d.' % (name, firstTime)

	def notice(self, command_number, command, response):
            print command
            print response

class Chimes(RoomNoticer):
    def __init__(self):
        super(Chimes, self).__init__()

        self._result = {}
        self._found = None

    def _enterRoom(self, name, firstTime):
        self._found = None
        impl = self._implementation
        count = 0

        while not self._found and count<13:
            impl.do('wait')
            count += 1

        print name, self._found

        self._result[name] = self._found
        self._found = None

    def notice(self, command_number, command, response):
        if 'chimes' in response:
            self._found = response

    def close(self):
        super(Chimes, self).close()

        print
        print self._result

class MakeInteractive(Monitor):

    def __init__(self, trigger):

        super(MakeInteractive, self).__init__()

        self._trigger = trigger
        self._interactive = False

    def handle(self, command_number, command, response):

        if self._trigger not in response:
            return

        if self._interactive:
            # avoid infinite recursion
            return

        self._interactive = True
        print
        print '=== The game is now interactive'
        print 'Give commands at stdin. EOF will continue game.'
        print

        while True:
            try:
                command = raw_input('>')
            except EOFError:
                return

            self._implementation.do(command)

class ScoreNoticer(Monitor):

    def __init__(self):

        super(Monitor, self).__init__()

    def handle(self, command_number, command, response):

        if "\007" in response:
            self._implementation.do('score')

        if "[Your score" in response:
            self._implementation.do('rank')


class TopiaryExplorer(Monitor):

    # This expects a savefile called "0-2-e.sav"
    # to exist, in the initial room of the maze.

    def __init__(self):
        super(TopiaryExplorer, self).__init__()

    def _move(self, filename, direction):

        direction = direction.lower()
        name, ext = os.path.splitext(filename.lower())
        x, y, old_dir = name.split('-')

        x = int(x)
        y = int(y)

        if direction=='n':
            y -= 1
        elif direction=='e':
            x += 1
        elif direction=='s':
            y += 1
        elif direction=='w':
            x -= 1
        else:
            raise ValueError("unknown direction: "+direction)

        x = str(x)
        y = str(y)

        return ('-'.join([x, y, direction]))+ext

    def _first_monster(self, response):
        response = response.replace('\r','')
        words = response.split()

        if 'A' in words:
            return words[words.index('A')+1]

        return None

    def handle(self, command_number, command, response):

        result = {
                }
        unexplored = set(['0-2-e.sav'])
        impl = self._implementation

        if command_number!=0:
            return

        while len(unexplored)!=0:

            print 'Unexplored: ', unexplored
            savefile = unexplored.pop()
            print 'Savefile:', savefile

            for direction in ('e', 'n', 's', 'w'):

                restored = impl.do('restore '+savefile)

                if 'Tangled' not in restored:
                    raise ValueError('restoration of '+savefile+' failed with:\n'+restored)

                monster = self._first_monster(impl.do('look'))
                moved = impl.do(direction)

                if 'Tangled roots' not in moved:
                    print '(outside topiary)'
                    result[keyname] = moved
                    continue

                keyname = savefile+' '+direction

                if self._first_monster(moved) != monster:
                    new_room = self._move(savefile, direction)

                    if not os.path.exists('c/'+new_room):
                        impl.do('save '+new_room)
                        unexplored.add(new_room)
                    else:
                        print '(not saving)'

                    result[keyname] = 0
                else:
                    result[keyname] = '\n'.join(moved.split('\n')[0:2])

            print 'Result:'
            print json.dumps(result, indent=2, sort_keys=True)
            json.dump(
                    result,
                    open('topiary.json', 'w'), 
                    indent=2, sort_keys=True)

SCRIPTS = {
        'playthrough': Playthrough,
        'rooms': RoomNoticer,
        'chimes': Chimes,
        'topiary': TopiaryExplorer,
        'score': ScoreNoticer,
        }

def main():

        parser = argparse.ArgumentParser(
            description='test an implementation of T-Zero')
        parser.add_argument(
            '-d', '--dos', 
            help='run the original DOS implementation',
            action="store_true")
        parser.add_argument(
            '-i', '--interactive', 
            help='become interactive when TRIGGER is in response',
            metavar='TRIGGER',
            type=str)
        parser.add_argument(
            '-q', '--quiet', 
            help='don\'t dump everything that happens',
            action="store_true")
        parser.add_argument(
            'scripts',
            help='play through the game with script SCRIPT (can be used multiply). Defaults to "playthrough"',
            nargs='*',
            metavar='SCRIPT',
            type=str)
        args = parser.parse_args()

        if args.dos:
            implementation = DosVersion()
        else:
            implementation = Z5Version()

        if len(args.scripts)==0:
            implementation.addMonitor(Playthrough())

        for script in args.scripts:
            if script not in SCRIPTS:
                raise ValueError(script+' is not a known script')

            implementation.addMonitor(SCRIPTS[script]())

        if not args.quiet:
            implementation.addMonitor(Logger(
    		to_stdout = True,
    		to_filename = 't0run.log',
		))

        if args.interactive is not None:
            implementation.addMonitor(MakeInteractive(trigger=args.interactive))

	implementation.run()
	implementation.close()

if __name__=='__main__':
	main()

