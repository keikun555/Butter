butter
======
Python implementation of the digital butterworth IIR filter

Dependencies
============
- **numpy** -- used for its math modules and fast array calculations
- **numba** -- used to increase calculation speed

Basic Usage
===========
Importing the Butter module::

  from butterworth import Butter

Creating the Butter instance for a lowpass butterworth filter with cutoff frequency 1000Hz and rolloff frequency 48Hz for data taken with sampling frequency 44100::

  filter_ = Butter(btype="Lowpass", cutoff=1000, rolloff=48, sampling=44100)

Sending sample data into filter and retrieving the filtered data::

  ```python
  data=[1.0, -2.0, 3.0, . . . .]
  filtered_data = filter_.send(data)
  ```

Retrieving forward-backward filtered data for the accumulated data::

  ```python
  data1=[1.0, -2.0, 3.0, . . . .]
  filtered_data = filter_.send(data1)
  data2=[-1.0, 2.0, -3.0, . . . .]
  more_filtered_data = filter_.send(data2)
  forward_backwards_filtered_data = filter_.filtfilt()
  ```
