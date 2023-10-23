#!/bin/sh

#Simulating some activities
sleep 3
cat /etc/passwd > /tmp/extracted_users.txt
sleep 5
ls /tmp
cat /tmp/extracted_users.txt
