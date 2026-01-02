from datetime import datetime
import os
import pathlib
import subprocess

server_name = '192.168.1.16'
shares = ['common', 'abi', 'ham', 'threans', 'guest']
password = pathlib.Path('password.txt').read_text().strip()

rsyncs: list[subprocess.Popen] = []
for share_name in shares:
    mount_path = f'/mnt/{share_name}'
    os.makedirs(mount_path, exist_ok=True)
    subprocess.run(['umount', mount_path])
    subprocess.run([
        'mount', '-t', 'cifs', f'//{server_name}/{share_name}', mount_path,
        '-o', f'username=smb-backup,password={password}'
    ], check=True)

    print(f'mounted {mount_path}')
    rsyncs.append(subprocess.Popen(
        ['rsync', '-a', mount_path, f'/raid/{share_name}'],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    ))

for rsync in rsyncs:
    stdout, stderr = rsync.communicate()
    returncode = rsync.wait()
    if returncode:
        raise RuntimeError('rsync failed', stdout, stderr)
    else:
        print('rsync complete')

with open('/mnt/common/beans/backup-report.txt', 'w') as f:
    f.write(f'Backup completed {datetime.now().strftime("%Y-%b-%d %H:%M")}')