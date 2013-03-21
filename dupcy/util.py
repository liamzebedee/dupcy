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

import os
import dateutil.parser
from datetime import datetime

def make_sure_dir_exists(path):
	try:
		os.makedirs(path)
	except OSError as exception:
		if exception.errno != errno.EEXIST:
			raise

def getSecondsUntilRelativeTime(timeStr):
	t = dateutil.parser.parse(timeStr)
	return (t - datetime.now()).total_seconds()
