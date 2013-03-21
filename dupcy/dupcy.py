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
from util import getSecondsUntilRelativeTime

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
	
	config['groups'][group.name] = group
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
	try:
		dateutil.parser.parse(args.time)
	except Exception as e: # TODO use right exception for dateutil.parser
		print("Error: invalid backup time string - {0}".format(e))
		return
	# XXX implement

def remLink(args): pass
def listLinks(args): pass

def backupSource(args): pass
def backupTarget(args): pass
def backupAll(args): pass
def restore(args): pass
def importConfig(args): pass
def exportConfig(args): pass

def processJob(job, eventLoop):
	cmd = job.cmd
	parser = argparse.ArgumentParser()
	parser.set_defaults(log=job.printToConn, eventLoop=eventLoop)
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
	pLinkX_rem.add_argument('sourceGroup', type=str)
	pLinkX_rem.add_argument('targetGroup', type=str)
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
	pRestore = subparser.add_parser('restore')
	
	pRestore.add_argument('source', type=str)
	pRestore.add_argument('--time', type=str)
	pRestore.add_argument('--from', type=str)
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
	args = parser.parse_args(cmd)
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

def initDefaultConfigState():
	defaults = {
		'groups': Groups(),
		'links': Links(),
		'jobs': Jobs(),
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
	
	global config
	config = shelve.open(os.path.join(GLib.get_user_config_dir(), 'dupcy'), writeback=True)
	initDefaultConfigState()
	
	# XXX consider increasing timeout interval to improve performance, events are rarely added 
	eventLoop = pyev.default_loop()
	watchers = []
	
	def handle_new_client(watcher, revents):
		conn = ln.accept()
		job = Job(conn.recv(), conn)
		if job.cmd is None or len(job.cmd) == 0:
			# XXX best to remove this, use try catch for processJob below instead
			job.printToConn("Error: command is malformed")
			conn.close()
			return
		config['jobs'].append(job.cmd)
		config.sync()
		try:
			processJob(job, eventLoop)
		except Exception as e:
			job.printToConn("Error: {0}".format(e))
		config['jobs'].remove(job.cmd)
		config.sync()
		conn.close()
	clientListener = pyev.Io(ln._listener._socket, pyev.EV_READ, eventLoop, handle_new_client)
	watchers.append(clientListener)
	
	def shutdown(watcher, revents):
		ln.close()
		config.close()
		eventLoop.stop(pyev.EVBREAK_ALL)
	watchers.extend([pyev.Signal(sig, eventLoop, shutdown) for sig in STOPSIGNALS])
	
	def backupLink(watcher, revents): pass # XXX implement
	links = config['links']
	for link in links:
		if link.time == '': continue
		# convert relative time string to an absolute value of the next backup
		absoluteTime = util.getSecondsUntilRelativeTime(link.time)
		watchers.append(pyev.Periodic(absoluteTime, 0.0, eventLoop, backupLink, link))
	
	for watcher in watchers: watcher.start()
	del watchers
	eventLoop.start()

if __name__ == "__main__":
	main()
