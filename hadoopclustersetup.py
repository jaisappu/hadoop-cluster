#!/usr/bin/python2


import commands,os
import cgi
import time


print  "content-type:text/html"
print  ""

dd=cgi.FieldStorage()

ns=dd.getvalue("n")
n=int(ns)
containerId= []

##creating docker containers for namenode
y = commands.getoutput('sudo docker run -it -d -h nn.example.com data/hadoop' )
containerId.append(y)

##creating docker container for jobtracker
y = commands.getoutput('sudo docker run -it -d -h jobt.example.com data/hadoop' )
containerId.append(y)

##creating docker container for datanodes
count=1
for i in range(n-2)  :
    y= commands.getoutput("sudo docker run -it -d -h dn"+str(count)+".example.com data/hadoop")
    containerId.append(y)
    count+=1



## putting entry in ansible hosts
count=4
f = open('/etc/ansible/hosts', 'w')
f.write('[namenode]\n')
f.write('172.17.0.2\n\n')
f.write('[jobtracker]\n')
f.write('172.17.0.3\n\n')
f.write('[datanode]\n')
for i in range(n-2) :
    f.write('172.17.0.'+str(count)+'\n')
    count+=1

f.close()

#commands.getoutput('sudo touch password.txt')
#commands.getoutput('sudo chmod 766 password.txt')
#f=open("password.txt",'w')
#f.write("q")
#f.close()

##generating an ssh key 
#commands.getoutput("sudo ssh-keygen -b 2048 -t rsa -f /tmp/sshkey -q -N "" ")

##sending the public key to the docker containers
#for i in range(n)   :
 #   commands.getoutput("sudo sshpass -f password.txt ssh-copy-id -o StrictHostKeyChecking=no 172.17.0."+str(i+2))

##creating all the required hadoop related files
commands.getoutput("sudo touch hdfs-site.xml")
commands.getoutput("sudo touch core-site.xml")
commands.getoutput("sudo touch mapred-site.xml")

commands.getoutput('sudo chmod 766 hdfs-site.xml')
commands.getoutput('sudo chmod 766 core-site.xml')
commands.getoutput('sudo chmod 766 mapred-site.xml')

##making entries in those files
##core-site.xml
f=open('core-site.xml','w')
f.write('<?xml version="1.0"?>\n<?xml-stylesheet type="text/xsl" href="configuration.xsl"?>\n')

f.write("<configuration>\n")
f.write("<property>\n<name>fs.default.name</name>\n<value>hdfs://172.17.0.2:10005</value>\n</property>\n</configuration>\n")
f.close()

stat=commands.getstatusoutput("sudo ansible all -m copy -a 'src=core-site.xml dest=/etc/hadoop/' ")


#hdfs-site.xml for datanode
f=open('hdfs-site.xml','w')
f.write('<?xml version="1.0"?>\n<?xml-stylesheet type="text/xsl" href="configuration.xsl"?>\n')
f.write('<configuration>\n<property>\n<name>dfs.data.dir</name>\n<value>/new_hadoop_dir</value>\n</property>\n</configuration>\n')
f.close()

stat=commands.getstatusoutput("sudo ansible datanode -m copy -a 'src=hdfs-site.xml dest=/etc/hadoop/' ")

#hdfs-site.xml for namenode
f=open('hdfs-site.xml','w')
f.write('<?xml version="1.0"?>\n<?xml-stylesheet type="text/xsl" href="configuration.xsl"?>\n')
f.write('<configuration>\n<property>\n<name>dfs.name.dir</name>\n<value>/metadata</value>\n</property>\n</configuration>\n')
f.close()
stat=commands.getstatusoutput("sudo ansible namenode -m copy -a 'src=hdfs-site.xml dest=/etc/hadoop/' ")


#mapred-site.xml
f=open('mapred-site.xml','w')
f.write('<?xml version="1.0"?>\n<?xml-stylesheet type="text/xsl" href="configuration.xsl"?>\n')
f.write('<configuration>\n<property>\n<name>mapred.job.tracker</name>\n<value>172.17.0.3:9001</value>\n</property>\n</configuration>\n')
f.close()

commands.getoutput("sudo ansible datanode -m copy -a 'src=mapred-site.xml dest=/etc/hadoop/'")
commands.getoutput("sudo ansible jobtracker -m copy -a 'src=mapred-site.xml dest=/etc/hadoop/'")


##starting the services for hadoop

commands.getoutput('sudo ansible  namenode  -m   shell  -a  "hadoop namenode -format" ')
time.sleep(5)
commands.getoutput('sudo ansible  namenode  -m   shell  -a  "hadoop-daemon.sh start namenode"')
commands.getoutput('sudo ansible  jobtracker -m   shell  -a  "hadoop-daemon.sh start jobtracker"')
commands.getoutput('sudo ansible  datanode  -m   shell  -a  "hadoop-daemon.sh start tasktracker"')
commands.getoutput('sudo ansible  datanode  -m   shell  -a  "hadoop-daemon.sh start datanode"')

print "<pre>"
print "<a href='http://192.168.122.1/fileupload.html'>" 
print "Click here to upload data"
print "</a>"
print "</pre>"
"""
print   "<META HTTP-EQUIV=refresh CONTENT='0 ; URL=http://192.168.122.1/cluster.html\n'>"
"""
