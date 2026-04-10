.PHONY: all config build

all: config build

config:
	cd rpi-image-gen && sudo ./install_deps.sh

build:
	cd rpi-image-gen && sudo git clean -fdx .
	cd rpi-image-gen && ./rpi-image-gen build -S ../bicycleimage/ -c bicycledata.yaml
