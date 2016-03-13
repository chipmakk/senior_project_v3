#!/bin/sh
echo hellocheckin | sudo -S echo "User Removed " $1 $2

echo hellocheckin | sudo -S sudo userdel $1
