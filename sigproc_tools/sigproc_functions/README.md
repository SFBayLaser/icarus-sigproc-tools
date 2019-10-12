
<h1><font color="blue"><font size="7">sigproc_functions</font></font></h1>
<p align=center>
<font color="gray"><font size="3">A Collection of Python Modules Declaring Basic Functions for Filtering and Analysis of Noise on ICARUS Waveforms</font></font><br>
</p>
<ul>
    <li><b>noiseProcessing.py</b></li>
        <ul>
            <li> <b>getPedestalAndRMS</b> - this calculates the mean(median) value of ADC values per channel to determine the pedestal, subtracts this value from the waveforms and then calculates the RMS of the channel </li>
            <li> <b>getCoherentNoiseCorrection</b> - this takes as input the pedestal corrected waveforms on a per unit basis - meaning in the grouping corresponding to the coherent noise - and then calculates the median value for each tick, then subtracts those values from each waveform. Finally, it computes the RMS of the ADC values for each tick in the set of input waveforms</li>
            <li> <b>removeCoherentNoise</b> - this takes as input a collection of pedestal correction wavefroms, and the grouping of consecutive channels to use, and computes the median for each tick in each grouping, then subtracts this from each of the input waveforms</li>
        </ul>
    <li><b>noiseAnalysis.py</b></li>
        <ul>
            <li> <b>computeCorrelations</b> - this takes an input a set of waveforms, in the form [numEvents,nGroups,nTicks], the number of events and the group size (consecutive channels) and computes the correlations between groups. Two methods are used: Pearson R test and cross correlation</li>
            <li><b>getPowerVec</b> - this takes as input a collection of waveforms and computes the resulting power spectrum for each individual waveform</li>
        </ul>
    <li><b>responseFunctions.py</b></li>
        <ul>
            <li><b>electronicsReponse</b> - this returns the electronics response, in particular in the form of the bessel filtered response described in the <a href="https://iopscience.iop.org/article/10.1088/1748-0221/13/12/P12007/pdf">electronics paper</a>. There is also useful information in <a href="http://sbn-docdb.fnal.gov/cgi-bin/RetrieveFile?docid=3197&filename=WarmADC18072017.pdf">this docdb article</a> (provided you have access to the SBN/ICARUS docdb area).</li>
        </ul>
    <li><b>fakeParticle.py</b></li>
        <ul>
            <li><b>genWhiteNoiseWaveform</b> - this will generate a set of "white noise" waveforms. It starts by generating a waveform of purely random ADC values and then convolves this waveform with the electronics response (see above)</li>
            <li><b>gaussParticle</b></li> - simply defines a guassian function to emulate the charge deposit on wires
            <li><b>createGaussianParticle</b></li> - this will generate a "particle trajectory" (simply a straight line) give the tick offset and track angle to the wires. The envelope of the trajectory will be a sliced gaussian (sliced along the wire direction)
            <li><b>createGaussDerivativeParticle</b></li> - this is meant to emulate a bipolar signal on wires by simply differentiating the gaussian function declared above. 
        </ul>
    <li><p>Plus more to be added as we move forward</p></li>
</ul>


