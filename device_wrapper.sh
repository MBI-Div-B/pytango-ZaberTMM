#!/bin/bash

# 28.2.2019
# Wrapper zum Starten ZaberTMM.py 


# Exportieren der Variable TANGO_HOST fuer die Bash-Shell

export TANGO_HOST=angstrom:10000

TANGOHOST=angstrom

#Umleiten der Ausgabe in eine Log-Datei
exec &>> /home/pi/Tango_Devices/Zaber/device.log

echo "---------------------------"
echo $(date)
echo "Tangohost: " $TANGOHOST

# Warten bis der Tangohost sich meldet
while ! timeout 0.2 ping -c 1 -n $TANGOHOST &> /dev/null
do
  :
# mache nix  
done

echo "ping Tangohost successful!"
echo "starting Zaber device"

# Fork/exec
(
  exec /usr/bin/python /home/pi/Tango_Devices/Zaber/ZaberTMM.py hhg &
) 
&>> /home/pi/Tango_Devices/Zaber/device.log 

exit 0
