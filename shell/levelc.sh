#!/bin/bash
echo $1
echo hellocheckin | sudo -S sudo adduser $1 levelc
#sudo useradd -G level2 $1