import numpy as np
import ROOT
from sproc import sproc

class Denoiser:
    '''
    Python class to interface C++ backend denoising modules conveniently. 

    USAGE:

        denoiser = Denoiser(fullEvent)
        # Find ROI and remove coherent noise
        denoiser.removeCoherentNoise2D('d', (7, 20), window=10, threshold=7.5)
    '''
    def __init__(self, fullEvent, **kwargs):

        self.fullEvent = fullEvent
        self.filter_1d = ROOT.sigproc_tools.Morph1D()
        self.filter_2d = ROOT.sigproc_tools.Morph2D()
        self.denoiser = ROOT.sigproc_tools.Denoising()
        self.numChannels = kwargs.get('numChannels', 576)
        self.numTicks = kwargs.get('numTicks', 4096)

    def removeCoherentNoise2D(self, filter_name='d',
                            structuringElement=(7,20),
                            window=10,
                            threshold=7.5):
        '''
        Coherent Noise Removal with 2D Morphological Filters
        '''
        selectVals =  ROOT.std.vector('std::vector<bool>')(
            self.numChannels, ROOT.std.vector('bool')(self.numTicks))
        roi = ROOT.std.vector('std::vector<bool>')(
            self.numChannels, ROOT.std.vector('bool')(self.numTicks))
        filteredWaveforms =  sproc.pyutil.as_float32_vector_2d(self.fullEvent.astype(np.float32))
        intrinsicRMS =  ROOT.std.vector('std::vector<float>')(
            self.numChannels, ROOT.std.vector('float')(self.numTicks))
        correctedMedians =  ROOT.std.vector('std::vector<float>')(
            self.numChannels, ROOT.std.vector('float')(self.numTicks))
        waveLessCoherent =  ROOT.std.vector('std::vector<float>')(
            self.numChannels, ROOT.std.vector('float')(self.numTicks))
        morphedWaveforms =  ROOT.std.vector('std::vector<float>')(
            self.numChannels, ROOT.std.vector('float')(self.numTicks))

        # Run 2D ROI finding and denoising.
        self.denoiser.removeCoherentNoise2D(
            waveLessCoherent, filteredWaveforms, morphedWaveforms, 
            intrinsicRMS, selectVals, roi, correctedMedians, 
            filter_name, 64, structuringElement[0], structuringElement[1], 
            window, threshold)
        
        # Coherent Noise Removed 2D Waveform
        self.waveLessCoherent = np.asarray(waveLessCoherent)
        self.correctedMedians = np.asarray(correctedMedians)
        # Morphological Filtered Waveform
        self.morphedWaveforms = np.asarray(morphedWaveforms)
        # ROI (Region of Interest)
        self.roi = sproc.pyutil.as_ndarray(roi).astype(bool).astype(int)
        # Region to protect signal from coherent noise removal. Note that
        # in general self.roi != self.selectVals, since it may be desirable to
        # be conservative with the ROIs. 
        self.selectVals = sproc.pyutil.as_ndarray(selectVals).astype(bool).astype(int)
        # Intrinsic RMS after coherent noise removal.
        self.intrinsicRMS = np.asarray(intrinsicRMS)


    def refine_rois(self):
        '''
        Use opening/closing operations to eliminate fragmented false rois.
        '''
        pass


    def median_denoising(self):
        '''
        Apply median filter for secondary denoising after CNC. 
        '''
        pass
