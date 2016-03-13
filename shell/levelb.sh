#!/bin/bash
echo $1
echo hellocheckin | sudo -S sudo adduser $1 levelb
#sudo useradd -G level2 $1