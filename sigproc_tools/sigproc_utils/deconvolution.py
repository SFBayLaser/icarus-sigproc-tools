import numpy as np
import ROOT
from sproc import sproc

import scipy.signal as sig


class Deconvolver:
    '''
    Class for interfacing deconvolution C++ backend modules.
    '''
    def __init__(self, waveLessCoherent, response_fn=None, selectVals=None):
        self.waveLessCoherent = waveLessCoherent
        self.numChannels = waveLessCoherent.shape[0]
        self.nTicks = waveLessCoherent.shape[1]
        if response_fn is not None:
            self.response_fn = response_fn
        if selectVals is None:
            selectVals = ROOT.std.vector('std::vector<bool>')(
                self.numChannels, ROOT.std.vector('bool')(self.numTicks))
        self.deconvolver = ROOT.sigproc_tools.AdaptiveWiener()
        utils = ROOT.sigproc_tools.MiscUtils()
        wLC_float2d = sproc.pyutil.as_float32_vector_2d(
            self.waveLessCoherent)
        self.selectVals = sproc.pyutil.as_bool_vector_2d(selectVals)
        self.noise_var = utils.compute_noise_power(
            wLC_float2d, self.selectVals)

    def deconvolve_1d(self):
        raise NotImplementedError

    def deconvolve_2d(self, name='lee', structuringElement=(7,7),
                      noise_var=None, **kwargs):
        '''
        Run 2D Deconvolution algorithms for denoising.

        Note that adaptive local wiener filters are not strictly speaking
        deconvolution algorithms (since they do not involve FFT/IFFT), but
        a local approximation to the Wiener filter which is MMSE optimal.

        INPUTS:
            - name: name of the algorithm to be used. Default is Lee Filter.

            Supported Algorithms:
                - lee: adaptive wiener filter developed by Lee et. al. See:
                    https://ieeexplore.ieee.org/document/4766994
                - lee_median: lee filter except using median instead of mean.
                - kuan: lee filter with adaptive weighting, see:
                    https://ieeexplore.ieee.org/document/4767641

        '''
        if noise_var is None:
            noise_var = self.noise_var
        sx = structuringElement[0]
        sy = structuringElement[1]
        a = kwargs.get('a', 1.0)
        epsilon = kwargs.get('epsilon', 2.5)
        deconvolvedWaveform = ROOT.std.vector('std::vector<float>')(
            self.numChannels, ROOT.std.vector('float')(self.nTicks))
        waveLessCoherent = sproc.pyutil.as_float32_vector_2d(
            self.waveLessCoherent)
        if name == 'lee':
            self.deconvolver.filterLee(
                deconvolvedWaveform, waveLessCoherent, noise_var, sx, sy)
        elif name == 'MMWF':
            self.deconvolver.MMWF(
                deconvolvedWaveform, waveLessCoherent, noise_var, sx, sy)
        elif name == 'lee_enhanced':
            self.deconvolver.filterLeeEnhanced(
                deconvolvedWaveform, waveLessCoherent,
                noise_var, sx, sy, a, epsilon)
        elif name == 'MMWFStar':
            self.deconvolver.MMWFStar(
                deconvolvedWaveform, waveLessCoherent, sx, sy)
        elif name == 'lee_enhanced_roi':
            self.deconvolver.adaptiveROIWiener(
                deconvolvedWaveform, waveLessCoherent, self.selectVals,
                noise_var, sx, sy, a, epsilon)
        else:
            raise ValueError('Provided Denoising algorithm name not available.')
        self.result = np.asarray(deconvolvedWaveform)
        return self.result

    @staticmethod
    def compute_charge(roi, waveform, electronicsGain=67.4):
        return np.sum(waveform[roi]) * electronicsGain
