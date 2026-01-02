
import os
import pathlib
import subprocess

server_name = '192.168.0.16'
shares = ['common', 'abi', 'ham', 'threans', 'guest']
password = pathlib.Path('password.txt').read_text()

rsyncs: list[subprocess.Popen] = []
for share_name in shares:
    os.makedirs(f'/mnt/{share_name}', exist_ok=True)
    subprocess.run([
        'mount', '-t', 'cifs', f'//{server_name}/{share_name}', f'/mnt/{share_name}',
        '-o', f'username=smb-backup,password={password}'
    ], check=True)

    rsyncs.append(subprocess.Popen(
        ['rsync', '-a', f'/mnt/{share_name}', f'/raid/{share_name}'],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    ))

for rsync in rsyncs:
    stdout, stderr = rsync.communicate()
    returncode = rsync.wait()
    if returncode:
        raise RuntimeError('rsync failed', stdout, stderr)
