**dupcy** is both a daemon and a client to such daemon.

*dupcy*:
* Try to run the daemon (see below).
* If no arguments were specified, exit now.
* Else, connect to and send the entire command to the daemon. Read the output and send it to stdout. When the socket closes, assume this means completion and exit.

Upon daemon startup, it performs the following:
* Try to listen on port 19374 - if we can't listen, assume this means the daemon is already running, and exit immediately. If we can listen, run an event loop in another thread.
** The event loop 

* Opens the unix domain socket for communication with the client. 
* Find and loads the configuration file
* Iterates through all the links.
** Checks any links that are due to update at a certain time, and if the time that they were last modified was more than 24 hours ago, add their backup job to the jobs queue. 
** Set backup timers for existing links with set backup times.
* Start the main loop to process jobs.

Dupcy daemon runs an event loop, which runs the command and sends the output.

The dupcy daemon event loop simply processes and executes jobs, which are commands that supply a file for logging. 
