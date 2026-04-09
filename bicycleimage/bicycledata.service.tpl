[Unit]
Description=bicycledata service
After=network.target NetworkManager.service
Wants=NetworkManager.service

[Service]
User=$BICYCLEDATA_USER
Group=$BICYCLEDATA_USER
WorkingDirectory=/home/$BICYCLEDATA_USER/bicycleinit
ExecStart=/home/$BICYCLEDATA_USER/bicycleinit/.env/bin/python3 bicycleinit.py
Environment="BICYCLEDATA_WIFI_SSID=$BICYCLEDATA_WIFI_SSID"
Environment="BICYCLEDATA_WIFI_PSK=$BICYCLEDATA_WIFI_PSK"

Restart=always
RestartSec=15
StartLimitInterval=0
StartLimitBurst=0

[Install]
WantedBy=multi-user.target
