# icarus-sigproc-tools
A collection of python tools for studying/analyzing signal processing for ICARUS

<div style="text-align:center;border-style: solid;border-width: 1px;">
    <h2><font color="blue"><font size="5">Define a Collection of Basic Functions for Analysis Waveforms</font></font></h2><br>
</div>
<ul>
    <li><p>Useful functions here</p></li>
        <ul>
            <li> <b>getPedestalAndRMS</b> - this calculates the mean(median) value of ADC values per channel to determine the pedestal, subtracts this value from the waveforms and then calculates the RMS of the channel </li>
            <li> <b>getCoherentNoiseCorrection</b> - this takes as input the pedestal corrected waveforms on a per unit basis - meaning in the grouping corresponding to the coherent noise - and then calculates the median value for each tick, then subtracts those values from each waveform. Finally, it computes the RMS of the ADC values for each tick in the set of input waveforms</li>
            <li> <b>removeCoherentNoise</b> - this takes as input a collection of pedestal correction wavefroms, and the grouping of consecutive channels to use, and computes the median for each tick in each grouping, then subtracts this from each of the input waveforms</li>
            <li> <b>computeCorrelations</b> - this takes an input a set of waveforms, in the form [numEvents,nGroups,nTicks], the number of events and the group size (consecutive channels) and computes the correlations between groups. Two methods are used: Pearson R test and cross correlation</li>
            <li><b>getPowerVec</b> - this takes as input a collection of waveforms and computes the resulting power spectrum for each individual waveform</li>
            <li><b>electronicsReponse</b> - this returns the electronics response, in particular in the form of the bessel filtered response described in the <a href="https://iopscience.iop.org/article/10.1088/1748-0221/13/12/P12007/pdf">electronics paper</a>. There is also useful information in <a href="http://sbn-docdb.fnal.gov/cgi-bin/RetrieveFile?docid=3197&filename=WarmADC18072017.pdf">this docdb article</a> (provided you have access to the SBN/ICARUS docdb area).</li>
            <li><b>genWhiteNoiseWaveform</b> - this will generate a set of "white noise" waveforms. It starts by generating a waveform of purely random ADC values and then convolves this waveform with the electronics response (see above)</li>
        </ul>
    <li><p>With these functions we can also take a first look at noise mitigation</p></li>
</ul>


