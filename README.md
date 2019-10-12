<!-- It seems that github simply ignores the "style" tags within div tags... so try something different -->
<p align=center>
<a href="http://icarus.lngs.infn.it"><img src="http://icarus.lngs.infn.it/img/n3.jpg" alt="ICARUS Experiment" style="border:0"></a>
</p>

<h1 align=center><font color="blue"><font size="7">ICARUS Signal Processing</font></font></h1><br>
<p align=center>
<font color="gray"><font size="3">A repository aimed at collecting tools and notebooks useful for studying waveforms/ROI/hit finding <br>with the ICARUS LAr TPC</font></font><br>
</p>


<h2><font color="blue"><font size="5">General Directory Structure</font></font></h2>
<ul>
    <li><b>sigproc_tools</b> - This folder is broken into two parts:</li>
        <ul>
            <li><b>sigproc_functions</b> - A collection of python modules defining functions useful for stuying noise and developing filtering techniques </li>
            <li><b>sigproc_objects</b> - A collection of python classes for accessing the data to be analyzed</li>
        </ul>
    <li><b>plotting</b> - A collection of useful function definitions for making specific types of plots</li>
    <li><b>notebooks</b> - A collection of example Jupyter notebooks for performing specific analyes</li>
</ul>

<h2><font color="blue"><font size="5">Prerequisites for running</font></font></h2>
<ul>
    <li>The interface are python modules which are designed to be run in jupyter notebooks. Example jupyter notebooks are provided, to be able to execute them you will need:</li>
    <ul>
        <li>The modules are designed to run in python 3.6 or above (tested in 3.7)</li>
        <li>One will need access to the standard python include packages numpy, scipy and matplotlib</li>
        <li>Access to the input root data files is with the <a href="https://uproot.readthedocs.io/en/latest/">uproot package</a> where you can find instructions on installaion (e.g. through pip or conda)</li>
        <li>Graphics output is performed with the <a href="https://plotly/python/">plot-ly</a> package which provides for a nice interactive user experience (though, warning, can be memory intensive)</li>
        <li>Also useful for the 3D event views is the <a href="https://ipywidgets.readthedocs.io/en/latest/">ipywidgets</a> package those this is not required for the basic analysis</li>
        <li>Finally, you will need to be able to run a <a href="https://jupyter-notebook.readthedocs.io/en/stable/">jupyter notebook</a>
    </ul>
    <li>The main idea is to have this installation running on your laptop (e.g. the above works nicely on a macbook pro) with input data files copied to your local machine. However, provided the above libraries are available, no reason to not run the cro-magnon form (i.e. over network to an icarus gpvm machine)</li>
</ul>

<h2><font color="blue"><font size="5">Installing</font></font></h2>
<ul>
    <li>Create a working area on your machine where you will copy the input files and set up this repository</li>
    <li>Navigate to that folder
    <li>git clone https://github.com/SFBayLaser/icarus-sigproc-tools </li>
    <li>Copy one of the example notebooks fromt the repository folder to your working folder (it is not recommended to open them directly since this will create a cache folder and, more important, when you execute the notebook it will create arrays and images which are quite large - it would not be good to upload those back to the root repository!)</li>
    <li>Open the notebook and in the first code block that is highlighted with "TODO" be sure to replace the path you see there with the full path to folder which contains the signal processing tools repository</li>
    <li>In the second "TODO" block set the fully qualified path to the location of your data files and the name of the file you want to read</li>
    <li>Run the notebook!</li>
</ul>





# Project Title

One Paragraph of project description goes here

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

What things you need to install the software and how to install them

```
Give examples
```

### Installing

A step by step series of examples that tell you how to get a development env running

Say what the step will be

```
Give the example
```

And repeat

```
until finished
```

End with an example of getting some data out of the system or using it for a little demo

## Running the tests

Explain how to run the automated tests for this system

### Break down into end to end tests

Explain what these tests test and why

```
Give an example
```

### And coding style tests

Explain what these tests test and why

```
Give an example
```

## Deployment

Add additional notes about how to deploy this on a live system

## Built With

* [Dropwizard](http://www.dropwizard.io/1.0.2/docs/) - The web framework used
* [Maven](https://maven.apache.org/) - Dependency Management
* [ROME](https://rometools.github.io/rome/) - Used to generate RSS Feeds

## Contributing

Please read [CONTRIBUTING.md](https://gist.github.com/PurpleBooth/b24679402957c63ec426) for details on our code of conduct, and the process for submitting pull requests to us.

## Versioning

We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/your/project/tags). 

## Authors

* **Billie Thompson** - *Initial work* - [PurpleBooth](https://github.com/PurpleBooth)

See also the list of [contributors](https://github.com/your/project/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* Hat tip to anyone whose code was used
* Inspiration
* etc


