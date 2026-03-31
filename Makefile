.PHONY: build

build:
	cd rpi-image-gen && sudo git clean -fdx .
	cd rpi-image-gen && ./rpi-image-gen build -S ../bicycleimage/ -c bicycledata.yaml
