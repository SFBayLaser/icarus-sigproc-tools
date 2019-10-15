# the source of life
import numpy as np

def electronicsReponse(tick,tickWidth):
    shapingTime = 1.3
    #arg = tick * tickWidth / shapingTime
    #return arg * np.exp(-arg)
    timeOffset  = 1.625
    binTime     = tick * tickWidth - timeOffset
    binTime     = np.where(binTime>0.,binTime,0.) / shapingTime
    leftArg     = 0.5 * np.multiply(0.9*binTime,0.9*binTime)
    rightArg    = 0.5 * np.multiply(0.5*binTime,0.5*binTime)
    rawResponse = np.multiply(1. - np.exp(-leftArg),np.exp(-rightArg))
    normFactor  = np.sum(rawResponse,axis=-1)
    if normFactor.ndim > 0:
        normFactor = normFactor.reshape((normFactor.shape)+(1,))
    return rawResponse / normFactor
    
