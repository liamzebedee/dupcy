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

class Links(list):
	def backupSource(self, sourceGroupName):
		# TODO
		pass
	
	def getLinkForTargetGroup(self, targetGroup):
		for link in self:
			if link.targetGroup is targetGroup:
				return link
		return None

class Link(object):
	def __init__(self, sourceGroups, targetGroup, pre='', post=''):
		self.sourceGroups = sourceGroups
		self.targetGroup = targetGroup
		self.lastModified = time()
		self.pre = pre
		self.post = post
	
	def doneSomething(self):
		"""Updates the lastModified attribute (should be called after something is done)"""
		self.lastModified = time()
	
	def duplicity(self, cmds):
		call(["duplicity", "--name='{0}'".format(self.targetGroup.name)] + cmds)
	
	def getTarget(self): return self.targetGroup.items[0].geturl()
	
	def backup(self):
		# Ugly. XXX interact with API directly
		includes = ['--include "{0}"'.format(source.path) for source in self.sourceGroups.items()]
		self.duplicity(includes + ["--exclude /", "/", self.getTarget()])
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
			options.append('--file-to-restore "{0}"'.format(_file))
		if time is not '':
			options.append('--time "{0}'.format(time))
		self.duplicity(['restore'] + options + [self.getTarget(), path])
		self.doneSomething()
