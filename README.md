# Lase
#### `Python API for the Koheron Lase board`

## Requirements

* Python 2.7
* PyQtGraph
* PyQt or PySide 
* Scipy
* NumPy

## Run demo

```sh
python interface.py
```

![Demo](https://cloud.githubusercontent.com/assets/1735094/9765362/317e8212-5714-11e5-8480-ab3e311260c9.gif)

## Lase API : basic simulation example

```python
from lase.drivers import OscilloSimu
import numpy as np
import matplotlib.pyplot as plt

driver = OscilloSimu()

# Set laser current to 30 mA
current = 30 mA
driver.set_laser_current(current)
print 'Laser power = ', driver.get_laser_power(), 'a.u.'

# Enable laser
driver.start_laser()
print 'Laser power = ', driver.get_laser_power(), 'a.u.'

# Modulate the laser current
n = driver.sampling.n # Number of points in the waveform
fs = driver.sampling.fs # Sampling frequency (Hz)
mod_amp = 0.4 # Modulation amplitude in V
freq = 10
print 'Modulation frequency = ', freq * fs / n, 'Hz'
driver.dac[1,:] = mod_amp * np.cos(2*np.pi* freq/n*np.arange(n))
driver.set_dac()

# Retrieve the modulation signal from the photodiode on ADC 1
driver.get_adc()
signal = driver.adc[0,:]

# Plot the result
plt.plot(driver.sampling.t, signal)

#
driver.stop_laser()
driver.close()

```

## Control the Koheron Lase board

### Installation

Get [latest release](https://github.com/Koheron/Lase/releases) of SD card image `lase.img`.

## Copyright

Copyright 2015 Koheron SAS. The code is released under [the MIT licence](https://github.com/Koheron/Lase/blob/master/LICENSE).

