# numpy is the source of all life in python
import numpy as np

# An object for handling RawDigits from art root files

class RawDigit:
    """
    RawDigit: Emulates RawDigits as read into python via "uproot". Generally this means that we are given the 
    "events" folder in the input root file which contains the RawDigits per event. We can then access each by 
    event number 
    """
    def __init__(self,eventsFolder,producer):
        """
        args: eventsFolder is the folder containing the desired RawDigits by event
              producer is the path to the RawDigits for uproot to decode when looking them up
        """
        self.eventsFolder = eventsFolder
        self.producer     = producer
        self.obj          = eventsFolder.array(self.producer+"obj",flatten=True)
        
    def numEvents(self):
        numEvents = len(self.obj)
        return numEvents
        
    def numChannels(self,eventNum):
        nChannels = self.obj[eventNum]
        return nChannels
    
    def numTicks(self,eventNum,channelNum=0):
        samples = self.eventsFolder.array(self.producer+"obj.fSamples",entrystart=eventNum,entrystop=eventNum+1,flatten=True)
        return samples[channelNum]
    
    def getWaveforms(self,eventNum):
        """
        Plan: Provided the RawDigits exists for a given event (e.g. in Multi-TPC readout an event may have no RawDigits),
              we can look up the information to pull out the waveform from the data block. Interestingly, each waveform 
              will begin with a count (4096) and end with a guard (0) - except there is no count for the first and no guard
              for the last. So the below contortions are done to allow resizing and dropping of this extraneous info
        """
        # First check to see if this event has an entry (can happen in multiTPC readout)
        if self.numChannels(eventNum) > 0:
            nTicks    = self.numTicks(eventNum)
            nChannels = self.numChannels(eventNum)
            waveforms = self.eventsFolder.array(self.producer+"obj.fADC",entrystart=eventNum,entrystop=eventNum+1,flatten=True)
            waveforms = np.concatenate([waveforms,[0,nTicks]])  # This adds the pattern "0, 4096" to the end of the 1D array
            waveforms = waveforms.reshape(nChannels,nTicks+2)   # Now we make a 2D array of 384 channels by 4096+2 ticks
            return waveforms[:,:-2]
        else:
            return numpy.zeros(shape=(1,1))
        
    def getChannels(self,eventNum):
        channels = self.eventsFolder.array(self.producer+"obj.fChannel",entrystart=eventNum,entrystop=eventNum+1,flatten=True)
        return channels

