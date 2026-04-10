# bicycleimage

This project creates a master (golden) Raspberry Pi image for initializing bicycle data collector units running [bicycleinit](https://github.com/bicycledata/bicycleinit). The resulting image is ready to flash onto devices and provides a consistent starting point for bicycle data collection units.

The image is generated using [rpi-image-gen](https://github.com/raspberrypi/rpi-image-gen).

## Features

The generated image includes:

- Wi-Fi setup
- Bluetooth setup
- Hostname configuration
- Timezone setup
- Default username and password
- Installation of all required packages for `bicycleinit`
- System service setup to automatically launch `bicycleinit` on boot
- UART0 preconfigured

## Build Instructions

It is recommended to use the Raspberry Pi target hardware to build the image. Clone this repository, including its submodules, and follow the steps below to create the image.

### Initial setup

The first time you run the build, rpi-image-gen needs to install its dependencies:
```bash
make config
```

### Build the image

Once the setup is complete, build the image by running:
```bash
make build
```
