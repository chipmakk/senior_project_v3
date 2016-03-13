#!/bin/bash
echo "Added user " $1 $2

echo hellocheckin | sudo -S sudo useradd -m $1 -s /bin/bash
echo hellocheckin | sudo -S sudo echo "$1:$2" | sudo chpasswd
