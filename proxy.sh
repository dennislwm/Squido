#!/usr/bin

clear
user=
pass=
port=

echo "Updating and installing prerequisites"
apt-get update -y && apt-get install squid -y && apt-get install apache2-utils -y

if [ -f "/etc/squid3/tmpfile" ];
then
	echo "Removing old files"
	rm /etc/squid3/tmpfile -f
else
	echo "No files to remove"
fi

if [ -f "/etc/squid3/squid.conf" ];
then
        echo "Backing up original squid config file"
        mv /etc/squid3/squid.conf /etc/squid3/squid.conf.bak
else
        echo "No squid config file found, nothing to backup"
fi

IPS=`ifconfig | grep 'inet addr:' | awk {'print $2'}  | grep -v '127.0.0.' | sed -e 's/addr://'`
for i in $IPS;
do printf $i'\n';
done

echo "Retrieving basic squid config and configuring IPs"
mv /usr/src/squid.conf /etc/squid3/squid.conf

# Loop round all IP addresses
x=0
for i in $IPS;
do
   :
   x=`expr $x + 1`
   printf "acl ip$x myip $i\n" >> /etc/squid3/tmpfile
   printf "tcp_outgoing_address $i ip$x\n\n" >> /etc/squid3/tmpfile
done


cat /etc/squid3/squid.conf >> /etc/squid3/tmpfile
mv /etc/squid3/tmpfile  /etc/squid3/squid.conf

echo "Adding $user to allowed users"
if [ -f "/etc/squid3/squid_passwd" ];
then
       	htpasswd -b /etc/squid3/squid_passwd $user $pass 
else
        htpasswd -c -b /etc/squid3/squid_passwd $user $pass
fi

echo "Restarting Squid"
service squid3 restart

echo "Install finished - you should now be able to connect to any of the IPs on port $port"

IPS=`ifconfig | grep 'inet addr:' | awk {'print $2'}  | grep -v '127.0.0.' | sed -e 's/addr://'`
for i in $IPS;
do printf $i:$port:$user:$pass'\n';
done
