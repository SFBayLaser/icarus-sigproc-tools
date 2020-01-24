# numpy is the source of all life in python
import numpy as np
from sigproc_tools.sigproc_functions.noiseProcessing import *
from sigproc_tools.sigproc_objects.rawdigit import RawDigit

# An object which will perform basic noise filtering on an input data set of RawDigits

class FilterEventsByCrate:
    """
    The goal here is to provide access to a series of objects that represent RawDigit waveforms 
    after several noise filter steps have been performed including coherent noise subtraction
    """
    def __init__(self,eventsFolder,producer,crateNum):
        """
        args: eventsFolder is the folder containing the desired RawDigits by event
              producer is the path to the RawDigits for uproot to decode when looking them up
        """
        self.rawdigits = RawDigit(eventsFolder,producer)
        self.crateNum  = crateNum

        # Get starting and ending indices
        self.numChannelsPerCrate = 576
        self.startIndex          = self.numChannelsPerCrate * crateNum
        self.stopIndex           = self.startIndex + self.numChannelsPerCrate

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
        nChannels = self.numChannelsPerCrate
        nGroups   = nChannels // grouping
        
        print("Number of channels:",nChannels,", grouping:",grouping,", nGroups:",nGroups,", start/stop:",self.startIndex,"/",self.stopIndex)

        if self.startIndex > self.rawdigits.numChannels(eventNum):
            print("--> Bad index, start:",self.startIndex,", numChannels:",self.rawdigits.numChannels(eventNum))
            return 0        

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
            fullRawDigits                      = self.rawdigits.getWaveforms(eventNo)
            self.rawWaveforms[eventNo]         = fullRawDigits[self.startIndex:self.stopIndex,:]
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



