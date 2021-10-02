# asteroid_lightcurve

![ezgif com-gif-maker (3)](https://user-images.githubusercontent.com/83130573/135700079-26e068c9-79c0-4adf-a8b9-4bad44d7e836.gif)

## I.About:
#### Asteroid Curve is a tool that enables scientists and users to study and create an asteroid light curve by rendering the 3D model, manipulating object's position, light source, simulation and observing settings. 
#### This project is a submission for the [2021 NASA Space Apps Challenge](https://www.spaceappschallenge.org/about/). 
#### More information on [our team's project](https://2021.spaceappschallenge.org/challenges/statements/when-light-curves-throw-us-curve-balls/teams/glowing-darkness/project), [how to use the interface](https://www.youtube.com/watch?v=LkDYK82yCeo).


## II.Usage:
#### Prerequisite:
>[python3](https://www.python.org/downloads/)


>[pip](https://pypi.org/project/pip/)


>[git](https://git-scm.com/downloads)


#### Dependencies:
***See [requirements.txt](https://github.com/jalalirs/asteroid_lightcurve/blob/main/requirements.txt)***


### To install the tool in your device:
##### 1- Clone the repository
##### 2- Create and activate virtual environment
##### 3- Install dependencies
##### 4- Run AsteroidCurve.py

### 1- Clone this repository:
First make sure you should have [git](https://git-scm.com/downloads) installed.

on terminal or cmd:
Create or select path where Asteroid Curve repository will be installed:
```
$ mkdir AsteroidCurve
```
on Linux:
```
$ cd ~/AsteroidCurve
```
on MacO or Windows:
```
$ cd AsteroidCurve
```
clone the repository:
```
$ git clone https://github.com/jalalirs/asteroid_lightcurve.git
```

### 2- Create a virtual environment:

Linux:
```
$ mkdir ~/virtualenvs
$ virtualenv nameOfEnv
$ source nameOfEnv/bin/activate
$ cd ~\<PathOfInstalledRepository>
$ cd \asteroid_lightcurve-main
```
MacOs:
```
$ mkdir virtualenvs
$ virtualenv nameOfEnv
$ source nameOfEnv/bin/activate
cd \<PathOfInstalledRepository>
cd \asteroid_lightcurve-main
```
on Windows:
```
$ mkdir virtualenvs
$ cd \virtualenvs
$ python3 -m venv <Virtual Environment Name>
$ .\<Virtual Environment Folder Name>\Scripts\activate
$ cd \<PathToVirtualEnv>
$ .\venv\Scripts\activate.bat
$ cd \<PathOfInstalledRepository>
$ cd \asteroid_lightcurve-main
```

### 3- Install all dependencies:
Using the `requirements.txt` file this command will install all Python libraries that the project depends on.
```
$ pip install -r requirements.txt
```
#### ***Note: If you want to use the Inertial Stability feature, clone this two repositories [1] Mesh Reader:(https://github.com/p-hofmann/MeshReader.git),[2] Voxlib: (https://github.com/p-hofmann/PyVoxelizer.git) into your environment.***

### 4- launch the tool:
Finally:
```
$ python AsteroidCurve.py
```

### 



## III.Simulation menu:

### A. 3D model Gallery
### B. Retriveing observed data
### C. Orbital Positioning
### D. X,Y,Z Positioning 


## A. Load 3D model Gallery
The asteroid 3D models provided by NASA are listed by default in this section along with simple objects to start with.
Another option is loading existing 3D models in the user's device.
***note: the tool accepts .obj format only.***

![Screen Shot 2021-10-01 at 6 01 22 PM](https://user-images.githubusercontent.com/83130573/135697219-53678fca-24bb-4470-a5f4-e92e8efca82d.png)

### B. Retriveing observed light curve data 
This feature enables the user to get all light curves observed and published in [Asteroid Light Curve Photomerty Database](https://alcdef.org/) by searching asteroid designations (ID) and choosing plots. This will allow the user to match the observed light curve with the simulated light curve in the next secion.

![data retriveal](https://user-images.githubusercontent.com/83130573/135698494-dac0c802-abf7-4247-a29b-dedb343a8ad3.gif)


## C,D. This tool provides two ways to simulate the asteroid 3D object:

#### In X, Y, Z (custom setup) simulation, the user is able to control where the light source, observer and asteroid can be, changing variables affecting the light curve appearance.
![20210930181557_Trim (1)-min](https://user-images.githubusercontent.com/83130573/135499736-1eb66f1c-464a-4231-bdb8-7fba0dc305fc.gif)

#### In Orbital (solar system) simulatioin, the user can choose the trajectory of the orbiting 3D model from a given list, which will affect how the observer from earth will see the asteroid. Controlling other settings are also available to study the light curve affected by a wide range of variables.
![20210930174008_Trim-min](https://user-images.githubusercontent.com/83130573/135499921-12c35a1f-2778-49fd-a559-3a4dc323195c.gif)

### After graphing the light curve, the tool allows the user to match the resulted curve with the observed light curve (retrived in light curve data section) by normlizing and shifting the graph.

## To create a light curve:
#### 1- Choose the positioning way you want from the bar 
#### 2- Load the 3D model from `load model` choose from the provided models in `Gallery` import models from PC. ***note: the tool accepts .obj format only.***
#### 3- Change variables of observing, light, object, simulation settings from tabs.
#### 4- Click `play` and see your asteroid rotating and creating beautiful light curves!

![ezgif com-gif-maker (1)](https://user-images.githubusercontent.com/83130573/135501739-f0ba9732-206b-4553-ad82-1a9317e0f3ce.gif)


## To Do:
#### 1- Automate observed data light curve fitting to get best match with simulated light curve.
#### 2- Synthesize astroid shapes and rondomize noise to test every possible effects on light curve.
