# C.H.I.P.-NeoPixel-SPI-Control-Visualiser
Neopixel controller for C.H.I.P. board. Light, Peak Volume or Visualisation of Audio source. 

[![ChipNeoPixels](http://img.youtube.com/vi/m9ATuX6nQkU/0.jpg)](http://www.youtube.com/watch?v=m9ATuX6nQkU "Click to watch ChipNeoPixels Video ")

CHIP connects to audio source via TRRS socket and is configured as a mic-in.
CHIP runs python flask to serve webpage at http://<Ip.Add.re.ss>:5000 offering 


### Prerequisites
* Uses Chip's TRRS as mic-in so audio input to Alsa. 
* NeoPixel Strip connected to CHIP pin 29, CSIHSYNC  (see config.py) 
* Assumes CHIP is configuted to connect to wifi via say nmtui
* Needs Python and associated libraries(see scripts), python flask installed on CHIP.
* Needs SPI configured on CHIP - http://www.chip-community.org/index.php/SPI_support 
* Once Configured, test with daniperron's test script - https://bbs.nextthing.co/t/neopixel-stick-works-well-with-the-spi/15934 
* I found a small in-line amp to increase/decrease volume level helped processing.


http://www.youtube.com/watch?v=m9ATuX6nQkU 

##  Modes 
### 1. Main Screen
![My image](https://github.com/sanc909/C.H.I.P.-NeoPixel-SPI-Control-Visualiser/blob/master/img/Capture0001.PNG) 
### 2. Mood - choose Colour and number of Leds
![My image](https://github.com/sanc909/C.H.I.P.-NeoPixel-SPI-Control-Visualiser/blob/master/img/Capture0002.PNG)
### 3. Meter - choose number of Leds
![My image](https://github.com/sanc909/C.H.I.P.-NeoPixel-SPI-Control-Visualiser/blob/master/img/Capture0003.PNG)
### 4. Music -  choose Visualisation: Energy, Scroll or Spectrum 
![My image](https://github.com/sanc909/C.H.I.P.-NeoPixel-SPI-Control-Visualiser/blob/master/img/Capture0005.PNG)

Or turn off Leds




## Authors

* **San Cabraal** - *Initial work* - [sanc909](https://github.com/sanc909)

See also the list of [contributors](https://github.com/your/project/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

*  Scott Lawson's  Audio Reactive Led Strip https://github.com/scottlawsonbc/audio-reactive-led-strip 
*  SPI configured on CHIP                   http://www.chip-community.org/index.php/SPI_support 
*  daniperron's SPI+NeoPixel test script -  https://bbs.nextthing.co/t/neopixel-stick-works-well-with-the-spi/15934 

