[Unit]
Description=bicycledata service
After=network.target

[Service]
User=$BICYCLEDATA_USER
Group=$BICYCLEDATA_USER
WorkingDirectory=/home/$BICYCLEDATA_USER/bicycleinit
ExecStart=/home/$BICYCLEDATA_USER/bicycleinit/.env/bin/python3 bicycleinit.py

Restart=always
RestartSec=5
StartLimitInterval=0
StartLimitBurst=0

[Install]
WantedBy=multi-user.target
