###Normal (Simple) Way
sudo port install bitcoind 

if you *recently* update to Mavericks without migrating your macports accordingly, the installation will most likely to break. (The ports dependencies won't work.) 
- This guide talks about how to migrate your macports.[[https://trac.macports.org/wiki/Migration][migrate]]
	- step 1: update your xcode (this includes running "xcode-select --install)
	- step 2: [[https://distfiles.macports.org/MacPorts/MacPorts-2.2.1-10.9-Mavericks.pkg][download]] the macports for mavericks and install it
	- step 3: Reinstall ports
		- port -qv installed > myports.txt
		- sudo port -f uninstall installed
		- sudo port clean all 
		- sudo port install portname +variant1 +variant2 #Install "portname" one by one by browsing myports.txt
			- alternative, you can reinstall ports all in once.
	- setp 4: sudo port install bitcoind 
	
###start bitcoind as daemon 
	- Step 1: ln -s ~/Library/Application\ Support/Bitcoin ~/.bitcoin
	- Step 2: touch ~/.bitcoin/bitcoin.conf
	- Step 3: chmod 400 ~/.bitcoin/bitcoin.conf(daemonize won't work if it is owner-read only)
	- Step 4: bitcoind -conf=~/.bitcoin/bitcoin.conf -daemon -reindex
 
