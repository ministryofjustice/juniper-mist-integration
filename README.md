# Juniper mist integration script

This repo has been developed by the DevOps Lan&Wi-Fi to automate site creation on juniper mist.

## Run script

## Development setup

### Prerequisites
* Docker
* IDE that integrates with docker (We use IntelliJ in this example)

### Setup
* Run `make build-dev`
* Integrate built docker container with IDE. [here](https://www.jetbrains.com/help/idea/configuring-remote-python-sdks.html#2546d02c) is the example for intelliJ
* mark src directory & test directory within the IDE. [here](https://www.jetbrains.com/help/idea/content-roots.html)

# Notes
* To see options run `make help` 
* If you update [requirements.txt](src/requirements.txt), you will need to rebuild the docker container.
