**Software is incomplete for usage**.

Dupcee is a frontend and wrapper to the *duplicity* backup program, making advanced backups **simpler** and more **user-friendly**. It is a **free** program licensed under the GPLv3.

# Dupcee
Dupcee starts with two concepts: the **source** and the **target**. **Sources** are places on your computer where files are stored, **targets** are places where you want to backup these files to. 

Sources and targets are grouped into source and target **groups**. We **link** source and target groups together to form the backup process.

Groups are a powerful abstraction when used correctly. For example, when I created this program I had 2 things I needed to backup - schoolwork and media. I had multiple places where school-related data was stored, as well as for media. I also had 2 different backup targets, a USB and a HDD. My media folder was huge, so it wouldn't fit on the USB, but my schoolwork would. **I needed a way to backup multiple sources to different targets, but only backup some sources depending on the target**. What I did was created a source group *school* and a source group called *media*, and likewise two target groups *hdd* and *usb*. I created a backup link between *school*/*media* and *hdd*, and another between *school* and *usb*.

**Links** are very flexible, as they can be configured to backup only when certain conditions are met, and can also exectute pre/post backup jobs.

## Commands
* Add a group with name, optionally pre job
* Remove a group by its name

* Add a URL to a group by its name, optionally forced
* Remove a URL from a group

* Add a link between a source group and a target group, optionally doing by time or by when it changes
* Remove a link between a source group and a target group

* Backup a source, optionally fully, to a specific target
* Backup a target, optionally a full backup
* Backup everything
* Restore a source, optionally according to a time, from a specific target

* Load config from URL
* Export config to URL

## Comparison
To duplicity:
* Every location is specified in URL form. e.g. file:///home/liamzebedee instead of /home/liamzebedee
* There is an overhead of storing configuration data in comparison to duplicity, which is standalone - this is required to store source groups etc.
* Backups can be scheduled. 

To duply:
* The configuration data needs not be backed up seperately - it is by default automatically backed up with the data. 
