# Copyright 2013 Liam Edwards-Playne.
#
# This file is part of Dupcy.
#
# Dupcy is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Dupcy is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Dupcy.  If not, see <http://www.gnu.org/licenses/>.

import dupcy
from time import time
from util import getSecondsUntilRelativeTime, getpwd

import pyev
from shutil import copy2
from subprocess import call
import os

class Links(dict):
	"""key: target group name
	   value: corresponding Link """
	
	def backupSource(self, sourceGroupName):
		# TODO
		pass
	
	def backupTarget(self, targetName, config='', full=False):
		url = self[targetName].targetGroup.items[0]
		if url.scheme == 'file':
			if not os.path.exists(url.path):
				return False
		
		self[targetName].backup(full)
		if config is not '':
			if url.scheme == 'file':
				copy2(config, url.path)
	
	def updateWatchers(self, eventLoop):
		for link in self.values():
			link.updateWatcher(eventLoop)

class Link(object):
	def __init__(self, sourceGroups, targetGroup, time=''):
		"""sourceGroups: a dictionary of group name to group
		targetGroup: a single group"""
		self.sourceGroups = sourceGroups
		self.targetGroup = targetGroup
		self.time = time
		self.watcher = None
		self.doneSomething()
	
	def __getstate__(self):
		d = dict(self.__dict__)
		d['watcher'] = None
		return d		
	
	def doneSomething(self):
		"""Updates the lastModified attribute (should be called after something is done)"""
		self.lastModified = time()
	
	def duplicity(self, mode, cmds):
		os.environ['PASSPHRASE'] = getpwd()
		full = ["duplicity", mode, "--name='{0}'".format(self.targetGroup.name)] + cmds
		print("> {0}".format(full))
		call(full)
		del os.environ['PASSPHRASE']
	
	def getTarget(self):
		return self.targetGroup.items[0].geturl()
	
	def backup(self, full=True):
		# Ugly. XXX interact with API directly
		includes = []
		for k, group in self.sourceGroups.items():
			for item in group.items:
				includes.append('--include={0}'.format(item.path))
		self.duplicity("full" if full else "incremental", includes + ["--exclude=**", "/", self.getTarget()])
		self.doneSomething()
	
	def restore(self, path='/', _file='/', time=''):
		"""
		Restores to path (by default '/') from this link's target, optionally a 
		specific file from a specific time.
		@param path absolute path
		@param _file relative path to file or directory
		"""
		options = []
		if _file is not '/':
			options.append('--file-to-restore="{0}"'.format(_file))
		if time is not '':
			options.append('--time="{0}'.format(time))
		self.duplicity("restore", options + [self.getTarget(), path])
		self.doneSomething()
		
	def updateWatcher(self, eventLoop):
		if self.time == '': return
		# convert relative time string to an absolute value of the next backup
		absoluteTime = getSecondsUntilRelativeTime(self.time)
		if self.watcher is not None: self.watcher.stop()
		def backupWrapper(watcher, revents):
			self.backup(True)
		self.watcher = pyev.Periodic(eventLoop.now() + absoluteTime, 0.0, eventLoop, backupWrapper)
		self.watcher.start()
		self.doneSomething()
