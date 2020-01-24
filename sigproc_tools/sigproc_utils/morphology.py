import numpy as np
import ROOT
from sproc import sproc

#######################################################################
#
#   1D and 2D Morphological Filtering Modules with C++ backend.
#   
#   2019. 12. 16    Dae Heun Koh
#
#######################################################################

# 1D Filters

def dilation_1d(input, se=10):
    '''
    INPUTS:
        - input (np.float32 array): input 2D array to compute dilation.
        - se (int tuple): structuring element; determines the size of
        moving window. 

    RETURNS:
        - dilation1D (np.array): 1D dilation filter applied output. 
    '''
    morph1d = ROOT.sigproc_tools.Morph1D()
    inputTemp = input.astype(np.float32)
    numChannels, numTicks = input.shape
    inputTemp = sproc.pyutil.as_float32_vector_2d(inputTemp)
    dilation1D = ROOT.std.vector('std::vector<float>')(
        numChannels, ROOT.std.vector('float')(numTicks))
    morph1d.getDilation(inputTemp, se, dilation1D)
    dilation1D = np.asarray(dilation1D)
    return dilation1D

def erosion_1d(input, se=10):
    '''
    INPUTS:
        - input (np.float32 array): input 2D array to compute dilation.
        - se (int tuple): structuring element; determines the size of
        moving window. 

    RETURNS:
        - dilation2D (np.array): 1D dilation filter applied output. 
    '''
    morph1d = ROOT.sigproc_tools.Morph1D()
    inputTemp = input.astype(np.float32)
    numChannels, numTicks = input.shape
    inputTemp = sproc.pyutil.as_float32_vector_2d(inputTemp)
    erosion1D = ROOT.std.vector('std::vector<float>')(
        numChannels, ROOT.std.vector('float')(numTicks))
    morph1d.getErosion(inputTemp, se, erosion1D)
    erosion1D = np.asarray(erosion1D)
    return erosion1D

def gradient_1d(input, se=10):
    '''
    INPUTS:
        - input (np.float32 array): input 2D array to compute dilation.
        - se (int tuple): structuring element; determines the size of
        moving window. 

    RETURNS:
        - dilation2D (np.array): 1D dilation filter applied output. 
    '''
    morph1d = ROOT.sigproc_tools.Morph1D()
    inputTemp = input.astype(np.float32)
    numChannels, numTicks = input.shape
    inputTemp = sproc.pyutil.as_float32_vector_2d(inputTemp)
    gradient1D = ROOT.std.vector('std::vector<float>')(
        numChannels, ROOT.std.vector('float')(numTicks))
    morph1d.getGradient(inputTemp, se, gradient1D)
    gradient1D = np.asarray(gradient1D)
    return gradient1D

# 2D Filters

def dilation_2d(input, se=(7, 20)):
    '''
    INPUTS:
        - input (np.float32 array): input 2D array to compute dilation.
        - se (int tuple): structuring element; determines the size of
        moving window. 

    RETURNS:
        - dilation2D (np.array): 2D dilation filter applied output. 
    '''
    morph2d = ROOT.sigproc_tools.Morph2D()
    inputTemp = input.astype(np.float32)
    numChannels, numTicks = input.shape
    inputTemp = sproc.pyutil.as_float32_vector_2d(inputTemp)
    dilation2D = ROOT.std.vector('std::vector<float>')(
        numChannels, ROOT.std.vector('float')(numTicks))
    morph2d.getDilation(inputTemp, se[0], se[1], dilation2D)
    dilation2D = np.asarray(dilation2D)
    return dilation2D

def erosion_2d(input, se=(7, 20)):
    '''
    INPUTS:
        - input (np.float32 array): input 2D array to compute dilation.
        - se (int tuple): structuring element; determines the size of
        moving window. 

    RETURNS:
        - dilation2D (np.array): 2D dilation filter applied output. 
    '''
    morph2d = ROOT.sigproc_tools.Morph2D()
    inputTemp = input.astype(np.float32)
    numChannels, numTicks = input.shape
    inputTemp = sproc.pyutil.as_float32_vector_2d(inputTemp)
    erosion2D = ROOT.std.vector('std::vector<float>')(
        numChannels, ROOT.std.vector('float')(numTicks))
    morph2d.getErosion(inputTemp, se[0], se[1], erosion2D)
    erosion2D = np.asarray(erosion2D)
    return erosion2D

def gradient_2d(input, se=(7, 20)):
    '''
    INPUTS:
        - input (np.float32 array): input 2D array to compute dilation.
        - se (int tuple): structuring element; determines the size of
        moving window. 

    RETURNS:
        - dilation2D (np.array): 2D dilation filter applied output. 
    '''
    morph2d = ROOT.sigproc_tools.Morph2D()
    inputTemp = input.astype(np.float32)
    numChannels, numTicks = input.shape
    inputTemp = sproc.pyutil.as_float32_vector_2d(inputTemp)
    gradient2D = ROOT.std.vector('std::vector<float>')(
        numChannels, ROOT.std.vector('float')(numTicks))
    morph2d.getGradient(inputTemp, se[0], se[1], gradient2D)
    gradient2D = np.asarray(gradient2D)
    return gradient2D

def median_2d(input, se=(7, 20)):
    '''
    INPUTS:
        - input (np.float32 array): input 2D array to compute dilation.
        - se (int tuple): structuring element; determines the size of
        moving window. 

    RETURNS:
        - dilation2D (np.array): 2D dilation filter applied output. 
    '''
    morph2d = ROOT.sigproc_tools.Morph2D()
    inputTemp = input.astype(np.float32)
    numChannels, numTicks = input.shape
    inputTemp = sproc.pyutil.as_float32_vector_2d(inputTemp)
    median2D = ROOT.std.vector('std::vector<float>')(
        numChannels, ROOT.std.vector('float')(numTicks))
    morph2d.getMedian(inputTemp, se[0], se[1], median2D)
    median2D = np.asarray(median2D)
    return median2D