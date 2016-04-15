#!/bin/bash

for i in auto ; do
  cat << EOF > /etc/systemd/system/cs312-${i}@.service
[Unit]
Description=cs312-${i} %I

[Service]
ExecStart=/usr/bin/python3 /auto/cli/rest_listener.py %I
WorkingDirectory=/auto/cli/
Type=simple
User=root
Group=root

[Install]
WantedBy=multi-user.target
EOF
done

systemd_path=/etc/systemd/system
ln -sf ${systemd_path}/cs312-auto@.service ${systemd_path}/cs312-auto@443.service


systemctl daemon-reload
systemctl start cs312-auto@443
