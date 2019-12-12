# numpy is the source of all life in python
import numpy as np
import uproot

# An object defining a filter function for use in signal deconvolution
class Filter:
    """
    Filter: an object serving as a base class for defining a specific filter
    """
    def __init__(self,numTimeBins,samplingRate):
        """
        args: numTimeBins is the number of time bins to use when creating the response function
              samplingRate is the width of each bin (assumed in usec)
        """
        self.numTimeBins  = numTimeBins
        self.samplingRate = samplingRate

        # local constants
        maxFrequency = 1000. / (2.*samplingRate)           # max sampling frequency in MHz
        frequencyRes = maxFrequency / float(numTimeBins/2) # frequency resolution in MHz

        # Make a vector containing the times for the response to be calculated
        self.frequencyBins = np.arange(0.,maxFrequency+frequencyRes,frequencyRes)

        self.filter = np.zeros(len(self.frequencyBins))

class FilterGauss(Filter):
    """
    Filter: an object to define a filter for use in the ICARUS deconvolution
    """
    def __init__(self,numTimeBins,samplingRate,params):
        """
        args: numTimeBins is the number of time bins to use when creating the response function
              binWidth is the width of each bin (assumed in usec)
              params is a list of pairs describing the gaussians used by the filter
        """

        # intialize the base class first
        Filter.__init__(self,numTimeBins,samplingRate)

        self.params    = params
        self.filter    = (np.exp(-0.5*((self.frequencyBins-self.params[0])/self.params[1])**2)).astype(complex)
        self.filter[0] = complex(0.,0.)  # set the constant component to zero 

        # normalize to the peak value
        largestElement = np.amax(self.filter)

        self.filter /= largestElement

class FilterDoubleGauss(Filter):
    """
    Filter: an object to define a filter for use in the ICARUS deconvolution
    """
    def __init__(self,numTimeBins,samplingRate,params):
        """
        args: numTimeBins is the number of time bins to use when creating the response function
              binWidth is the width of each bin (assumed in usec)
              params is a list of pairs describing the gaussians used by the filter
        """

        # intialize the base class first
        Filter.__init__(self,numTimeBins,samplingRate)

        self.params = params

        gauss1  = np.exp(-0.5*((self.frequencyBins-self.params[1][0])/self.params[1][1])**2)
        gauss2  = np.ones(len(self.frequencyBins)) - np.exp(-0.5*((self.frequencyBins-self.params[0][0])/self.params[0][1])**2)

        # By construction the zero bin will be zero
        self.filter = (gauss1 * gauss2).astype(complex)

        # normalize to the peak value
        largestElement = np.amax(self.filter)

        self.filter /= largestElement


class FilterPseudoWiener(Filter):
    """
    Filter: an object to define a filter for use in the ICARUS deconvolution
    """
    def __init__(self,numTimeBins,samplingRate,params):
        """
        args: numTimeBins is the number of time bins to use when creating the response function
              binWidth is the width of each bin (assumed in usec)
              params is a list of pairs describing the gaussians used by the filter
        """

        # intialize the base class first
        Filter.__init__(self,numTimeBins,samplingRate)

        self.params = params

        wiener  = np.exp(-0.5*pow((self.frequencyBins-self.params[0])/self.params[1],self.params[2]))

        # By construction the zero bin will be zero
        self.filter = wiener.astype(complex)
        self.filter[0] = complex(0.,0.)

        # normalize to the peak value
        largestElement = np.amax(self.filter)

        self.filter /= largestElement


class FilterGaussPseudoWiener(Filter):
    """
    Filter: an object to define a filter for use in the ICARUS deconvolution
    """
    def __init__(self,numTimeBins,samplingRate,params):
        """
        args: numTimeBins is the number of time bins to use when creating the response function
              binWidth is the width of each bin (assumed in usec)
              params is a list of pairs describing the gaussians used by the filter
        """

        # intialize the base class first
        Filter.__init__(self,numTimeBins,samplingRate)

        self.params = params

        gauss   = np.ones(len(self.frequencyBins)) - np.exp(-0.5*((self.frequencyBins-self.params[0][0])/self.params[0][1])**2)
        wiener  = np.exp(-0.5*pow((self.frequencyBins-self.params[1][0])/self.params[1][1],self.params[1][2]))

        # By construction the zero bin will be zero
        self.filter = (gauss*wiener).astype(complex)

        # normalize to the peak value
        largestElement = np.amax(self.filter)

        self.filter /= largestElement
