import paramiko
import csv
import datetime
import os,time

def times():
    today = str(datetime.datetime.today()).split(' ')
    time=today[1].split('.')
    t=""+today[0]+' '+time[0]+''
    return t

if __name__=="__main__":
    print "Time    : %s"%times()
    path=os.path.dirname(os.path.abspath(__file__))

    conf=open(os.path.join(path,'conf.txt'),'r').readlines()
    proxyUsername=str(str(conf[0]).split('=')[1]).strip()
    proxyPassword=str(str(conf[1]).split('=')[1]).strip()
    proxyPort=str(str(conf[2]).split('=')[1]).strip()
    proxySh=open(os.path.join(path,'proxy.sh'),'r').read()
    proxySh=proxySh.replace('user=','user=%s'%(str(proxyUsername))).replace('pass=','pass=%s'%(str(proxyPassword))).replace('port=','port=%s'%(str(proxyPort)))
    open(os.path.join(path,'proxy2.sh'),'wb').write(proxySh)
    time.sleep(1)
    squidSh=open(os.path.join(path,'squid.conf'),'r').read()
    squidSh=squidSh.replace('http_port 0.0.0.0:','http_port 0.0.0.0:%s'%(str(proxyPort)))
    open(os.path.join(path,'squid2.conf'),'wb').write(squidSh)
    time.sleep(1)
    with open('servers.csv', 'rb') as csvfile:
        reader = csv.reader(csvfile)
        your_list = list(reader)

    for item1 in your_list:
        host = item1[0]
        username = item1[1]
        password = item1[2]
        port = 22

        pathProxy = '/usr/src/proxy.sh'
        proxy = os.path.join(path,'proxy2.sh')
        pathConfig = '/usr/src/squid.conf'
        config = os.path.join(path,'squid2.conf')
        transport = paramiko.Transport((host, port))
        transport.connect(username = username, password = password)
        sftp = paramiko.SFTPClient.from_transport(transport)
        sftp.put(proxy, pathProxy)
        sftp.put(config, pathConfig)
        sftp.close()
        transport.close()
        print "Copied SquidProxy Script To Server " + "........" + host
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, username=username, password=password, port=22)
        print "Installing SquidProxy Script To Server " + "........" + host
        #
        sleeptime = 0.001
        outdata, errdata = '', ''
        ssh_transp = ssh.get_transport()
        chan = ssh_transp.open_session()
        # chan.settimeout(3 * 60 * 60)
        chan.setblocking(0)
        chan.exec_command('cd /usr/src && sh proxy.sh')
        while True:  # monitoring process
            # Reading from output streams
            while chan.recv_ready():
                outdata += chan.recv(1000)
            while chan.recv_stderr_ready():
                errdata += chan.recv_stderr(1000)
            if chan.exit_status_ready():  # If completed
                break
            time.sleep(sleeptime)
        retcode = chan.recv_exit_status()
        ssh_transp.close()

        print(outdata)
        for x in str(outdata).splitlines():
            if proxyPassword in x:
                open(os.path.join(path,'proxies.txt'),'a').write(x+'\n')
    os.remove(os.path.join(path,'squid2.conf'))
    os.remove(os.path.join(path,'proxy2.sh'))