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

from link import *
from group import *
from job import *

import sys
import argparse
from multiprocessing.connection import Listener, Client
import socket
import yapdi
import thread
from gi.repository import GLib
import os
import shelve
import pyev
import signal
import dateutil.parser

address = ('localhost', 19340)
configLocation = os.path.join(GLib.get_user_config_dir(), 'dupcy')

def addGroup(args):
	args.log('Processing group')
	group = config['groups'].get(args.name, Group(args.name))
	
	if args.force and args.preBackupJob is not None:
		args.log('Set new pre backup job')
		group.preBackupJob = args.preBackupJob
	if args.items is not None:
		args.log('Adding new items to group') 
		for item in args.items:
			group.add(item, addAnyways=args.force)
	args.log('Saving configuration')
	
	config['groups'][args.name] = group
	config.sync()

def remGroup(args):
	if args.items is None:
		args.log('Deleting group')
		del config['groups'][args.name]
	else:
		group = config['groups'][args.name]
		args.log('Deleting items')
		for item in args.items:
			group.remove(item)
	config.sync()

def listGroups(args):
	groups = config['groups']
	for name, group in groups.iteritems():
		args.log("= {0} =".format(name))
		for item in group.items:
			args.log(item.geturl())
		args.log("")

def addLink(args):
	if args.time is not None:
		try:
			dateutil.parser.parse(args.time)
		except ValueError as e:
			print("Error: invalid backup time string - {0}".format(e))
			return
	args.log('Processing link')
	default = Link({}, config['groups'][args.targetGroup])
	link = config['links'].get(args.targetGroup, default)
	sourceGroup = config['groups'][args.sourceGroup]
	if sourceGroup is None:
		args.log('Source group {0} does not exist, aborting.'.format(args.sourceGroup))
		return
	link.sourceGroups[args.sourceGroup] = sourceGroup
	if args.time is not None:
		link.time = args.time
		link.doneSomething()
		args.log("Adding countdown timer for backup")
		link.updateWatcher(eventLoop)
	
	args.log("Saving configuration")
	config['links'][link.targetGroup.name] = link
	config.sync()

def remLink(args):
	link = config['links'].get(args.targetGroup)
	if link is None: return
	
	if args.sourceGroup is not None:
		del link.sourceGroups[args.sourceGroup]		
	else:
		if link.watcher is not None: link.watcher.stop()
		del config['links'][args.targetGroup]
	config.sync()

def listLinks(args):
	links = config['links']
	for name, link in links.iteritems():
		args.log("= {0} =".format(name))
		[args.log(k) for k, v in link.sourceGroups.items()]
		args.log("")

def backupSource(args):	
	# source --to --full
	pass

def backupTarget(args):
	if not config['links'].has_key(args.target):
		args.log("Not backing up: no such target exists")
		return
	args.log("Backup in progress")
	
	config['links'].backupTarget(args.target, configLocation, args.full)
	args.log("Backup complete")
	config.sync()

def backupAll(args): pass
def restore(args):
	# args.source from to
	if args.fromTarget is not '':
		fromTarget = config['links'][args.fromTarget]
		fromTarget.restore(args.to)

def importConfig(args): pass
def exportConfig(args): pass

def processJob(job):
	cmd = job.cmd
	parser = argparse.ArgumentParser()
	parser.set_defaults(log=job.printToConn, job=job)
	subparser = parser.add_subparsers()
	
	# dupcee group
	pGroup = subparser.add_parser('group')
	pGroupX = pGroup.add_subparsers()
	
	pGroupX_add = pGroupX.add_parser('add')
	pGroupX_add.add_argument('name', type=str)
	pGroupX_add.add_argument('--pre-backup-job', type=str)
	pGroupX_add.add_argument('--force', action="store_true")
	pGroupX_add.add_argument('--items', nargs='*')
	pGroupX_add.set_defaults(func=addGroup)
	
	pGroupX_rem = pGroupX.add_parser('remove')
	pGroupX_rem.add_argument('name', type=str)
	pGroupX_rem.add_argument('--items', nargs='*')
	pGroupX_rem.set_defaults(func=remGroup)
	
	pGroupX_list = pGroupX.add_parser('list')
	pGroupX_list.set_defaults(func=listGroups)
	
	# dupcee link
	pLink = subparser.add_parser('link')
	pLinkX = pLink.add_subparsers()
	
	pLinkX_add = pLinkX.add_parser('add')
	pLinkX_add.add_argument('sourceGroup', type=str)
	pLinkX_add.add_argument('targetGroup', type=str)
	pLinkX_add.add_argument('--time', type=str)
	pLinkX_add.set_defaults(func=addLink)
	
	pLinkX_rem = pLinkX.add_parser('remove')
	pLinkX_rem.add_argument('targetGroup', type=str)
	pLinkX_rem.add_argument('--sourceGroup', type=str)
	pLinkX_rem.set_defaults(func=remLink)
	
	pLinkX_list = pLinkX.add_parser('list')
	pLinkX_list.set_defaults(func=listLinks)
	
	# dupcee backup
	pBackup = subparser.add_parser('backup')
	pBackupX = pBackup.add_subparsers()

	pBackupX_source = pBackupX.add_parser('source')
	pBackupX_source.add_argument('source', type=str)
	pBackupX_source.add_argument('--to', type=str)
	pBackupX_source.add_argument('--full', action="store_true")
	pBackupX_source.set_defaults(func=backupSource)
	
	pBackupX_target = pBackupX.add_parser('target')
	pBackupX_target.add_argument('target', type=str)
	pBackupX_target.add_argument('--full', action="store_true")
	pBackupX_target.set_defaults(func=backupTarget)
	
	pBackupX_all = pBackupX.add_parser('all')
	
	# dupcee restore
	# dupcy restore --source 1 --from hdd --to /home/liamzebedee/Documents/test1
	pRestore = subparser.add_parser('restore')
	
	pRestore.add_argument('source', type=str)
	#pRestore.add_argument('--time', type=str)
	#pRestore.add_argument('--sourceFile', type=str)
	pRestore.add_argument('--fromTarget', type=str)
	pRestore.add_argument('--to', type=str)
	pRestore.set_defaults(func=restore)
	
	# dupcee config
	pConfig = subparser.add_parser('config')
	pConfigX = pConfig.add_subparsers()
	
	pConfig_import = pConfigX.add_parser('import')
	pConfig_import.add_argument('importPath', type=str)
	pConfig_import.set_defaults(func=importConfig)
	
	pConfig_export = pConfigX.add_parser('export')
	pConfig_export.add_argument('exportPath', type=str)
	pConfig_export.set_defaults(func=exportConfig)
	
	# setup
	try:
		args = parser.parse_args(cmd)
	except:
		job.printToConn("Error: Malformed command. See the README for a guide on commands.")
		return
	args.func(args)
	job.printToConn("Finished.")

def client(cmd):
	"""Sends a command cmd to the daemon, and outputs the response"""
	conn = Client(address)
	conn.send(cmd)
	while True:
		try:
			print(conn.recv())
		except EOFError:
			return

def loadConfig():
	"""Loads the config, this can also be used for debugging"""
	global config
	config = shelve.open(configLocation, writeback=True)

def getConfig():
	global config
	loadConfig()
	return config

def initDefaultConfigState():
	defaults = {
		'groups': Groups(),
		'links': Links(),
	}
	for k, v in defaults.iteritems():
		if k not in config or config[k] is None:
			print("Initialising config '{0}'".format(k))
			config[k] = v

def main():
	STOPSIGNALS = (signal.SIGINT, signal.SIGTERM)	
	
	try:
		ln = Listener(address)
	except socket.error, e:
		# TODO check for specific error
		# Daemon already running
		client(sys.argv[1:])
		return
	
	daemon = yapdi.Daemon()
	#daemon.daemonize() XXX debug
	
	loadConfig()
	initDefaultConfigState()
	
	# XXX consider increasing timeout interval to improve performance, events are rarely added 
	global eventLoop
	eventLoop = pyev.default_loop()
	watchers = []
	
	def handle_new_client(watcher, revents):
		conn = ln.accept()
		job = Job(conn.recv(), conn)
		try:
			processJob(job)
		except Exception as e:
			job.printToConn("Error running job: {0}".format(e))
		conn.close()
	clientListener = pyev.Io(ln._listener._socket, pyev.EV_READ, eventLoop, handle_new_client)
	watchers.append(clientListener)
	
	def shutdown(watcher, revents):
		ln.close()
		config.close()
		eventLoop.stop(pyev.EVBREAK_ALL)
	watchers.extend([pyev.Signal(sig, eventLoop, shutdown) for sig in STOPSIGNALS])
	
	config['links'].updateWatchers(eventLoop)
	config.sync()
	
	for watcher in watchers: watcher.start()
	del watchers
	eventLoop.start()

if __name__ == "__main__":
	main()
