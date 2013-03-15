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
		
	def backup(self):
		# Ugly. XXX interact with API directly
		self._includes = ['--include "{0}"'.format(source.path) for source in self.sourceGroups.items()]
		call([	"duplicity", 
			 	"--name='{0}'".format(self.targetGroup.name)] +
			 	self._includes +
			 	["--exclude /",
			 	"/", self.target.items[0].geturl()])
		self.doneSomething()
	
	def restore(self, path): pass
