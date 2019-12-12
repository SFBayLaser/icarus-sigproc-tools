# numpy is the source of all life in python
import numpy as np
import uproot
import scipy.signal as signal

from sigproc_tools.sigproc_objects.fieldresponse import FieldResponse
from sigproc_tools.sigproc_objects.electronicsresponse import ElectronicsResponse


# An object containing the full response for a given plane in ICARUS

class FullResponse:
    """
    FullResponse: An object designed to hold the information describing the full TPC response for ICARUS - meaning converting from
    a charge deposition in # electrons to a waveform shape in ADC counts/ticks. This will be a combinaiton of the field response, 
    describing the charge deposition on a wire from a charge deposition in the TPC (typicall a delta function) and then the 
    response due to the TPC electronics. 
    """
    def __init__(self,responsesFolder,responseFile,filter,normalization=-1.):
        """
        args: responsesFolder is the fully qualified path to the directory containing the response files
              responseFile is tthe name of the file to input
              normalizaation is the normalization to apply to the field response. Note that the electronics 
              response will be normalized to 1, the field responses should be normalized to the collection plane
        """
        self.FieldResponse       = FieldResponse(responsesFolder,responseFile,normalization)
        self.ElectronicsResponse = ElectronicsResponse(len(self.FieldResponse.timeBins),self.FieldResponse.binSize)

        # Build the "full" response from the two above
        # Begin with the convolution of the transforms
        fullResponse = np.fft.irfft(np.multiply(self.FieldResponse.transform,self.ElectronicsResponse.transform))
        
        # Now we need to resample to convert from the time binning of the Field Response to that of the TPC readout
        # The conversions are:
        # 1) the ratio of bin width in the TPC readout (0.4us) to the field response
        # 2) the number of bins in resmapled output will be the number of bins in the field response divided by the above ratio
        self.TPCTickWidth = 0.4
        self.TPCNumTicks  = 4096
     
        binTimeRatio      = self.TPCTickWidth / self.FieldResponse.binSize
        binRatio          = int(len(self.FieldResponse.timeBins) / binTimeRatio)
        self.Response     = signal.resample(fullResponse,binRatio) * binTimeRatio  #This converts to ticks and preserves area (I claim)

        print("binTimeRatio:",binTimeRatio,", binRatio:",binRatio,", len:",len(self.Response))

        # the resampled response now needs to be padded with zeros to make full length
        self.Response = np.append(self.Response,np.zeros(self.TPCNumTicks-len(self.Response)))

        # Get the FFT of the full response
        self.ResponseFFT = np.fft.rfft(self.Response)

        # It will be handly to keep a resampled electronics response too
        self.ElecResponse = signal.resample(self.ElectronicsResponse.electronicsResponse,binRatio) * binTimeRatio
        self.ElecResponse = np.append(self.ElecResponse,np.zeros(self.TPCNumTicks-len(self.ElecResponse)))

        self.ElecResponseFFT = np.fft.rfft(self.ElecResponse)

        # Get the full response T0 offset (returned in us)
        self.T0Offset = self.FieldResponse.t0Offset + self.ElectronicsResponse.t0Offset

        # TODO add in the deconvolution (like here)
        self.Filter           = filter
        self.DeconvolutionFFT = np.divide(self.Filter.filter,self.ResponseFFT,out=np.zeros_like(self.Filter.filter),where=np.absolute(self.ResponseFFT)!=0.)


 
