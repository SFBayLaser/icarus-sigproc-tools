# numpy is the source of all life in python
import numpy as np
import uproot

# An object for handling RawDigits from art root files

class FieldResponse:
    """
    FieldResponse: An object designed to hold the information (input as a root TH1F histogram) which describes the field
    response for a given plane in the ICARUS TPC

    Note that historically the field responses have been calculated in 50 ns bins over a 50 us time range (1000 bins). So this
    sets the initial initialization for both the field response and the electronics response... resampling will be performed at
    a higher level (calcualting the overall respponse functions)
    """
    def __init__(self,responsesFolder,responseFile,normalization=-1.):
        """
        args: responsesFolder is the fully qualified path to the directory containing the response files
              responseFile is tthe name of the file to input
        """
        self.responsesFolder = responsesFolder
        self.responseFile    = responseFile

        print("FieldResponse opening input file:",responsesFolder+responseFile)
        self.hist_file = uproot.open(responsesFolder+responseFile)

        key = str(self.hist_file.keys()[0])

        print("FieldResponse key:",key)

        # This is outdated?
        #self.folderName    = key[key.index('\'')+1:str(key).index(';')]
        self.folderName    = key
        th1fhistogram      = self.hist_file[self.folderName].to_numpy()

        self.timeBins      = th1fhistogram[1]
        self.responseVals  = th1fhistogram[0]
        self.binSize       = self.timeBins[1] - self.timeBins[0]

        # What kind of response are we? This will be contained in the file name
        self.responseType = int(responseFile[responseFile.index('vw0')+3])

        # Find the time offset which is response dependent
        if self.responseType < 2:
            # In this case we first find the minimum
            minBin = np.argmin(self.responseVals)
            # and then we search backwards from there to find the zero crossover which is the last bin that is positive
            t0Bin  = minBin - np.argmax(self.responseVals[minBin::-1] > 0.) + 1
        else:
            maxResponse = np.amax(self.responseVals)
            t0Bin       = np.argmax(self.responseVals)
   
        self.t0Offset = self.timeBins[t0Bin] - self.timeBins[0]

        # Get the normalization factor
        self.normFactor  = np.sum(self.responseVals)        

        if normalization <= 0.:
            self.responseVals /= self.normFactor
        else:
            self.responseVals /= normalization

        # Finally, compute the FFT 
        self.transform = np.fft.rfft(self.responseVals)

        print("Field Response for plane type:",self.responseType,", T0 offset:",self.t0Offset,", normalization:",self.normFactor)

 
