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

from urlparse import urlparse
import os

class Groups(dict): pass

class Group(object):
	def __init__(self, name, items=[], preBackupJob=''):
		self.name = name
		self.items = items
		self.preBackupJob = preBackupJob
	
	def add(self, url, addAnyways=False):
		if url not in self.items:
			url = urlparse(url)
			valid = True
			if url.scheme == 'file':
				valid = os.path.exists(url.path)
			if valid or addAnyways:
				print("Adding item {0} to group {1}".format(url, self.name))
				self.items.append(url)
	
	def remove(self, url):
		self.items.remove(urlparse(url))
