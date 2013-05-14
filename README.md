cloud-init-cern
===============

Additional Cloud-init modules developed in order to contextualize services to executed LHC experiments jobs.

More information can be found here:
https://twiki.cern.ch/twiki/bin/view/LCG/CloudInit

IN THIS DIRECTORY YOU CAN FIND THE CLOUDINIT MODULES FOR THE INSTALLATION AND CONFIGURATION OF GANGLIA, CVMFS AND CONDOR.

THESE ARE CLOUD CONFIG MODULES, WHICH MEANS AFTER THEY ARE CORRECTLY INSTALLED IN YOUR IMAGE YOU'LL BE ABLE TO EASILY CONFIGURE THOSE THREE SERVICES THROUGH USER-DATA.

YOU CAN FIND THE DETAILED EXPLANATION OF THESE MODULES IN THE FOLLOWING TWIKI PAGE: https://twiki.cern.ch/twiki/bin/view/LCG/CloudInit

YOU ARE FREE TO DOWNLOAD THEM, TEST THEM AND MODIFY THEM AS YOU LIKE AND NEED.

HERE'S A BRIEF SUMMARY OF WHAT YOU NEED TO DO TO USE THESE MODULES:

 -> Download the three modules to an instance where you already have the CloudInit package installed, and move 	them to the Python modules directory (where all of the other Cloud Config modules are): /usr/lib/python2.6/site-packages/cloudinit/CloudConfig/

 -> Edit the file /etc/cloud/cloud.cfg and add these three lines to the 'cloud_config_modules' section:

		 - condor
		 - ganglia
		 - cvmfs

 -> EXTRA STEP: if you are planning to do extensive testing and/or use these modules as default I would suggest you to either snapshot the current instance or bake your own Cloud Image from scratch with these modules included.

 -> Create your user-data file using the Cloud Config structure and refer to the services you want to install and configure.
You can configure several parameters for each one of the services. Here are two minimal examples of user-data files that you could use during instantiation:
To create a simple node:
	

	#cloud-config

	cvmfs:
	 local:
	  repositories: grid.cern.ch
	  http-proxy: DIRECT

	ganglia:
	 nodes:	
	  udpSendChannel:
	   host: yourheadnode.com
   
	condor:
	 workernode:
	  condor-host: yourcondormaster.com
	  daemon-list: MASTER, STARTD

To create a master headnode:


	#cloud-config

	condor:
 	 master:
	  lowport: 21000
  	  highport: 24500
 
	ganglia:
 	 headnode:
	  source: '"my cluster"'

ALWAYS REMEMBER TO PUT '#cloud-config' IN YOUR FIRST LINE AND TO RESPECTIVE WHITE-SPACES.


Cristóvão Cordeiro, 26/04/2013, christovao.jose.domingues.cordeiro@cern.ch

