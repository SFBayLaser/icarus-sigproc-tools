# Note that the analysis functions below need to decode art root data objects so we will need 
# access to the gallery utilities to access theb
# All of this assumes you have set up the icarusalg package so you can interface to LArSoft services
import ROOT
import ICARUSservices as services
import galleryUtils
import numpy as np

import plotly.graph_objects as go
import plotly.subplots as subplots
from   plotly.colors import DEFAULT_PLOTLY_COLORS

from tqdm import tqdm

# Define a gaussian function
# x are the input coordinates
# PeakAmp is the amplitude of the gaussian
# PeakTime is the center of the gaussian
# sigma is the sigma of the gaussian
# baseline is the default baseline of the waveform
def gaus(x,peakAmp,peakTime,sigma,baseline):
       return peakAmp*np.exp(-0.5*(x-peakTime)**2/(sigma**2))+baseline


# Define a generic function to map channels to the individual objects in that channel
def mapChannelsToObjects(objectTags, getObjectHandle):
    # First task is to build the channel to ROI map
    channelToObjects = {}
    
    for objectTag in objectTags:
        objectCol = getObjectHandle(objectTag).product()
        
        for object in objectCol :
            channel = object.Channel()
            
            if channel in channelToObjects:
                channelToObjects[channel].append(object)
            else:
                channelToObjects[channel] = [object]
    
    return channelToObjects

# Define a function to build the list of hits to use
def buildHitList(channel,channelToHit):
    hitList = []

    if channel in channelToHit:
        fullHitList = channelToHit[channel]

        if len(fullHitList) > 1000:
            lastHitIdx = 0
            bestHit    = fullHitList[0]
            bestAmp    = 0.

            #print("**** channel",bestHit.Channel()," has",len(fullHitList)," hits")
    
            for hit in fullHitList:
                hitMult = hit.Multiplicity()
                ndf     = hit.DegreesOfFreedom()
    
            #    if len(fullHitList) > 1:
            #        print("--Checking",hit.LocalIndex(),"(",lastHitIdx,"), mult:",hitMult,", ndf:",ndf,", chi:",hit.GoodnessOfFit(),", amp:",hit.PeakAmplitude())
    
                # There is only one hit in the snippet or its a long hit
                if hitMult == 1 or ndf == 1:
                    hitList.append(hit)
                    lastHitIdx = 0
                    bestAmp    = 0.
                    continue

                # Are we on a new snippet?
                hitIdx  = hit.LocalIndex()

                if hitIdx < lastHitIdx:
                    hitList.append(bestHit)
            #        print(">> saving hit, amplitude:",bestAmp,", index:",lastHitIdx)
                    lastHitIdx = 0
                    bestAmp = 0.
    
                # By definition the first hit on a snippet will start as the "best"
                if hit.PeakAmplitude() > bestAmp:
                    bestHit = hit
                    bestAmp = hit.PeakAmplitude()
    
                lastHitIdx = hitIdx
    
            if lastHitIdx > 0:
                hitList.append(bestHit)

            #print("  -->Done, have",len(hitList)," hits")
        else:
            hitList = fullHitList

    return hitList


# Define a function for finding the ROI and Hit finding efficiency
# maxEvents is the nuumber of events to analyze
# sampleEvents is the input art root events
# channelToWire is a mapping between channel number and resulting WireID objects
# detClocks is the LArSoft detector clocks service interface
# simChannelPath allows us to switch SimChannel source
def findEfficiencies(maxEvents, sampleEvents, channelToWireMap, detClocks, simChannelPath="largeant",simTickOffset=-2):
    rawDigitTags   = [ROOT.art.InputTag("MCDecodeTPCROI:PHYSCRATEDATATPCEE"),
                      ROOT.art.InputTag("MCDecodeTPCROI:PHYSCRATEDATATPCEW"),
                      ROOT.art.InputTag("MCDecodeTPCROI:PHYSCRATEDATATPCWE"),
                      ROOT.art.InputTag("MCDecodeTPCROI:PHYSCRATEDATATPCWW")]
    simChannelTags = [ROOT.art.InputTag(simChannelPath)]
    channelROITags = [ROOT.art.InputTag("roifinder2d:PHYSCRATEDATATPCEE"),
                      ROOT.art.InputTag("roifinder2d:PHYSCRATEDATATPCEW"),
                      ROOT.art.InputTag("roifinder2d:PHYSCRATEDATATPCWE"),
                      ROOT.art.InputTag("roifinder2d:PHYSCRATEDATATPCWW")]
    gaushitTags    = [ROOT.art.InputTag("gaushitTPCEE"),
                      ROOT.art.InputTag("gaushitTPCEW"),
                      ROOT.art.InputTag("gaushitTPCWE"),
                      ROOT.art.InputTag("gaushitTPCWW")]
    simChanROITag  =  ROOT.art.InputTag("simChannelROI:All")
    mcTrackTag     = ROOT.art.InputTag("mcreco")

    getSimChannelHandle = galleryUtils.make_getValidHandle("std::vector<sim::SimChannel>",sampleEvents)
    getChannelROIHandle = galleryUtils.make_getValidHandle("std::vector<recob::ChannelROI>", sampleEvents)
    getGausHitHandle    = galleryUtils.make_getValidHandle("std::vector<recob::Hit>", sampleEvents)
    getSimChanROIHandle = galleryUtils.make_getValidHandle("std::vector<recob::ChannelROI>", sampleEvents)
    getRawDigitHandle   = galleryUtils.make_getValidHandle("std::vector<raw::RawDigit>", sampleEvents)
    getMcTrackHandle    = galleryUtils.make_getValidHandle("std::vector<sim::MCTrack>", sampleEvents)

    
    allROIs        = {0:[],1:[],2:[]}
    dataROIs       = {0:[],1:[],2:[]}
    simMaxVals     = {0:[],1:[],2:[]}
    simChargeVals  = {0:[],1:[],2:[]}
    maxTickVals    = {0:[],1:[],2:[]}
    simMaxTickVals = {0:[],1:[],2:[]}
    simLens        = {0:[],1:[],2:[]} 
    maxROIVals     = {0:[],1:[],2:[]}
    trkCosXVals    = {0:[],1:[],2:[]}
    overlaps       = {0:[],1:[],2:[]}
    deltaStarts    = {0:[],1:[],2:[]}
    deltaTicks     = {0:[],1:[],2:[]}
    dataLens       = {0:[],1:[],2:[]}
    hitPeakAmps    = {0:[],1:[],2:[]}
    hitCharges     = {0:[],1:[],2:[]}
    hitIntegrals   = {0:[],1:[],2:[]}
    hitDeltaTs     = {0:[],1:[],2:[]}
    hitMults       = {0:[],1:[],2:[]}
    rawDigitPHs    = {0:[],1:[],2:[]}
    dataHits       = {0:[],1:[],2:[]}
    validTracks    = {0:[],1:[],2:[]}

    # Container to return the results  
    dataMap = {}
    dataMap["allROIs"]        = allROIs
    dataMap["dataROIs"]       = dataROIs
    dataMap["simMaxVals"]     = simMaxVals
    dataMap["simChargeVals"]  = simChargeVals
    dataMap["maxTickVals"]    = maxTickVals
    dataMap["simMaxTickVals"] = simMaxTickVals
    dataMap["simLens"]        = simLens
    dataMap["maxROIVals"]     = maxROIVals
    dataMap["trkCosXVals"]    = trkCosXVals
    dataMap["overlaps"]       = overlaps
    dataMap["deltaStarts"]    = deltaStarts
    dataMap["deltaTicks"]     = deltaTicks
    dataMap["dataLens"]       = dataLens
    dataMap["hitPeakAmps"]    = hitPeakAmps
    dataMap["hitCharges"]     = hitCharges
    dataMap["hitIntegrals"]   = hitIntegrals
    dataMap["hitDeltaTs"]     = hitDeltaTs
    dataMap["hitMults"]       = hitMults
    dataMap["rawDigitPHs"]    = rawDigitPHs
    dataMap["dataHits"]       = dataHits
    dataMap["validTracks"]    = validTracks

    numEvents = 0
    
    for event in galleryUtils.forEach(sampleEvents):
        # First task is to build the channel to ROI map
        channelToROI = mapChannelsToObjects(channelROITags, getChannelROIHandle)
        
        # Channel to SimChannel...
        channelToSim = mapChannelsToObjects(simChannelTags, getSimChannelHandle)
                        
        # Build a similar mapping for hits
        channelToHit = mapChannelsToObjects(gaushitTags, getGausHitHandle)
                    
        # One more for the RawDigits...
        channelToRawDigit = mapChannelsToObjects(rawDigitTags, getRawDigitHandle)

        # Map of MCTrack ID to MCTrack
        mcTrackCol = getMcTrackHandle(mcTrackTag).product()
        
        trackIDToMCTrack = {}
        
        for mcTrack in mcTrackCol:
            trackIDToMCTrack[mcTrack.TrackID()] = mcTrack
         
        # Now we go through the sim channel information and try to match
        simChanROICol = getSimChanROIHandle(simChanROITag).product()
        
        for simChannel in simChanROICol:
            channel = simChannel.Channel()
            
            # Look up the plane for this channel
            wireIDs = channelToWireMap.channelToWireIDMap[channel]
    
            planeIdx = wireIDs[0].Plane
            
            roiList = []
            if channel in channelToROI:
                for roi in channelToROI[channel][0].SignalROI().get_ranges():
                    roiList.append(roi)
                            
            # We focus on the largest hit on a snippet (unless long hits)
            hitList = buildHitList(channel,channelToHit)

            rawDigitList = []
            if channel in channelToRawDigit:
                rawDigitList = channelToRawDigit[channel]
                
            tdcToIDEMap = ROOT.sim.SimChannel.TDCIDEs_t
            if channel in channelToSim:
                tdcToIDEMap = channelToSim[channel][0].TDCIDEMap()
        
            for simROI in simChannel.SignalROI().get_ranges():
                overlap    = 0
                match      = 0.
                startTick  = simROI.begin_index()
                endTick    = simROI.end_index()
                simMaxTick = np.argmax(simROI.data()) + startTick + simTickOffset
                simCharge  = np.sum(simROI.data())
                simMaxVal  = max(simROI.data()) / 3.
                simLen     = simROI.data().size()
                roiMaxVal  = 0
                deltaStart = -4096
                deltaTick  = -4096
                dataLen    = 0

                # Let's not consider charge deposits that are too small to be seen...
                if simMaxVal < 250:
                    continue
                
                # First task is to look at ROIs
                for roi in roiList:
                    if roi.begin_index() > endTick:
                        break

                    if roi.end_index() < startTick:
                        continue

                    if roi.begin_index() <= endTick and roi.end_index() >= startTick:
                        dataStart       = roi.begin_index()
                        overlap         = min(endTick,roi.end_index()) - max(startTick,dataStart)
                        overlapFraction = overlap / simROI.data().size()
                        dataMaxTick     = np.argmax(roi.data()) + dataStart
                        deltaTick       = dataMaxTick - simMaxTick
                        deltaStart      = roi.begin_index()-startTick
                        deltaEnd        = roi.end_index()-endTick
                        dataLen         = roi.data().size()
                        roiMaxVal       = max(roi.data())
                        match           = 1.
                        
                        break
                            
                allROIs[planeIdx].append(1.)
                dataROIs[planeIdx].append(match)
                simMaxVals[planeIdx].append(simMaxVal)
                simChargeVals[planeIdx].append(simCharge)
                simLens[planeIdx].append(simLen)
                maxTickVals[planeIdx].append(simMaxTick)
                maxROIVals[planeIdx].append(roiMaxVal)
                overlaps[planeIdx].append(overlap)
                deltaStarts[planeIdx].append(deltaStart)
                deltaTicks[planeIdx].append(deltaTick)
                dataLens[planeIdx].append(dataLen)
                
                # Now look at Guashits
                hitMatch     =  0.
                peakAmp      = -1
                peakCharge   = -1
                peakIntegral = -1
                deltaT       = -4096
                
                # This only makes sense if we found the ROI
                if match:
                    hitLen = len(hitList)

                    for hit in hitList:
                        hitPeak  = hit.PeakTime()
                        hitSigma = hit.RMS()
                        hitStart = hitPeak - 3.*hitSigma
                        hitEnd   = hitPeak + 3.*hitSigma
                        
                        #We are trying to get the hit closest to the actual sim energy deposit here
                        #if hitStart <= startTick+simLen and hitEnd >= startTick and abs(hitPeak-simMaxTick) < abs(deltaT):
                        if hitPeak <= startTick+simLen+1 and hitPeak >= startTick-1 and abs(hitPeak-simMaxTick) < abs(deltaT):
                            hitMatch     = 1.
                            peakAmp      = hit.PeakAmplitude()
                            peakCharge   = hit.SummedADC()
                            peakIntegral = hit.Integral()
                            deltaT       = hitPeak - simMaxTick
                        
                dataHits[planeIdx].append(hitMatch)
                hitPeakAmps[planeIdx].append(peakAmp)
                hitCharges[planeIdx].append(peakCharge)
                hitIntegrals[planeIdx].append(peakIntegral)
                hitDeltaTs[planeIdx].append(deltaT)
                hitMults[planeIdx].append(hitLen)
                
                peakRawDigit = 0.
                if len(rawDigitList) > 0:
                    rawDigit = rawDigitList[0]
                    if planeIdx == 2:
                        peakRawDigit = np.max(np.array(rawDigit.ADCs())[startTick:endTick])
                    else:
                        # Expand search area a bit
                        firstTick = max(0,startTick-5)
                        lastTick  = min(4095,endTick+5)
                        peakRawDigit = np.max(np.array(rawDigit.ADCs())[firstTick:lastTick]) - np.min(np.array(rawDigit.ADCs())[firstTick:lastTick])
                    
                rawDigitPHs[planeIdx].append(peakRawDigit)
                
                # Ok, try match tracks
                trackID   = -999
                trackCosX = -999.
                tdcMax    = 0
                peakMax   = -999
                
                if channel in channelToSim:
                    tdc = detClocks.DataForJob().TPCTick2TDC(simMaxTick) 
                    
                    for tdcToIDE in tdcToIDEMap:
                        if tdc == tdcToIDE.first:
                            #print("For tick:",simMaxTick,", TDCIDE tdc val:",tdcToIDE.first)
                            numElectrons = 0
                            trackID = -999
                            for ide in tdcToIDE.second:
                                numElectrons += ide.numElectrons
                                if trackID < -990:
                                    trackID = ide.trackID
                                    
                                #print("   --> numElectrons:",ide.numElectrons,", track id:",ide.trackID,", origTrackID:",ide.origTrackID)
                        
                        charge = channelToSim[channel][0].Charge(tdcToIDE.first)
                            
                        if charge > peakMax:
                            peakMax = charge
                            tdcMax  = tdcToIDE.first
                        
                if trackID > -999 and trackID < 0:
                    trackID = -trackID
                    
                validTrack = 0
                    
                if trackID in trackIDToMCTrack:
                    start4Mom = trackIDToMCTrack[trackID].Start().Momentum()
                    end4Mom   = trackIDToMCTrack[trackID].End().Momentum()
                    fourMom   = 0.5 * (start4Mom + end4Mom)
                    trackCosX = fourMom.Px() / np.sqrt(fourMom.Px()*fourMom.Px()+fourMom.Py()*fourMom.Py()+fourMom.Pz()*fourMom.Pz())
                    #print("  --> Track start mom:",trackIDToMCTrack[trackID].Start().Momentum(),", track cosx:",trackCosX)
                    validTrack = 1
                #elif trackID > -999:
                #    print("SimChannel IDE says trackID:",trackID)
                    
                simChanObjTick = detClocks.DataForJob().TPCTDC2Tick(tdcMax)
                
                trkCosXVals[planeIdx].append(trackCosX)
                validTracks[planeIdx].append(validTrack)
                simMaxTickVals[planeIdx].append(simChanObjTick)
            
        numEvents += 1
        
        if numEvents % (maxEvents//10) == 0:
            print("Processed",numEvents," of the requested",maxEvents," events")
        
        if numEvents >= maxEvents:
            break
    
    print("findEfficiencies processed",numEvents," events")
    
    return dataMap



# Define a function for finding the false positives for ROIs and Hits
# maxEvents is the nuumber of events to analyze
# sampleEvents is the input art root events
# channelToWire is a mapping between channel number and resulting WireID objects
# detClocks is the LArSoft detector clocks service interface
# simChannelPath allows us to switch SimChannel source
def findFalsePositives(maxEvents, sampleEvents, channelToWireMap, detClocks, simChannelPath="largeant"):
    rawDigitTags   = [ROOT.art.InputTag("MCDecodeTPCROI:PHYSCRATEDATATPCEE"),
                      ROOT.art.InputTag("MCDecodeTPCROI:PHYSCRATEDATATPCEW"),
                      ROOT.art.InputTag("MCDecodeTPCROI:PHYSCRATEDATATPCWE"),
                      ROOT.art.InputTag("MCDecodeTPCROI:PHYSCRATEDATATPCWW")]
    simChannelTags = [ROOT.art.InputTag(simChannelPath)]
    channelROITags = [ROOT.art.InputTag("roifinder:PHYSCRATEDATATPCEE"),
                      ROOT.art.InputTag("roifinder:PHYSCRATEDATATPCEW"),
                      ROOT.art.InputTag("roifinder:PHYSCRATEDATATPCWE"),
                      ROOT.art.InputTag("roifinder:PHYSCRATEDATATPCWW")]
    gaushitTags    = [ROOT.art.InputTag("gaushitTPCEE"),
                      ROOT.art.InputTag("gaushitTPCEW"),
                      ROOT.art.InputTag("gaushitTPCWE"),
                      ROOT.art.InputTag("gaushitTPCWW")]
    simChanROITag  = [ROOT.art.InputTag("simChannelROI:All")]
    mcTrackTag     = ROOT.art.InputTag("mcreco")

    getSimChannelHandle = galleryUtils.make_getValidHandle("std::vector<sim::SimChannel>",sampleEvents)
    getChannelROIHandle = galleryUtils.make_getValidHandle("std::vector<recob::ChannelROI>", sampleEvents)
    getGausHitHandle    = galleryUtils.make_getValidHandle("std::vector<recob::Hit>", sampleEvents)
    getSimChanROIHandle = galleryUtils.make_getValidHandle("std::vector<recob::ChannelROI>", sampleEvents)
    getRawDigitHandle   = galleryUtils.make_getValidHandle("std::vector<raw::RawDigit>", sampleEvents)
    getMcTrackHandle    = galleryUtils.make_getValidHandle("std::vector<sim::MCTrack>", sampleEvents)

    
    allROIs        = {0:[],1:[],2:[]}
    matchROIs      = {0:[],1:[],2:[]}
    roiMaxVals     = {0:[],1:[],2:[]}
    roiMaxTickVals = {0:[],1:[],2:[]}
    simMaxTickVals = {0:[],1:[],2:[]}
    simMaxVals     = {0:[],1:[],2:[]}
    overlaps       = {0:[],1:[],2:[]}
    deltaStarts    = {0:[],1:[],2:[]}
    deltaTicks     = {0:[],1:[],2:[]}
    roiLens        = {0:[],1:[],2:[]}
    simLens        = {0:[],1:[],2:[]}
    hitPeakAmps    = {0:[],1:[],2:[]}
    hitDeltaTs     = {0:[],1:[],2:[]}
    hitMults       = {0:[],1:[],2:[]}
    rawDigitPHs    = {0:[],1:[],2:[]}
    dataHits       = {0:[],1:[],2:[]}
    validTracks    = {0:[],1:[],2:[]}

    # Container to return the results  
    dataMap = {}
    dataMap["allROIs"]        = allROIs
    dataMap["matchROIs"]      = matchROIs
    dataMap["roiMaxVals"]     = roiMaxVals
    dataMap["roiMaxTickVals"] = roiMaxTickVals
    dataMap["simMaxTickVals"] = simMaxTickVals
    dataMap["simMaxVals"]     = simMaxVals
    dataMap["overlaps"]       = overlaps
    dataMap["deltaStarts"]    = deltaStarts
    dataMap["deltaTicks"]     = deltaTicks
    dataMap["roiLens"]        = roiLens
    dataMap["simLens"]        = simLens
    dataMap["hitPeakAmps"]    = hitPeakAmps
    dataMap["hitDeltaTs"]     = hitDeltaTs
    dataMap["hitMults"]       = hitMults
    dataMap["rawDigitPHs"]    = rawDigitPHs
    dataMap["dataHits"]       = dataHits
    dataMap["validTracks"]    = validTracks

    numEvents = 0
    
    for event in galleryUtils.forEach(sampleEvents):
        # First task is to build the channel to ROI map
        channelToSimROI = mapChannelsToObjects(simChanROITag, getSimChanROIHandle)
        
        # Channel to SimChannel...
        channelToSim = mapChannelsToObjects(simChannelTags, getSimChannelHandle)
                        
        # Build a similar mapping for hits
        channelToHit = mapChannelsToObjects(gaushitTags, getGausHitHandle)
                    
        # One more for the RawDigits...
        channelToRawDigit = mapChannelsToObjects(rawDigitTags, getRawDigitHandle)

        # Map of MCTrack ID to MCTrack
        mcTrackCol = getMcTrackHandle(mcTrackTag).product()
        
        trackIDToMCTrack = {}
        
        for mcTrack in mcTrackCol:
            trackIDToMCTrack[mcTrack.TrackID()] = mcTrack
            
        #print("******* Event",numEvents," *********")
            
        # Loop through the input ROIs from recon...
        for channelROITag in channelROITags:
            # Now we go through the sim channel information and try to match
            channelROICol = getChannelROIHandle(channelROITag).product()
            
            #print("Processing channelROITag",channelROITag)
            
            for channelROI in channelROICol:
                channel = channelROI.Channel()
                
                # Look up the plane for this channel
                wireIDs = channelToWireMap.channelToWireIDMap[channel]
        
                planeIdx = wireIDs[0].Plane
                
                simROIList = []
                if channel in channelToSimROI:
                    for roi in channelToSimROI[channel][0].SignalROI().get_ranges():
                        simROIList.append(roi)
                    
                hitList = []
                if channel in channelToHit:
                    hitList = channelToHit[channel]
                    
                rawDigitList = []
                if channel in channelToRawDigit:
                    rawDigitList = channelToRawDigit[channel]
                    
                tdcToIDEMap = ROOT.sim.SimChannel.TDCIDEs_t
                if channel in channelToSim:
                    tdcToIDEMap = channelToSim[channel][0].TDCIDEMap()
                    
                #print("  ++++ ROI for channel:",channel,", size of Sim:",len(simROIList)," ++++")
         
                for roi in channelROI.SignalROI().get_ranges():
                    overlap      = 0
                    match        = 0.
                    roiStartTick = roi.begin_index()
                    roiEndTick   = roi.end_index()
                    roiMaxTick   = np.argmax(roi.data()) + roiStartTick
                    roiMaxVal    = max(roi.data())
                    roiLen       = roi.data().size()
                    simMaxVal    = 0
                    simMaxTick   = -4096
                    deltaStart   = -4096
                    deltaTick    = -4096
                    simLen       = 0
                    
                    #print("  - ROI start/end",roiStartTick,"/",roiEndTick,", max/len",roiMaxVal,"/",roiLen)
                    
                    # First task is to match to simulation
                    for simROI in simROIList:
                        #print("    - Checking simROI:",simROI.begin_index(),",",simROI.end_index())
                        if simROI.begin_index() > roiEndTick:
                            break
                        if simROI.begin_index() <= roiEndTick and simROI.end_index() >= roiStartTick:
                            simStart        = simROI.begin_index()
                            overlap         = min(roiEndTick,simROI.end_index()) - max(roiStartTick,simStart)
                            overlapFraction = overlap / roi.data().size()
                            simMaxTick      = np.argmax(simROI.data()) + simStart
                            deltaTick       = roiMaxTick - simMaxTick
                            deltaStart      = simROI.begin_index()-roiStartTick
                            deltaEnd        = simROI.end_index()-roiEndTick
                            simLen          = simROI.data().size()
                            simMaxVal       = max(simROI.data()) / 3.
                            match           = 1
                            #print("      -----> matched!")
                            
                            if overlap/simLen > 0.1:
                                break
                                
                    allROIs[planeIdx].append(1.)
                    matchROIs[planeIdx].append(match)
                    simMaxVals[planeIdx].append(simMaxVal)
                    simMaxTickVals[planeIdx].append(simMaxTick)
                    roiMaxVals[planeIdx].append(roiMaxVal)
                    roiMaxTickVals[planeIdx].append(roiMaxTick)
                    overlaps[planeIdx].append(overlap)
                    deltaStarts[planeIdx].append(deltaStart)
                    deltaTicks[planeIdx].append(deltaTick)
                    simLens[planeIdx].append(simLen)
                    roiLens[planeIdx].append(roiLen)
                    
                    # Now look at Guashits
                    hitMatch = 0.
                    peakAmp  = 0.
                    deltaT   = -4096.
                    
                    # This only makes sense if we found the ROI
                    if match:
                        for hit in hitList:
                            hitPeak  = hit.PeakTime()
                            hitSigma = hit.RMS()
                            hitStart = hitPeak - 3.*hitSigma
                            hitEnd   = hitPeak + 3.*hitSigma
                            
                            #if hitStart <= endTick and hitEnd >= startTick and abs(hitPeak-simMaxTick) < abs(deltaT):
                            if hitStart <= simStart+simLen and hitEnd >= simStart and abs(hitPeak-simMaxTick) < abs(deltaT):
                                hitMatch = 1.
                                peakAmp  = hit.PeakAmplitude()
                                deltaT   = hitPeak - simMaxTick
                            
                    dataHits[planeIdx].append(hitMatch)
                    hitPeakAmps[planeIdx].append(peakAmp)
                    hitDeltaTs[planeIdx].append(deltaT)
                    hitMults[planeIdx].append(len(hitList))
                    
                    peakRawDigit = 0.
                    if len(rawDigitList) > 0:
                        rawDigit = rawDigitList[0]
                        if planeIdx == 2:
                            peakRawDigit = np.max(np.array(rawDigit.ADCs())[roiStartTick:roiEndTick])
                        else:
                            # Expand search area a bit
                            firstTick = max(0,roiStartTick-5)
                            lastTick  = min(4095,roiEndTick+5)
                            peakRawDigit = np.max(np.array(rawDigit.ADCs())[firstTick:lastTick]) - np.min(np.array(rawDigit.ADCs())[firstTick:lastTick])
                        
                    rawDigitPHs[planeIdx].append(peakRawDigit)
    
        numEvents += 1
        
        if numEvents % 20 == 0:
            print("Processed",numEvents," of the requested",maxEvents," events")
        
        if numEvents >= maxEvents:
            break
    
    print("processEvents processed",numEvents," events")
    
    return dataMap

