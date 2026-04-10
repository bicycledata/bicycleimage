[Unit]
Description=bicycledata service
After=expand-rootfs.service network.target NetworkManager.service
Wants=expand-rootfs.service NetworkManager.service

[Service]
User=$BICYCLEDATA_USER
Group=$BICYCLEDATA_USER
WorkingDirectory=/home/$BICYCLEDATA_USER/bicycleinit
ExecStart=/home/$BICYCLEDATA_USER/bicycleinit/.env/bin/python3 bicycleinit.py

Restart=always
RestartSec=15
StartLimitInterval=0
StartLimitBurst=0

[Install]
WantedBy=multi-user.target
