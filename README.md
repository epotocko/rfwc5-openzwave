# rfwc5-openzwave

Proof of concept programming the RFWC5 scene controller using python-openzwave. 
The program.py script will program each of the 5 buttons to trigger a scene activation command with a corresponding id (i.e. button 1 triggers scene id 1). The activation command will only be handled by the controller. Intended usage is with software such as Home Assistant that just needs to receive the scene activation commands and will handle the automation from there.

## Usage
This program uses the sendRawData function that is not currently included in python-openzwave master, so python-openzwave/openzwave needs to be built from a branch (https://github.com/tkintscher/python-openzwave.git).  I used docker to build python-openzwave and run the code to program the device.
Update the constants for `DEVICE`, `HOME_ID`, `CONTROLLER_NODE_ID`, and `SCENE_CONTROLLER_NODE_ID` at the top of program.py.
```bash
docker build -t tmp .
docker run -i \
  -v $(pwd)/config/zwcfg_0x12345678.xml:/test/zwcfg_0x12345678.xml \
  -v $(pwd)/config/pyozw.sqlite:/test/pyozw.sqlite \
  -v $(pwd)/config/options.xml:/test/options.xml \
  -v $(pwd)/program.py:/test/program.py \
  --device /dev/ttyUSB0:/dev/ttyUSB0 \
  -t tmp
 --
```
Once the device has been programmed, the code is no longer needed.

## Related Work
https://github.com/saains/SmartThingsPublic/blob/master/devicetypes/saains/cooper-aspire-scene-controller-rfwc5-rfwc5d.src/cooper-aspire-scene-controller-rfwc5-rfwc5d.groovy
https://community.openhab.org/t/tutorial-cooper-rfwc5-scene-controller-with-openhab2/31731

## Future
If the sendRawData [pull request](https://github.com/OpenZWave/python-openzwave/pull/158) is merged into a future version of python-openzwave, this script could be run in any environment with python-openzwave installed via pip. Also, a custom Home Assistant component could potentially be built if the sendRawData function was available.
