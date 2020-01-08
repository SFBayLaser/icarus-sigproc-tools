# numpy is the source of all life in python
import numpy as np
from sigproc_tools.sigproc_functions.noiseProcessing import *
from sigproc_tools.sigproc_objects.rawdigit import RawDigit

# An object which will perform basic noise filtering on an input data set of RawDigits

class FilterEvents:
    """
    The goal here is to provide access to a series of objects that represent RawDigit waveforms 
    after several noise filter steps have been performed including coherent noise subtraction
    """
    def __init__(self,eventsFolder,producer):
        """
        args: eventsFolder is the folder containing the desired RawDigits by event
              producer is the path to the RawDigits for uproot to decode when looking them up
        """
        self.rawdigits = RawDigit(eventsFolder,producer)

    # Given direct access to the RawDigits to recover its functionality 
    def getRawDigits(self):
        return self.rawdigits

    # Run the basic event loop
    def filterEvents(self,grouping):
        """
        Here we perform the noise filtering over all of the RawDigits available in the input file
        args: grouping - the number of channels to group together for coherent noise subtraction
        """

        eventNum  = 10
        numEvents = self.rawdigits.numEvents()
        nTicks    = self.rawdigits.numTicks(eventNum)
        nChannels = self.rawdigits.numChannels(eventNum)
        nGroups   = nChannels // grouping
        
        print("Number of channels:",nChannels,", grouping:",grouping,", nGroups:",nGroups)
        
        # Set up to loop over events
        # Define placeholders for the output arrays
        self.rawWaveforms        = np.ndarray([numEvents,nChannels,nTicks])
        self.waveLessPedAll      = np.ndarray([numEvents,nChannels,nTicks])
        self.pedestalsAll        = np.ndarray([numEvents,nChannels])
        self.rmsAll              = np.ndarray([numEvents,nChannels])
        self.waveLessCoherentAll = np.ndarray([numEvents,nChannels,nTicks])
        self.medianAll           = np.ndarray([numEvents,nGroups,nTicks])
        self.intrinsicRMSAll     = np.ndarray([numEvents,nGroups,nTicks])
        
        locWaveforms        = np.ndarray((nChannels,nTicks))
        
        print("Applying filtering to ",numEvents,"events")
        
        for eventNo in range(numEvents):
            self.rawWaveforms[eventNo]         = self.rawdigits.getWaveforms(eventNo)
            self.waveLessPedAll[eventNo],      \
            self.pedestalsAll[eventNo],        \
            self.rmsAll[eventNo]               = getPedestalsAndRMS(self.rawWaveforms[eventNo,:,:])
            self.waveLessCoherentAll[eventNo], \
            self.medianAll[eventNo],           \
            self.intrinsicRMSAll[eventNo]      = removeCoherentNoise(self.waveLessPedAll[eventNo],grouping,nTicks)
            
            if eventNo%10 == 0:
                print("--> Done with event ",eventNo)
        
        print("Done")

        return numEvents



