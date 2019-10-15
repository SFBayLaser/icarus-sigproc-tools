# numpy is the source of all life in python
import numpy as np
import uproot

# An object for handling RawDigits from art root files

class ElectronicsResponse:
    """
    ElectronicsResponse: an object to describe the electronics response. We assume the ad hoc formulation to describe
    the Bessel Filter response function for ICARUS
    """
    def __init__(self,numTimeBins,binWidth):
        """
        args: numTimeBins is the number of time bins to use when creating the response function
              binWidth is the width of each bin (assumed in usec)
        """
        # Start with the parameters describing the response
        self.shapingTime = 1.3
        self.timeOffset  = 1.625

        # Make a vector containing the times for the response to be calculated
        responseBins = np.arange(numTimeBins)
        self.timeBins = responseBins * binWidth

        # Zero the bins which have negative values (because of the offset)
        elecTime = self.timeBins - self.timeOffset
        elecTime = np.where(elecTime>0.,elecTime,np.zeros(numTimeBins)) / self.shapingTime

        # Set the arguments to the response function
        leftArg     = 0.5 * np.multiply(0.9*elecTime,0.9*elecTime)
        rightArg    = 0.5 * np.multiply(0.5*elecTime,0.5*elecTime)

        # Calculate the "raw" response
        self.electronicsResponse = np.multiply(1. - np.exp(-leftArg),np.exp(-rightArg))

        # Determine the t0 offset for the electronics response (taken as the peak position)
        self.t0Offset = self.timeBins[np.argmax(self.electronicsResponse)] - self.timeBins[0]

        normFactor  = np.sum(self.electronicsResponse)

        # Now get the normalized response
        self.electronicsResponse /= normFactor

        # Finally, compute the FFT 
        self.transform = np.fft.rfft(self.electronicsResponse)

 
