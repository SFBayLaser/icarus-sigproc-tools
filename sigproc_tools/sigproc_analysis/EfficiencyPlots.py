import numpy as np

import plotly.graph_objects as go
import plotly.subplots as subplots
from   plotly.colors import DEFAULT_PLOTLY_COLORS

# Define a gaussian function
# x are the input coordinates
# PeakAmp is the amplitude of the gaussian
# PeakTime is the center of the gaussian
# sigma is the sigma of the gaussian
# baseline is the default baseline of the waveform
def gaus(x,peakAmp,peakTime,sigma,baseline):
       return peakAmp*np.exp(-0.5*(x-peakTime)**2/(sigma**2))+baseline


# Some plotting functions
# figure is the ploty multi plot figure to add the plots too
# dataMap is map containing the data 
# linestyle is the style for the plots
# dash is line solid or dash
def plotEfficiencies(figure, dataMap,lineStyle="hvh",dash="solid"):
    for planeIdx in range(3):
        validTrackArray = np.array(dataMap["validTracks"][planeIdx])
        
        #selectGoodTracks = np.logical_and(validTrackArray>0,np.array(dataMap["rawDigitPHs"][planeIdx])>5.)
        selectGoodTracks = np.logical_and(validTrackArray>0,np.array(dataMap["rawDigitPHs"][planeIdx])>0.)
        
        allROIArray     = np.array(dataMap["allROIs"][planeIdx])[selectGoodTracks]
        dataROIArray    = np.array(dataMap["dataROIs"][planeIdx])[selectGoodTracks]
        maxValArray     = np.array(dataMap["simMaxVals"][planeIdx])[selectGoodTracks]
        rawPHArray      = np.array(dataMap["rawDigitPHs"][planeIdx])[selectGoodTracks]
        dataHitArray    = np.array(dataMap["dataHits"][planeIdx])[selectGoodTracks]
        
        totVsAmpHist, xEdges = np.histogram(rawPHArray,bins=100, range=(0.,100.),weights=allROIArray)
        datVsAmpHist, xEdges = np.histogram(rawPHArray,bins=100, range=(0.,100.),weights=dataROIArray)
        
        hitVsAmpHist, xEdges = np.histogram(rawPHArray,bins=100, range=(0.,100.),weights=dataHitArray)
        
        effVsAmpROIHist = np.divide(datVsAmpHist,totVsAmpHist, out=np.zeros_like(datVsAmpHist), where=totVsAmpHist!=0)
        effVsAmpHitHist = np.divide(hitVsAmpHist,totVsAmpHist, out=np.zeros_like(hitVsAmpHist), where=totVsAmpHist!=0)
        
        xEdges = 0.5 * (xEdges[:-1] + xEdges[1:])
        figure.add_trace(go.Scatter(x=xEdges,y=effVsAmpROIHist,name=str('ROI Efficiency: %d' % (planeIdx)),line_shape=lineStyle,line=dict(color=DEFAULT_PLOTLY_COLORS[planeIdx],dash=dash,width=2)),row=1,col=planeIdx+1)
        figure.add_trace(go.Scatter(x=xEdges,y=effVsAmpHitHist,name=str('Hit Efficiency: %d' % (planeIdx)),line_shape=lineStyle,line=dict(color=DEFAULT_PLOTLY_COLORS[planeIdx+3],dash=dash,width=2)),row=1,col=planeIdx+1)
            
        figure.update_xaxes(title={"text":"RawDigit Pulse Height","standoff":10},row=1,col=planeIdx+1)
        figure.update_yaxes(title_text="Efficiency",row=1,col=planeIdx+1)

        # Angular efficiencies
        trkCosX = np.array(dataMap["trkCosXVals"][planeIdx])
        
        selectPH   = rawPHArray > 8.
        
        trkCos     = trkCosX[selectGoodTracks]
        
        totVsAngHist, xEdges = np.histogram(trkCos,bins=40, range=(-1.1,1.1),weights=allROIArray)
        datVsAngHist, xEdges = np.histogram(trkCos,bins=40, range=(-1.1,1.1),weights=dataROIArray)
        hitVsAngHist, xEdges = np.histogram(trkCos,bins=40, range=(-1.1,1.1),weights=dataHitArray)
        
        roiEffVsAngHist = np.divide(datVsAngHist,totVsAngHist, out=np.zeros_like(datVsAngHist), where=totVsAngHist!=0)
        hitEffVsAngHist = np.divide(hitVsAngHist,totVsAngHist, out=np.zeros_like(hitVsAngHist), where=totVsAngHist!=0)
        
        xEdges = 0.5 * (xEdges[:-1] + xEdges[1:])
        figure.add_trace(go.Scatter(x=xEdges,y=roiEffVsAngHist,name=str('ROI Eff vs Trk Cos plane: %d' % (planeIdx)),line_shape=lineStyle,line=dict(color=DEFAULT_PLOTLY_COLORS[planeIdx],dash=dash,width=2)),row=2,col=planeIdx+1)
        figure.add_trace(go.Scatter(x=xEdges,y=hitEffVsAngHist,name=str('Hit Eff vs Trk Cos plane: %d' % (planeIdx)),line_shape=lineStyle,line=dict(color=DEFAULT_PLOTLY_COLORS[planeIdx+3],dash=dash,width=2)),row=2,col=planeIdx+1)
            
        figure.update_xaxes(title={"text":"Track Cos(x)","standoff":10},row=2,col=planeIdx+1)
        figure.update_yaxes(title_text="Efficiency",row=2,col=planeIdx+1)
        
    
def plotChargeResolution(figure, dataMap,lineStyle="hvh",dash="solid"):
    for planeIdx in range(3):
        validTrackArray = np.array(dataMap["validTracks"][planeIdx])
        
        #selectGoodTracks = np.logical_and(validTrackArray>0,np.array(dataMap["rawDigitPHs"][planeIdx])>5.)
        selectGoodTracks = np.logical_and(validTrackArray>0,np.array(dataMap["rawDigitPHs"][planeIdx])>0.)
        
        simChargeArray   = np.array(dataMap["simChargeVals"][planeIdx])[selectGoodTracks] / 80.1
        hitChargeArray   = np.array(dataMap["hitCharges"][planeIdx])[selectGoodTracks]
        hitIntegralArray = np.array(dataMap["hitIntegrals"][planeIdx])[selectGoodTracks]
        rawPHArray       = np.array(dataMap["rawDigitPHs"][planeIdx])[selectGoodTracks]
        
        simVsAmpHist, xEdges = np.histogram(rawPHArray,bins=100, range=(0.,100.),weights=simChargeArray)
        hitVsAmpHist, xEdges = np.histogram(rawPHArray,bins=100, range=(0.,100.),weights=hitChargeArray)
        intVsAmpHist, xEdges = np.histogram(rawPHArray,bins=100, range=(0.,100.),weights=hitIntegralArray)
        
        chgRatVsAmpHist = np.divide(hitVsAmpHist,simVsAmpHist, out=np.zeros_like(hitVsAmpHist), where=simVsAmpHist>0)
        intRatVsAmpHist = np.divide(intVsAmpHist,simVsAmpHist, out=np.zeros_like(intVsAmpHist), where=simVsAmpHist>0)
        
        xEdges = 0.5 * (xEdges[:-1] + xEdges[1:])
        figure.add_trace(go.Scatter(x=xEdges,y=chgRatVsAmpHist,name=str('SummedADC/Sim: %d' % (planeIdx)),line_shape=lineStyle,line=dict(color=DEFAULT_PLOTLY_COLORS[planeIdx],dash=dash,width=2)),row=1,col=planeIdx+1)
        figure.add_trace(go.Scatter(x=xEdges,y=intRatVsAmpHist,name=str('Integral/Sim: %d' % (planeIdx)),line_shape=lineStyle,line=dict(color=DEFAULT_PLOTLY_COLORS[planeIdx+3],dash=dash,width=2)),row=1,col=planeIdx+1)
            
        figure.update_xaxes(title={"text":"SimChannel Pulse Height","standoff":10},row=1,col=planeIdx+1)

        # Angular efficiencies
        trkCosX = np.array(dataMap["trkCosXVals"][planeIdx])
        
        trkCos     = trkCosX[selectGoodTracks]
        
        simVsAngHist, xEdges = np.histogram(trkCos,bins=40, range=(-1.1,1.1),weights=simChargeArray)
        chgVsAngHist, xEdges = np.histogram(trkCos,bins=40, range=(-1.1,1.1),weights=hitChargeArray)
        intVsAngHist, xEdges = np.histogram(trkCos,bins=40, range=(-1.1,1.1),weights=hitIntegralArray)
        
        chgRatVsAngHist = np.divide(chgVsAngHist,simVsAngHist, out=np.zeros_like(chgVsAngHist), where=simVsAngHist>0)
        intRatVsAngHist = np.divide(intVsAngHist,simVsAngHist, out=np.zeros_like(intVsAngHist), where=simVsAngHist>0)
        
        xEdges = 0.5 * (xEdges[:-1] + xEdges[1:])
        figure.add_trace(go.Scatter(x=xEdges,y=chgRatVsAngHist,name=str('SummedADC/Sim vs Trk Cos plane: %d' % (planeIdx)),line_shape=lineStyle,line=dict(color=DEFAULT_PLOTLY_COLORS[planeIdx],dash=dash,width=2)),row=2,col=planeIdx+1)
        figure.add_trace(go.Scatter(x=xEdges,y=intRatVsAngHist,name=str('Integral/Sim vs Trk Cos plane: %d' % (planeIdx)),line_shape=lineStyle,line=dict(color=DEFAULT_PLOTLY_COLORS[planeIdx+3],dash=dash,width=2)),row=2,col=planeIdx+1)
            
        figure.update_xaxes(title={"text":"Track Cos(x)","standoff":10},row=2,col=planeIdx+1)
        
    
def plotEfficHeat(figure,dataMap,lineStyle="hvh",dash="solid"):
    for planeIdx in range(3):
        validTrackArray = np.array(dataMap["validTracks"][planeIdx])
        
        #selectGoodTracks = np.logical_and(validTrackArray>0,np.array(dataMap["rawDigitPHs"][planeIdx])>5.)
        selectGoodTracks = validTrackArray>0
        
        allROIArray     = np.array(dataMap["allROIs"][planeIdx])[selectGoodTracks]
        dataROIArray    = np.array(dataMap["dataROIs"][planeIdx])[selectGoodTracks]
        rawPHArray      = np.array(dataMap["rawDigitPHs"][planeIdx])[selectGoodTracks]
        dataHitArray    = np.array(dataMap["dataHits"][planeIdx])[selectGoodTracks]
        trkCosX         = np.array(dataMap["trkCosXVals"][planeIdx])[selectGoodTracks]
        
        allEffic2d, xEdges, yEdges = np.histogram2d(rawPHArray,trkCosX,bins=[40,40],range=[[0.,40.],[-1.1,1.1]],weights=allROIArray)
        datEffic2d, xEdges, yEdges = np.histogram2d(rawPHArray,trkCosX,bins=[40,40],range=[[0.,40.],[-1.1,1.1]],weights=dataROIArray)

        effic2d = np.divide(datEffic2d,allEffic2d, out=np.ones_like(datEffic2d), where=allEffic2d!=0)
        
        xEdges = 0.5 * (xEdges[:-1] + xEdges[1:])
        yEdges = 0.5 * (yEdges[:-1] + yEdges[1:])
        
        #figure.add_trace(go.Heatmap(x=xEdges,y=yEdges,z=effic2d, colorscale="Greys"),row=planeIdx+1,col=1)
        figure.add_trace(go.Contour(x=xEdges,y=yEdges,z=np.transpose(effic2d)),row=planeIdx+1,col=1)

        figure.update_xaxes(title={"text":"RawDigit Pulse Height","standoff":10},row=planeIdx+1,col=1)
        figure.update_yaxes(title_text="Track Cos(x)",row=planeIdx+1,col=1)
        
        hitEffic2d, xEdges, yEdges = np.histogram2d(rawPHArray,trkCosX,bins=[40,40],range=[[0.,40.],[-1.1,1.1]],weights=dataHitArray)

        effic2d = np.divide(hitEffic2d,allEffic2d, out=np.ones_like(hitEffic2d), where=allEffic2d!=0)
        
        xEdges = 0.5 * (xEdges[:-1] + xEdges[1:])
        yEdges = 0.5 * (yEdges[:-1] + yEdges[1:])
        
        #figure.add_trace(go.Heatmap(x=xEdges,y=yEdges,z=effic2d, colorscale="Greys"),row=planeIdx+1,col=1)
        figure.add_trace(go.Contour(x=xEdges,y=yEdges,z=np.transpose(effic2d)),row=planeIdx+1,col=2)

        figure.update_xaxes(title={"text":"RawDigit Pulse Height","standoff":10},row=planeIdx+1,col=2)
        figure.update_yaxes(title_text="Track Cos(x)",row=planeIdx+1,col=2)

def plotEfficHeatByPlane(figure,dataMap,lineStyle="hvh",dash="solid",planeIdx=0):
    validTrackArray = np.array(dataMap["validTracks"][planeIdx])
    
    #selectGoodTracks = np.logical_and(validTrackArray>0,np.array(dataMap["rawDigitPHs"][planeIdx])>5.)
    selectGoodTracks = validTrackArray>0
    
    allROIArray     = np.array(dataMap["allROIs"][planeIdx])[selectGoodTracks]
    dataROIArray    = np.array(dataMap["dataROIs"][planeIdx])[selectGoodTracks]
    maxValArray     = np.array(dataMap["maxVals"][planeIdx])[selectGoodTracks]
    rawPHArray      = np.array(dataMap["rawDigitPHs"][planeIdx])[selectGoodTracks]
    dataHitArray    = np.array(dataMap["dataHits"][planeIdx])[selectGoodTracks]
    trkCosX         = np.array(dataMap["trkCosXVals"][planeIdx])[selectGoodTracks]
    
    allEffic2d, xEdges, yEdges = np.histogram2d(rawPHArray,trkCosX,bins=[40,40],range=[[0.,40.],[-1.1,1.1]],weights=allROIArray)
    datEffic2d, xEdges, yEdges = np.histogram2d(rawPHArray,trkCosX,bins=[40,40],range=[[0.,40.],[-1.1,1.1]],weights=dataROIArray)

    effic2d = np.divide(datEffic2d,allEffic2d, out=np.ones_like(datEffic2d), where=allEffic2d!=0)
    
    xEdges = 0.5 * (xEdges[:-1] + xEdges[1:])
    yEdges = 0.5 * (yEdges[:-1] + yEdges[1:])
    
    #figure.add_trace(go.Heatmap(x=xEdges,y=yEdges,z=effic2d, colorscale="Greys"),row=planeIdx+1,col=1)
    figure.add_trace(go.Contour(x=xEdges,y=yEdges,z=np.transpose(effic2d)),row=1,col=1)

    figure.update_xaxes(title={"text":"Estimated Pulse Height","standoff":10},row=1,col=1)
    figure.update_yaxes(title_text="Track Cos(x)",row=1,col=1)
    
    hitEffic2d, xEdges, yEdges = np.histogram2d(rawPHArray,trkCosX,bins=[40,40],range=[[0.,40.],[-1.1,1.1]],weights=dataHitArray)

    effic2d = np.divide(hitEffic2d,allEffic2d, out=np.ones_like(hitEffic2d), where=allEffic2d!=0)
    
    xEdges = 0.5 * (xEdges[:-1] + xEdges[1:])
    yEdges = 0.5 * (yEdges[:-1] + yEdges[1:])
    
    #figure.add_trace(go.Heatmap(x=xEdges,y=yEdges,z=effic2d, colorscale="Greys"),row=planeIdx+1,col=1)
    figure.add_trace(go.Contour(x=xEdges,y=yEdges,z=np.transpose(effic2d)),row=1,col=2)

    figure.update_xaxes(title={"text":"Estimated Pulse Height","standoff":10},row=1,col=2)
    figure.update_yaxes(title_text="Track Cos(x)",row=1,col=2)
    
def plotEfficByPlane(figure,dataMap,lineStyle="hvh",dash="solid",planeIdx=0):
    validTrackArray = np.array(dataMap["validTracks"][planeIdx])
    
    #selectGoodTracks = np.logical_and(validTrackArray>0,np.array(dataMap["rawDigitPHs"][planeIdx])>5.)
    selectGoodTracks = validTrackArray>0
    
    allROIArray     = np.array(dataMap["allROIs"][planeIdx])[selectGoodTracks]
    dataROIArray    = np.array(dataMap["dataROIs"][planeIdx])[selectGoodTracks]
    maxValArray     = np.array(dataMap["maxVals"][planeIdx])[selectGoodTracks]
    rawPHArray      = np.array(dataMap["rawDigitPHs"][planeIdx])[selectGoodTracks]
    dataHitArray    = np.array(dataMap["dataHits"][planeIdx])[selectGoodTracks]
    trkCosX         = np.array(dataMap["trkCosXVals"][planeIdx])[selectGoodTracks]

    totVsAmpHist, xEdges = np.histogram(rawPHArray,bins=100, range=(0.,100.),weights=allROIArray)
    datVsAmpHist, xEdges = np.histogram(rawPHArray,bins=100, range=(0.,100.),weights=dataROIArray)
    
    hitVsAmpHist, xEdges = np.histogram(rawPHArray,bins=100, range=(0.,100.),weights=dataHitArray)
    
    effVsAmpROIHist = np.divide(datVsAmpHist,totVsAmpHist, out=np.zeros_like(datVsAmpHist), where=totVsAmpHist!=0)
    effVsAmpHitHist = np.divide(hitVsAmpHist,totVsAmpHist, out=np.zeros_like(hitVsAmpHist), where=totVsAmpHist!=0)
    
    xEdges = 0.5 * (xEdges[:-1] + xEdges[1:])
    figure.add_trace(go.Scatter(x=xEdges,y=effVsAmpROIHist,name=str('ROI Eff vs Pulse Height: %d' % (planeIdx)),line_shape=lineStyle,line=dict(color=DEFAULT_PLOTLY_COLORS[planeIdx],dash=dash,width=2)),row=1,col=1)
    figure.add_trace(go.Scatter(x=xEdges,y=effVsAmpHitHist,name=str('Hit Eff vs Pulse Height: %d' % (planeIdx)),line_shape=lineStyle,line=dict(color=DEFAULT_PLOTLY_COLORS[planeIdx+3],dash=dash,width=2)),row=1,col=1)
        
    figure.update_xaxes(title={"text":"Estimated Pulse Height","standoff":10},row=1,col=1)
    figure.update_yaxes(title_text="Efficiency",row=1,col=1)

    # Angular efficiencies
    trkCosX = np.array(dataMap["trkCosXVals"][planeIdx])
    
    selectPH   = rawPHArray > 8.
    
    trkCos     = trkCosX[selectGoodTracks]
    
    totVsAngHist, xEdges = np.histogram(trkCos,bins=40, range=(-1.1,1.1),weights=allROIArray)
    datVsAngHist, xEdges = np.histogram(trkCos,bins=40, range=(-1.1,1.1),weights=dataROIArray)
    hitVsAngHist, xEdges = np.histogram(trkCos,bins=40, range=(-1.1,1.1),weights=dataHitArray)
    
    roiEffVsAngHist = np.divide(datVsAngHist,totVsAngHist, out=np.zeros_like(datVsAngHist), where=totVsAngHist!=0)
    hitEffVsAngHist = np.divide(hitVsAngHist,totVsAngHist, out=np.zeros_like(hitVsAngHist), where=totVsAngHist!=0)
    
    xEdges = 0.5 * (xEdges[:-1] + xEdges[1:])
    figure.add_trace(go.Scatter(x=xEdges,y=roiEffVsAngHist,name=str('ROI Eff vs Trk Cos plane: %d' % (planeIdx)),line_shape=lineStyle,line=dict(color=DEFAULT_PLOTLY_COLORS[planeIdx],dash=dash,width=2)),row=1,col=2)
    figure.add_trace(go.Scatter(x=xEdges,y=hitEffVsAngHist,name=str('Hit Eff vs Trk Cos plane: %d' % (planeIdx)),line_shape=lineStyle,line=dict(color=DEFAULT_PLOTLY_COLORS[planeIdx+3],dash=dash,width=2)),row=1,col=2)
        
    figure.update_xaxes(title={"text":"Track Cos(x)","standoff":10},row=1,col=2)
    figure.update_yaxes(title_text="Efficiency",row=1,col=2)
        
        
def plotDetails(figure,dataMap,lineStyle="hvh",dash="solid"):
    for planeIdx in range(3):
        validTrackArray = np.array(dataMap["validTracks"][planeIdx])
        
        selectGoodTracks = validTrackArray>0
        
        allROIArray      = np.array(dataMap["allROIs"][planeIdx])[selectGoodTracks]
        dataROIArray     = np.array(dataMap["dataROIs"][planeIdx])[selectGoodTracks]
        maxValArray      = np.array(dataMap["simMaxVals"][planeIdx])[selectGoodTracks]
        rawPHArray       = np.array(dataMap["rawDigitPHs"][planeIdx])[selectGoodTracks]
        dataHitArray     = np.array(dataMap["dataHits"][planeIdx])[selectGoodTracks]
        simChargeArray   = np.array(dataMap["simChargeVals"][planeIdx])[selectGoodTracks]
        hitChargeArray   = np.array(dataMap["hitCharges"][planeIdx])[selectGoodTracks]
        hitIntegralArray = np.array(dataMap["hitIntegrals"][planeIdx])[selectGoodTracks]
    
        # Angular efficiencies
        trkCosX = np.array(dataMap["trkCosXVals"][planeIdx])

        # Maximum simulated pulse height
        maxValues, xEdges = np.histogram(maxValArray[maxValArray>1.],bins=200, range=(0,5000.)) 
        
        xEdges = 0.5 * (xEdges[:-1] + xEdges[1:])
        figure.add_trace(go.Scatter(x=xEdges,y=maxValues,name=str('Max PH plane: %d' % (planeIdx)),line_shape=lineStyle,line=dict(color=DEFAULT_PLOTLY_COLORS[planeIdx],dash=dash,width=2)),row=1,col=1)
        figure.update_xaxes(title={"text":"Pulse Height (ADC)","standoff":10},row=1,col=1)
        figure.update_yaxes(title_text="Counts/ADC",row=1,col=1)
        
        # overlap
        #simOverlaps = np.array(dataMap["overlaps"][planeIdx])
        #simOverlap, xEdges = np.histogram(simOverlaps[simOverlaps>0],bins=40, range=(0,50.)) #max(overlaps[planeIdx])))
        #
        #xEdges = 0.5 * (xEdges[:-1] + xEdges[1:])
        #roiEfficFig.add_trace(go.Scatter(x=xEdges,y=simOverlap,name=str('Overlap plane: %d' % (planeIdx)),line_shape=lineStyle,line=dict(color=DEFAULT_PLOTLY_COLORS[planeIdx],dash=dash,width=2)),row=3,col=2)
        
        # track cos x
        trackAng, xEdges = np.histogram(trkCosX,bins=20, range=(-1.1,1.1)) #max(overlaps[planeIdx])))
        
        xEdges = 0.5 * (xEdges[:-1] + xEdges[1:])
        figure.add_trace(go.Scatter(x=xEdges,y=trackAng,name=str('Track Cos plane: %d' % (planeIdx)),line_shape=lineStyle,line=dict(color=DEFAULT_PLOTLY_COLORS[planeIdx],dash=dash,width=2)),row=1,col=2)
        figure.update_xaxes(title={"text":"Track Cos(x)","standoff":10},row=1,col=2)
        figure.update_yaxes(title_text="Counts",row=1,col=2)
        
        # Peak Amplitude
    #    peakAmplitudes = np.array(hitPeakAmps[planeIdx])
        peakAmplitudes = np.array(dataMap["rawDigitPHs"][planeIdx])[selectGoodTracks]

        peakAmp, xEdges = np.histogram(peakAmplitudes[dataROIArray>0],bins=100, range=(0,100.)) #(min(deltaStarts[planeIdx]),max(deltaStarts[planeIdx])))
        
        #peakAmplitudes = np.array(dataMap["hitPeakAmps"][planeIdx])[selectGoodTracks]

        #peakAmp, xEdges = np.histogram(peakAmplitudes[dataHitArray>0],bins=100, range=(0,100.)) #(min(deltaStarts[planeIdx]),max(deltaStarts[planeIdx])))
        
        xEdges = 0.5 * (xEdges[:-1] + xEdges[1:])
        figure.add_trace(go.Scatter(x=xEdges,y=peakAmp,name=str('Peak Amp plane: %d' % (planeIdx)),line_shape=lineStyle,line=dict(color=DEFAULT_PLOTLY_COLORS[planeIdx],dash=dash,width=2)),row=1,col=3)
        figure.update_xaxes(title={"text":"RawDigit Pulse Height (ADC)","standoff":10},row=1,col=3)
        figure.update_yaxes(title_text="Counts/ADC",row=1,col=3)
        
        # ROI Delta T
        deltaTs = np.array(dataMap["deltaTicks"][planeIdx])
        deltaT, xEdges = np.histogram(deltaTs[deltaTs>-1000],bins=25, range=(-12.5,12.5)) #(min(deltaStarts[planeIdx]),max(deltaStarts[planeIdx])))
        
        xEdges = 0.5 * (xEdges[:-1] + xEdges[1:])
        figure.add_trace(go.Scatter(x=xEdges,y=deltaT,name=str('Delta T plane: %d' % (planeIdx)),line_shape=lineStyle,line=dict(color=DEFAULT_PLOTLY_COLORS[planeIdx],dash=dash,width=2)),row=2,col=1)
        figure.update_xaxes(title={"text":"ROI Delta T (ticks)","standoff":10},row=2,col=1)
        figure.update_yaxes(title_text="Counts/Tick",row=2,col=1)
        
        # Hit Delta T
        deltaTs = np.array(dataMap["hitDeltaTs"][planeIdx])
        deltaT, xEdges = np.histogram(deltaTs[deltaTs>-1000],bins=25, range=(-12.5,12.5)) #(min(deltaStarts[planeIdx]),max(deltaStarts[planeIdx])))
        
        xEdges = 0.5 * (xEdges[:-1] + xEdges[1:])
        figure.add_trace(go.Scatter(x=xEdges,y=deltaT,name=str('Hit Delta T plane: %d' % (planeIdx)),line_shape=lineStyle,line=dict(color=DEFAULT_PLOTLY_COLORS[planeIdx],dash=dash,width=2)),row=2,col=2)
        figure.update_xaxes(title={"text":"Hit Delta T (ticks)","standoff":10},row=2,col=2)
        figure.update_yaxes(title_text="Counts/Tick",row=2,col=2)
        
        # Hit Multiplicities
        #mults = np.array(dataMap["hitMults"][planeIdx])
        #mult, xEdges = np.histogram(mults[peakAmplitudes>0],bins=15, range=(0,15)) #(min(deltaStarts[planeIdx]),max(deltaStarts[planeIdx])))
        #
        #xEdges = 0.5 * (xEdges[:-1] + xEdges[1:])
        #roiEfficFig.add_trace(go.Scatter(x=xEdges,y=mult,name=str('Hit Multiplicity plane: %d' % (planeIdx)),line_shape=lineStyle,line=dict(color=DEFAULT_PLOTLY_COLORS[planeIdx],dash=dash,width=2)),row=4,col=3)

        maxTickVals    = np.array(dataMap["maxTickVals"][planeIdx])[selectGoodTracks]
        simMaxTickVals = np.array(dataMap["simMaxTickVals"][planeIdx])[selectGoodTracks]
        
        deltaSimTicks, xEdges = np.histogram(maxTickVals-simMaxTickVals, bins=21, range=(-10.5,10.5))
        
        xEdges = 0.5 * (xEdges[:-1] + xEdges[1:])
        figure.add_trace(go.Scatter(x=xEdges,y=deltaSimTicks,name=str('Hit Multiplicity plane: %d' % (planeIdx)),line_shape=lineStyle,line=dict(color=DEFAULT_PLOTLY_COLORS[planeIdx],dash=dash,width=2)),row=2,col=3)
        
        # Selection to get rid of bad associations to truth info
        selectGoodHits = np.logical_and(dataHitArray>0,maxValArray>200.)
        
        # Simulated charges
        simCharges, xEdges = np.histogram(simChargeArray[selectGoodHits],bins=200, range=(0,35000.)) 
        
        xEdges = 0.5 * (xEdges[:-1] + xEdges[1:])
        figure.add_trace(go.Scatter(x=xEdges,y=simCharges,name=str('Sim Charges plane: %d' % (planeIdx)),line_shape=lineStyle,line=dict(color=DEFAULT_PLOTLY_COLORS[planeIdx],dash=dash,width=2)),row=3,col=1)
        figure.update_xaxes(title={"text":"Charge Deposited (ADC)","standoff":10},row=3,col=1)
        figure.update_yaxes(title_text="Counts/Tick",row=3,col=1)
        
        # Hit charges
        hitCharges, xEdges = np.histogram(hitChargeArray[selectGoodHits],bins=100, range=(-10.,750.)) 
        
        xEdges = 0.5 * (xEdges[:-1] + xEdges[1:])
        figure.add_trace(go.Scatter(x=xEdges,y=hitCharges,name=str('Hit Charges plane: %d' % (planeIdx)),line_shape=lineStyle,line=dict(color=DEFAULT_PLOTLY_COLORS[planeIdx],dash=dash,width=2)),row=3,col=2)
        figure.update_xaxes(title={"text":"Hit SummedADC (ADC)","standoff":10},row=3,col=2)
        figure.update_yaxes(title_text="Counts/Tick",row=3,col=2)
         
        # Hit charges
        hitIntegrals, xEdges = np.histogram(hitIntegralArray[selectGoodHits],bins=100, range=(-10.,750.)) 
        
        xEdges = 0.5 * (xEdges[:-1] + xEdges[1:])
        figure.add_trace(go.Scatter(x=xEdges,y=hitIntegrals,name=str('Hit Charges plane: %d' % (planeIdx)),line_shape=lineStyle,line=dict(color=DEFAULT_PLOTLY_COLORS[planeIdx],dash=dash,width=2)),row=3,col=3)
        figure.update_xaxes(title={"text":"Hit Integral (ADC)","standoff":10},row=3,col=3)
        figure.update_yaxes(title_text="Counts/Tick",row=3,col=3)
        
