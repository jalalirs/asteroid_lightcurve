# asteroid_lightcurve

## I.About:
#### Asteroid Curve is a tool that enables scientists to study and create an asteroid light curve by rendering the 3D model, manipulating object's position, light source, simulation and observing settings. 
#### This project is a submission for the [2021 NASA Space Apps Challenge](https://www.spaceappschallenge.org/about/). 
#### More information on [our team's project](https://www.youtube.com/watch?v=3P302Ph8n6g).


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

### 4- launch the tool:
Finally:
```
$ python AsteroidCurve.py
```



## III.Simulation:
### This tool provides two ways to simulate the asteroid 3D object:
### I. X,Y,Z Positioning
### II. Orbital Positioning

#### In X, Y, Z only positioning, the user is able to control where the light source, observer and asteroid can be, changing variables affecting the light curve appearance.
![20210930181557_Trim (1)-min](https://user-images.githubusercontent.com/83130573/135499736-1eb66f1c-464a-4231-bdb8-7fba0dc305fc.gif)

#### In Orbital positioning, the user can choose the trajectory of the orbiting 3D model from a given list, which will affect how the observer from earth will see the asteroid. Controlling other settings are also available to study the light curve affected by a wide range of variables.
![20210930174008_Trim-min](https://user-images.githubusercontent.com/83130573/135499921-12c35a1f-2778-49fd-a559-3a4dc323195c.gif)


### To create a light curve:
#### 1- Choose the positioning way you want from the bar 
#### 2- Load the 3D model from `load model` choose from the provided models in `Gallery`. ***note: the tool accepts .obj format only.***
#### 3- Change variables of observing, light, object, simulation settings from tabs.
#### 4- Click `play` and see your asteroid rotating and creating beautiful light curves!

![ezgif com-gif-maker (1)](https://user-images.githubusercontent.com/83130573/135501739-f0ba9732-206b-4553-ad82-1a9317e0f3ce.gif)


