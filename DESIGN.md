**dupcy** is both a daemon and a client to such daemon.

The daemon is started by running "*dupcy start*". Upon startup, it performs the following:
* Opens the unix domain socket for communication with the client. 
* Find and loads the configuration file
* Iterates through all the links.
** Checks any links that are due to update at a certain time, and if the time that they were last modified was more than 24 hours ago, add their backup job to the jobs queue. 
** Set backup timers for existing links with set backup times.
* Start the main loop to process jobs.

That is the basis of the daemon. The client interfaces with the daemon through the command line, sending commands via the unix domain socket, also starting the daemon if necessary. 
