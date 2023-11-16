# The Channel To Wire mapping needs these libraries
# All of this assumes you have set up the icarusalg package so you can interface to LArSoft services
import ROOT
import ICARUSservices as services
import galleryUtils
from tqdm import tqdm

# And here recover the necessary services
def getServices():
    detClocks      = services.ServiceManager('DetectorClocks')
    detProperties  = services.ServiceManager('DetectorProperties')
    geometryCore   = services.ServiceManager('Geometry')
    lar_properties = services.ServiceManager('LArProperties')

    return detClocks,detProperties,geometryCore,lar_properties

# Define here an object for mapping channel ids to WireIDs (where we have to build this map because we need the WireID to call geometry service functions...)

class ChannelToWireMap:
    def __init__(self,geometryCore):
        self.channelToWireIDMap = {}
        
        print("ChanelToWireMap: Building the mapping between channel IDs and WireIDs")
        print("                 ==> Geometry, n cryo:",geometryCore.Ncryostats(),", n TPC:",geometryCore.NTPC(),", n planes:",geometryCore.Nplanes())
        
        for cryoIdx in tqdm(range(geometryCore.Ncryostats())):
            print("** Cryostat",cryoIdx," ***")
            for TPCidx in range(geometryCore.NTPC()):
                print("   ** TPC",TPCidx," **")
                for planeIdx in range(geometryCore.Nplanes()):
                    planeID     = ROOT.geo.PlaneID(cryoIdx,TPCidx,planeIdx)
                    plane       = geometryCore.Plane(planeID)
                    nWires      = plane.Nwires()
                    wireIDFirst = ROOT.geo.WireID(cryoIdx,TPCidx,planeIdx,0)
                    wireIDLast  = ROOT.geo.WireID(cryoIdx,TPCidx,planeIdx,nWires-1)
                    print("      -- Plane:",planeIdx,", # wires:",nWires,", first channel:",geometryCore.PlaneWireToChannel(wireIDFirst),", last channel:",geometryCore.PlaneWireToChannel(wireIDLast))
                    for wireIdx in range(nWires):
                        wireID = ROOT.geo.WireID(cryoIdx,TPCidx,planeIdx,wireIdx)
                        channel = geometryCore.PlaneWireToChannel(wireID)
                        self.channelToWireIDMap.setdefault(channel,[]).append(wireID)

# Define object to handle channel mapping - going from LArSoft channel back to electronics space
# This needs the library "urllib"
import urllib

class ChannelMapping:
    """
    We define an object to handle the mapping of channel ids back to electronics space.
    This requires access to the channel mapping database and the secret decoder mapping to crate name
    """
    def __init__(self):
        self.flangeIDToCrateMap = {}
        
        self.flangeIDToCrateMap[19]  = "WW01T";
        
        print("ChannelMapping: setting up the flange to crate name map")
        
        # we need to get this moved into the database...
        self.flangeIDToCrateMap[68]  = "WW01M";
        self.flangeIDToCrateMap[41]  = "WW01B";
        self.flangeIDToCrateMap[11]  = "WW02";
        self.flangeIDToCrateMap[17]  = "WW03";
        self.flangeIDToCrateMap[36]  = "WW04";# Define object to handle channel mapping - going from LArSoft channel back to electronics space
# This needs the library "urllib"
import urllib

class ChannelMapping:
    """
    We define an object to handle the mapping of channel ids back to electronics space.
    This requires access to the channel mapping database and the secret decoder mapping to crate name
    """
    def __init__(self):
        self.flangeIDToCrateMap = {}
        
        self.flangeIDToCrateMap[19]  = "WW01T";
        
        print("ChannelMapping: setting up the flange to crate name map")
        
        # we need to get this moved into the database...
        self.flangeIDToCrateMap[68]  = "WW01M";
        self.flangeIDToCrateMap[41]  = "WW01B";
        self.flangeIDToCrateMap[11]  = "WW02";
        self.flangeIDToCrateMap[17]  = "WW03";
        self.flangeIDToCrateMap[36]  = "WW04";
        self.flangeIDToCrateMap[18]  = "WW05";
        self.flangeIDToCrateMap[58]  = "WW06";
        self.flangeIDToCrateMap[71]  = "WW07";
        self.flangeIDToCrateMap[14]  = "WW08";
        self.flangeIDToCrateMap[25]  = "WW09";
        self.flangeIDToCrateMap[34]  = "WW10";
        self.flangeIDToCrateMap[67]  = "WW11";
        self.flangeIDToCrateMap[33]  = "WW12";
        self.flangeIDToCrateMap[87]  = "WW13";
        self.flangeIDToCrateMap[10]  = "WW14";
        self.flangeIDToCrateMap[59]  = "WW15";
        self.flangeIDToCrateMap[95]  = "WW16";
        self.flangeIDToCrateMap[22]  = "WW17";
        self.flangeIDToCrateMap[91]  = "WW18";
        self.flangeIDToCrateMap[61]  = "WW19";
        self.flangeIDToCrateMap[55]  = "WW20T";
        self.flangeIDToCrateMap[97]  = "WW20M";
        self.flangeIDToCrateMap[100] = "WW20B";
        self.flangeIDToCrateMap[83]  = "WE01T";
        self.flangeIDToCrateMap[85]  = "WE01M";
        self.flangeIDToCrateMap[7]   = "WE01B";
        self.flangeIDToCrateMap[80]  = "WE02";
        self.flangeIDToCrateMap[52]  = "WE03";
        self.flangeIDToCrateMap[32]  = "WE04";
        self.flangeIDToCrateMap[70]  = "WE05";
        self.flangeIDToCrateMap[74]  = "WE06";
        self.flangeIDToCrateMap[46]  = "WE07";
        self.flangeIDToCrateMap[81]  = "WE08";
        self.flangeIDToCrateMap[63]  = "WE09";
        self.flangeIDToCrateMap[30]  = "WE10";
        self.flangeIDToCrateMap[51]  = "WE11";
        self.flangeIDToCrateMap[90]  = "WE12";
        self.flangeIDToCrateMap[23]  = "WE13";
        self.flangeIDToCrateMap[93]  = "WE14";
        self.flangeIDToCrateMap[92]  = "WE15";
        self.flangeIDToCrateMap[88]  = "WE16";
        self.flangeIDToCrateMap[73]  = "WE17";
        self.flangeIDToCrateMap[1]   = "WE18";
        self.flangeIDToCrateMap[66]  = "WE19";
        self.flangeIDToCrateMap[48]  = "WE20T";
        self.flangeIDToCrateMap[13]  = "WE20M";
        self.flangeIDToCrateMap[56]  = "WE20B";
        self.flangeIDToCrateMap[94]  = "EW01T";
        self.flangeIDToCrateMap[77]  = "EW01M";
        self.flangeIDToCrateMap[72]  = "EW01B";
        self.flangeIDToCrateMap[65]  = "EW02";
        self.flangeIDToCrateMap[4]   = "EW03";
        self.flangeIDToCrateMap[89]  = "EW04";
        self.flangeIDToCrateMap[37]  = "EW05";
        self.flangeIDToCrateMap[76]  = "EW06";
        self.flangeIDToCrateMap[49]  = "EW07";
        self.flangeIDToCrateMap[60]  = "EW08";
        self.flangeIDToCrateMap[21]  = "EW09";
        self.flangeIDToCrateMap[6]   = "EW10";
        self.flangeIDToCrateMap[62]  = "EW11";
        self.flangeIDToCrateMap[2]   = "EW12";
        self.flangeIDToCrateMap[29]  = "EW13";
        self.flangeIDToCrateMap[44]  = "EW14";
        self.flangeIDToCrateMap[9]   = "EW15";
        self.flangeIDToCrateMap[31]  = "EW16";
        self.flangeIDToCrateMap[98]  = "EW17";
        self.flangeIDToCrateMap[38]  = "EW18";
        self.flangeIDToCrateMap[99]  = "EW19";
        self.flangeIDToCrateMap[53]  = "EW20T";
        self.flangeIDToCrateMap[82]  = "EW20M";
        self.flangeIDToCrateMap[35]  = "EW20B";
        self.flangeIDToCrateMap[96]  = "EE01T";
        self.flangeIDToCrateMap[28]  = "EE01M";
        self.flangeIDToCrateMap[16]  = "EE01B";
        self.flangeIDToCrateMap[69]  = "EE02";
        self.flangeIDToCrateMap[20]  = "EE03";
        self.flangeIDToCrateMap[79]  = "EE04";
        self.flangeIDToCrateMap[50]  = "EE05";
        self.flangeIDToCrateMap[45]  = "EE06";
        self.flangeIDToCrateMap[84]  = "EE07";
        self.flangeIDToCrateMap[42]  = "EE08";
        self.flangeIDToCrateMap[39]  = "EE09";
        self.flangeIDToCrateMap[26]  = "EE10";
        self.flangeIDToCrateMap[64]  = "EE11";
        self.flangeIDToCrateMap[43]  = "EE12";
        self.flangeIDToCrateMap[47]  = "EE13";
        self.flangeIDToCrateMap[15]  = "EE14";
        self.flangeIDToCrateMap[3]   = "EE15";
        self.flangeIDToCrateMap[27]  = "EE16";
        self.flangeIDToCrateMap[24]  = "EE17";
        self.flangeIDToCrateMap[40]  = "EE18";
        self.flangeIDToCrateMap[75]  = "EE19";
        self.flangeIDToCrateMap[86]  = "EE20T";
        self.flangeIDToCrateMap[54]  = "EE20M";
        self.flangeIDToCrateMap[8]   = "EE20B";

        # This allows us to map the readout board id to the crate name
        self.readoutBoardIDToCrateMap = {}
        
        self.urlReadoutBoards = "https://dbdata0vm.fnal.gov:9443/QE/hw/app/SQ/query?dbname=icarus_hardware_prd&t=readout_boards"
        readoutBoards = urllib.request.urlopen(self.urlReadoutBoards)
        
        print("ChannelMapping: Building the readout board ID to crate name map")
        
        for line in readoutBoards:
            splitLine = line.decode("utf-8").split(",")
            # avoid the first line which describes the columns
            if "readout_board_id" in splitLine[0]:
                print("Column labels:",splitLine)
                continue
            self.readoutBoardIDToCrateMap.setdefault(int(splitLine[0]),[]).append(self.flangeIDToCrateMap[int(splitLine[1])])
        
        # Now we get the mapping of channels to the crate name
        self.urlDaqChannels = "https://dbdata0vm.fnal.gov:9443/QE/hw/app/SQ/query?dbname=icarus_hardware_prd&t=daq_channels"
        
        daqChannels = urllib.request.urlopen(self.urlDaqChannels)

        self.channelToCrateInfoMap = {}

        print("ChannelMapping: Building the channel to crate info map...")

        for line in tqdm(daqChannels):
            splitLine = line.decode("utf-8").split(",")
            if "channel_id" in splitLine[0]:
                #print("Column labels:",splitLine)
                continue
            crateName = self.readoutBoardIDToCrateMap[int(splitLine[2])]
            self.channelToCrateInfoMap[int(splitLine[0])] = {"CrateName":crateName, 
                                                             "readout_board_id":int(splitLine[2]), 
                                                             "readout_board_slot":int(splitLine[4]), 
                                                             "channel_number":int(splitLine[5]), 
                                                             "wire_number":int(splitLine[1]),
                                                             "plane":splitLine[10],
                                                             "channel_type":splitLine[12]}
            
            if "induction" not in splitLine[10].lower() and "collection" not in splitLine[10].lower():
                print("--> channel:",int(splitLine[5])," in crate:",crateName," is of type:",splitLine[10])
            
        print("ChannelMapping: Done with initialization!")
            

        

        self.flangeIDToCrateMap[18]  = "WW05";
        self.flangeIDToCrateMap[58]  = "WW06";
        self.flangeIDToCrateMap[71]  = "WW07";
        self.flangeIDToCrateMap[14]  = "WW08";
        self.flangeIDToCrateMap[25]  = "WW09";
        self.flangeIDToCrateMap[34]  = "WW10";
        self.flangeIDToCrateMap[67]  = "WW11";
        self.flangeIDToCrateMap[33]  = "WW12";
        self.flangeIDToCrateMap[87]  = "WW13";
        self.flangeIDToCrateMap[10]  = "WW14";
        self.flangeIDToCrateMap[59]  = "WW15";
        self.flangeIDToCrateMap[95]  = "WW16";
        self.flangeIDToCrateMap[22]  = "WW17";
        self.flangeIDToCrateMap[91]  = "WW18";
        self.flangeIDToCrateMap[61]  = "WW19";
        self.flangeIDToCrateMap[55]  = "WW20T";
        self.flangeIDToCrateMap[97]  = "WW20M";
        self.flangeIDToCrateMap[100] = "WW20B";
        self.flangeIDToCrateMap[83]  = "WE01T";
        self.flangeIDToCrateMap[85]  = "WE01M";
        self.flangeIDToCrateMap[7]   = "WE01B";
        self.flangeIDToCrateMap[80]  = "WE02";
        self.flangeIDToCrateMap[52]  = "WE03";
        self.flangeIDToCrateMap[32]  = "WE04";
        self.flangeIDToCrateMap[70]  = "WE05";
        self.flangeIDToCrateMap[74]  = "WE06";
        self.flangeIDToCrateMap[46]  = "WE07";
        self.flangeIDToCrateMap[81]  = "WE08";
        self.flangeIDToCrateMap[63]  = "WE09";
        self.flangeIDToCrateMap[30]  = "WE10";
        self.flangeIDToCrateMap[51]  = "WE11";
        self.flangeIDToCrateMap[90]  = "WE12";
        self.flangeIDToCrateMap[23]  = "WE13";
        self.flangeIDToCrateMap[93]  = "WE14";
        self.flangeIDToCrateMap[92]  = "WE15";
        self.flangeIDToCrateMap[88]  = "WE16";
        self.flangeIDToCrateMap[73]  = "WE17";
        self.flangeIDToCrateMap[1]   = "WE18";
        self.flangeIDToCrateMap[66]  = "WE19";
        self.flangeIDToCrateMap[48]  = "WE20T";
        self.flangeIDToCrateMap[13]  = "WE20M";
        self.flangeIDToCrateMap[56]  = "WE20B";
        self.flangeIDToCrateMap[94]  = "EW01T";
        self.flangeIDToCrateMap[77]  = "EW01M";
        self.flangeIDToCrateMap[72]  = "EW01B";
        self.flangeIDToCrateMap[65]  = "EW02";
        self.flangeIDToCrateMap[4]   = "EW03";
        self.flangeIDToCrateMap[89]  = "EW04";
        self.flangeIDToCrateMap[37]  = "EW05";
        self.flangeIDToCrateMap[76]  = "EW06";
        self.flangeIDToCrateMap[49]  = "EW07";
        self.flangeIDToCrateMap[60]  = "EW08";
        self.flangeIDToCrateMap[21]  = "EW09";
        self.flangeIDToCrateMap[6]   = "EW10";
        self.flangeIDToCrateMap[62]  = "EW11";
        self.flangeIDToCrateMap[2]   = "EW12";
        self.flangeIDToCrateMap[29]  = "EW13";
        self.flangeIDToCrateMap[44]  = "EW14";
        self.flangeIDToCrateMap[9]   = "EW15";
        self.flangeIDToCrateMap[31]  = "EW16";
        self.flangeIDToCrateMap[98]  = "EW17";
        self.flangeIDToCrateMap[38]  = "EW18";
        self.flangeIDToCrateMap[99]  = "EW19";
        self.flangeIDToCrateMap[53]  = "EW20T";
        self.flangeIDToCrateMap[82]  = "EW20M";
        self.flangeIDToCrateMap[35]  = "EW20B";
        self.flangeIDToCrateMap[96]  = "EE01T";
        self.flangeIDToCrateMap[28]  = "EE01M";
        self.flangeIDToCrateMap[16]  = "EE01B";
        self.flangeIDToCrateMap[69]  = "EE02";
        self.flangeIDToCrateMap[20]  = "EE03";
        self.flangeIDToCrateMap[79]  = "EE04";
        self.flangeIDToCrateMap[50]  = "EE05";
        self.flangeIDToCrateMap[45]  = "EE06";
        self.flangeIDToCrateMap[84]  = "EE07";
        self.flangeIDToCrateMap[42]  = "EE08";
        self.flangeIDToCrateMap[39]  = "EE09";
        self.flangeIDToCrateMap[26]  = "EE10";
        self.flangeIDToCrateMap[64]  = "EE11";
        self.flangeIDToCrateMap[43]  = "EE12";
        self.flangeIDToCrateMap[47]  = "EE13";
        self.flangeIDToCrateMap[15]  = "EE14";
        self.flangeIDToCrateMap[3]   = "EE15";
        self.flangeIDToCrateMap[27]  = "EE16";
        self.flangeIDToCrateMap[24]  = "EE17";
        self.flangeIDToCrateMap[40]  = "EE18";
        self.flangeIDToCrateMap[75]  = "EE19";
        self.flangeIDToCrateMap[86]  = "EE20T";
        self.flangeIDToCrateMap[54]  = "EE20M";
        self.flangeIDToCrateMap[8]   = "EE20B";

        # This allows us to map the readout board id to the crate name
        self.readoutBoardIDToCrateMap = {}
        
        self.urlReadoutBoards = "https://dbdata0vm.fnal.gov:9443/QE/hw/app/SQ/query?dbname=icarus_hardware_prd&t=readout_boards"
        readoutBoards = urllib.request.urlopen(self.urlReadoutBoards)
        
        print("ChannelMapping: Building the readout board ID to crate name map")
        
        for line in readoutBoards:
            splitLine = line.decode("utf-8").split(",")
            # avoid the first line which describes the columns
            if "readout_board_id" in splitLine[0]:
                print("Column labels:",splitLine)
                continue
            self.readoutBoardIDToCrateMap.setdefault(int(splitLine[0]),[]).append(self.flangeIDToCrateMap[int(splitLine[1])])
        
        # Now we get the mapping of channels to the crate name
        self.urlDaqChannels = "https://dbdata0vm.fnal.gov:9443/QE/hw/app/SQ/query?dbname=icarus_hardware_prd&t=daq_channels"
        
        daqChannels = urllib.request.urlopen(self.urlDaqChannels)

        self.channelToCrateInfoMap = {}

        print("ChannelMapping: Building the channel to crate info map...")

        for line in tqdm(daqChannels):
            splitLine = line.decode("utf-8").split(",")
            if "channel_id" in splitLine[0]:
                #print("Column labels:",splitLine)
                continue
            crateName = self.readoutBoardIDToCrateMap[int(splitLine[2])]
            self.channelToCrateInfoMap[int(splitLine[0])] = {"CrateName":crateName, 
                                                             "readout_board_id":int(splitLine[2]), 
                                                             "readout_board_slot":int(splitLine[4]), 
                                                             "channel_number":int(splitLine[5]), 
                                                             "wire_number":int(splitLine[1]),
                                                             "plane":splitLine[10],
                                                             "channel_type":splitLine[12]}
            
            if "induction" not in splitLine[10].lower() and "collection" not in splitLine[10].lower():
                print("--> channel:",int(splitLine[5])," in crate:",crateName," is of type:",splitLine[10])
            
        print("ChannelMapping: Done with initialization!")
            

        
