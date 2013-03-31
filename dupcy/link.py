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

class Links(dict):
	"""key: target group name
	   value: corresponding Link """
	
	def backupSource(self, sourceGroupName):
		# TODO
		pass

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
	
	def backup(): pass
	def restore(): pass
	
	def doneSomething(self):
		"""Updates the lastModified attribute (should be called after something is done)"""
		self.lastModified = time()
