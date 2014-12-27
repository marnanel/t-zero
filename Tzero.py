from subprocess import Popen
from time import sleep
import os
import re

class Tzero:

	LOGFILE = 'orig/T-ZERO.SCR'

	def __init__(self):
		print 'Starting Dosbox'
		self._dosbox = Popen(['dosbox', '-conf', 't0.dosbox.conf'])
		print 'PID of Dosbox is', self._dosbox.pid

		print 'Sleeping to allow game to start'
		sleep(10)

		# This is very Linux-specific
		# ...and turned out not to be necessary :)
		#environ = file('/proc/%d/environ' % (self._dosbox.pid,)).read()
		#widindex = environ.index('WINDOWID=')
		#windowid = environ[widindex+9:environ.index(chr(0), widindex)]
		#self._window = hex(int(windowid))
		#print 'Window ID is', self._window

		# the _ is to bypass the initial "More?" prompt
		self.send('_LOG')
		self.send('MORE')

		self._logfile = file(self.LOGFILE, 'r')
		self._set_logsize()

	def _set_logsize(self):
		self._logsize = os.stat(self.LOGFILE).st_size

	def send(self, command, pressEnter=True):
		"""
		Sends a command to the game (using xte).
		Returns nothing. If you want to see the response,
		look at converse().
		"""

		args = ['xte']
		args.append('str '+command)
		if pressEnter:
			args.append('key Return')
			#args.extend(['keydown Control_L', 'key m', 'keyup Control_L'])

		Popen(args).wait()
		sleep(1)

	def converse(self, command, pressEnter=True):
		"""
		Sends a command to the game,
		and returns the game's response.
		"""
		logsize_before = self._logsize
		self.send(command, pressEnter=pressEnter)
		self._set_logsize()

		self._logfile.seek(logsize_before)
		answer = self._logfile.read(self._logsize - logsize_before)

		return answer

	def save(self, filename):
		# Special case because this comes up a lot

		answer = self.converse('SAVE '+filename)

		if 'overwrite' in answer:
			answer = self.converse('y', pressEnter=False)

		return answer

	def restore(self, filename):
		# just for parallelism
		return self.converse('RESTORE '+filename)

	def move(self, direction):
		"""
		'direction' is a direction (NORTH, EAST, SOUTH, WEST, UP, DOWN, IN, OUT,
		or their abbreviations)

		Returns a string;
		if we moved successfully it will be
		the new room name, possibly including the description;
		if we didn't move successfully it will be
		the error message prefixed with "!".
		"""
		result = self.converse(direction).split('\r\n')
		# result[0] is the command we just gave.
		# The last few lines of result are the next prompt.
		# If result[1] is empty, then the move was successful.
		if result[1]=='':
			return '\n'.join(result[2:-2])
		else:
			return '!'+'\n'.join(result[1:-4])
		return result

	def close(self):
		self.send('QUIT')
		self.send('Y')

def make_filename(s):
	s = s.upper()
	result = s[0]+re.subn(r'([AEIOU]|\W)', '', s[1:])[0]
	return result[:8]

if __name__=='__main__':
	print make_filename('UpRiver.')
