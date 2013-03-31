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

from time import time
from util import getpwd

import pyev
from shutil import copy2
from subprocess import call
import os

class NonExistentTargetException(Exception):
	def __init__(self, value):
		self.value = value

class Links(dict):
	"""key: target group name
	   value: corresponding Link """
	
	def backupTarget(self, targetName, configLocation='', incremental=False):
		"""Performs a backup of targetName, optionally copying over the
		dupcy configuration as well as performing an incremental backup"""
		targetURL = self[targetName].targetGroup.items[0]
		
		# Check if target exists
		if targetURL.scheme == 'file':
			if not os.path.exists(url.path):
				raise NonExistentTargetException(targetName)
		
		self[targetName].backup(full)
		
		# Try to copy config
		if config is not '':
			if url.scheme == 'file':
				copy2(config, url.path)
	
	def updateWatchers(self, eventLoop):
		for link in self.values():
			link.updateWatcher(eventLoop)

class Link(object):
	def __init__(self, sourceGroups, targetGroup, time=''):
		"""sourceGroups: a dictionary of group name to group
		targetGroup: a single group
		time: a string indicating a periodic time in which this link should be backed up"""
		self.sourceGroups = sourceGroups
		self.targetGroup = targetGroup
		self.time = time
		self.watcher = None
		self.doneSomething()

	def __getstate__(self):
		d = dict(self.__dict__)
		d['watcher'] = None
		return d
	
	def getTarget(self):
		return self.targetGroup.items[0]
	
	def backup(self, incremental=False):
		includes = []
		for k, group in self.sourceGroups.items():
			for item in group.items:
				includes.append('--include={0}'.format(item.path))
		
		os.environ['PASSPHRASE'] = getpwd()
		cmdList = ["duplicity", 
					"incremental" if incremental else "full",
					"--name='{0}'".format(self.targetGroup.name)].extend(
					includes).extend([
					"--exclude=**",
					"/",
					self.getTarget().geturl()])
		
		print("> {0}".format(full))
		call(command)
		
		del os.environ['PASSPHRASE']
		self.doneSomething()
	
	def restore(self): pass
	
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
	
	def doneSomething(self):
		"""Updates the lastModified attribute (should be called after something is done)"""
		self.lastModified = time()
