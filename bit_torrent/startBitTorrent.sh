#!/bin/bash
clear
while true; do
	printf " ______                   _______                                                   \n"
	printf "|  ___ \  _  _______     |__   __| ______  _____   _____   ______  __    _  _______ \n"
	printf "| |   | || ||__   __|       | |   |  __  ||  __ \ |  __ \ |  ____||  \  | ||__   __|\n"
	printf "| |__/ / | |   | |          | |   | |  | || |__| || |__| || |__   |   \ | |   | |   \n"
	printf "|  __ (  | |   | |          | |   | |  | ||    _/ |    _/ |  __|  | |\ \| |   | |   \n"
	printf "| |  \ \ | |   | |          | |   | |  | || |\ \  | |\ \  | |     | | \ | |   | |   \n"
	printf "| |___| || |   | |          | |   | |__| || | \ \ | | \ \ | |____ | |  \  |   | |   \n"
	printf "|______/ |_|   |_|          |_|   |______||_|  \_\|_|  \_\|______||_|   \_|   |_|   \n"
	printf "\n"
	printf "Sei un client o un server?\n1 - Client\n0 - Server\n"
	echo -n "Scelta: "
	read scelta
	
	case $scelta in  
	  1) echo "Start Client";
	  	 break;;
	  0) echo "Start Server";
	  	 break;;
	  *) clear;;
	esac
done
case $scelta in
	1) sh -c "python3 clientBitTorrent.py";;
	0) sh -c "python3 serverBitTorrent.py";;
esac

