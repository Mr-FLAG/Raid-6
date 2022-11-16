# CE7490 Project RAID6

CE7490 2022 Fall - Advanced Topics in Distributed System - Project 2: RAID-6 based distributed storage system

## Introduction
[RAID](https://en.wikipedia.org/wiki/RAID) (Redundant Array of Independent Disks) is developed for the demand of rising the reliability, capacity and speed of storage systems. The level of RAID6 is an extension of RAID5 by adding another parity block, which is designed to tolerate any two concurrent disk failure and maintain a relatively high storage efficiency. An example of RAID6 storage with double parity is shown below:

<p align="center">
    <img src='data/RAID4-6.drawio.png' width="400" height="250">
</p>

## Installation Guide
The RAID-6 system is devloped in Python 3.9 environment with dependencies math, numpy, os and time library.

The project is supported on Linux and Windows using terminal / command line.


## Running Experiments

The standard way to run the test from terminal / command line is:

```
python test.py 
```

The original file is stored in ```./data/file```. We have provided three kinds of file (.txt, .pdf, .jpg) for recovering test. Feel free to add your preferred file type and define your RAID6 configuration at ```./src/config.py ```.

## Reference
An excellent tutorial of implementing RAID6 using Reed-Solomon coding can be found at http://www.cs.utk.edu/~plank/plank/papers/CS-96-332.html
