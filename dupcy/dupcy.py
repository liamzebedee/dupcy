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

import sys
import argparse

def main():
	import link
	import group

	# XXX load configuration into these globals
	links = Links()
	groups = Groups()

	pass

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	subparser = parser.add_subparsers()
	
	# dupcee group
	pGroup = subparser.add_parser('group')
	pGroupX = pGroup.add_subparsers()
	
	pGroupX_add = pGroupX.add_parser('add')
	pGroupX_add.add_argument('name', type=str)
	pGroupX_add.add_argument('--pre-backup-job', type=str)
	pGroupX_add.add_argument('--force', action="store_true")
	
	pGroupX_rem = pGroupX.add_parser('remove')
	pGroupX_rem.add_argument('name', type=str)
	
	# dupcee link
	pLink = subparser.add_parser('link')
	pLinkX = pLink.add_subparsers()
	
	pLinkX_add = pLinkX.add_parser('add')
	pLinkX_add.add_argument('sourceGroup', type=str)
	pLinkX_add.add_argument('targetGroup', type=str)
	pLinkX_add.add_argument('--time', type=str)
	
	pLinkX_rem = pLinkX.add_parser('remove')
	pLinkX_rem.add_argument('sourceGroup', type=str)
	pLinkX_rem.add_argument('targetGroup', type=str)
	
	# dupcee backup
	pBackup = subparser.add_parser('backup')
	pBackupX = pBackup.add_subparsers()

	pBackupX_source = pBackupX.add_parser('source')
	pBackupX_source.add_argument('source', type=str)
	pBackupX_source.add_argument('--to', type=str)
	pBackupX_source.add_argument('--full', action="store_true")
	
	pBackupX_target = pBackupX.add_parser('target')
	pBackupX_target.add_argument('target', type=str)
	pBackupX_target.add_argument('--full', action="store_true")
	
	pBackupX_all = pBackupX.add_parser('all')
	
	# dupcee restore
	pRestore = subparser.add_parser('restore')
	
	pRestore.add_argument('source', type=str)
	pRestore.add_argument('--time', type=str)
	pRestore.add_argument('--from', type=str)
	
	# dupcee config
	pConfig = subparser.add_parser('config')
	pConfigX = pConfig.add_subparsers()
	
	pConfig_import = pConfigX.add_parser('import')
	pConfig_import.add_argument('importPath', type=str)
	
	pConfig_export = pConfigX.add_parser('export')
	pConfig_export.add_argument('exportPath', type=str)
	
	# setup
	args = parser.parse_args()
	main()
