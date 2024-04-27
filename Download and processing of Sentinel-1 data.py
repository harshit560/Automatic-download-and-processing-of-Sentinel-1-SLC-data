import os
import shutil
import os
from snappy import GPF
from snappy import ProductIO
import os, gc
from snappy import HashMap
from snappy import jpy
#import matplotlib.pyplot as plt
#import matplotlib.colors as colors
import numpy as np
import json

import asf_search as asf
import geopandas as gpd
from shapely.geometry import box
from datetime import date
import pandas as pd

parameters = HashMap()

def read(filename):
    print('Reading...')
    print(filename)
    return ProductIO.readProduct(filename)


def topsar_split(product,IW,firstBurstIndex,lastBurstIndex):
    print('Apply TOPSAR Split...')
    parameters = HashMap()
    parameters.put('subswath', IW)
    parameters.put('firstBurstIndex',firstBurstIndex ) # added by me
    parameters.put('lastBurstIndex',lastBurstIndex ) # added by me
    parameters.put('selectedPolarisations', 'VV')
    output=GPF.createProduct("TOPSAR-Split", parameters, product)
    return output


def do_apply_orbit_file(product):
    parameters = HashMap()
    GPF.getDefaultInstance().getOperatorSpiRegistry().loadOperatorSpis()
    parameters.put('orbitType', 'Sentinel Precise (Auto Download)')
    parameters.put('polyDegree', '3')
    parameters.put('continueOnFail', True)
    return GPF.createProduct("Apply-Orbit-File", parameters, product)
    
    
def back_geocoding(product):
    print('back_geocoding ...')
    parameters.put("Digital Elevation Model", "SRTM 1Sec HGT (Auto Download)")
    parameters.put("DEM Resampling Method", "BILINEAR_INTERPOLATION")
    parameters.put("Resampling Type", "BILINEAR_INTERPOLATION")
    parameters.put("Mask out areas with no elevation", True)
    parameters.put("Output Deramp and Demod Phase", True)
    parameters.put("Disable Reramp", False)
    return GPF.createProduct("Back-Geocoding", parameters, product)


def Enhanced_Spectral_Diversity(product):
    parameters = HashMap()
    #parameters.put("fineWinWidthStr2",512)
    #parameters.put("fineWinHeightStr",512)
    #parameters.put("fineWinAccAzimuth",16)
    #parameters.put("fineWinAccRange",16)
    #parameters.put("fineWinOversampling",128)
    #parameters.put("xCorrThreshold",0.1)
    #parameters.put("cohThreshold",0.3)
    #parameters.put("numBlocksPerOverlap",10)
    #parameters.put("esdEstimator",'Periodogram')
    #parameters.put("weightFunc",'Inv Quadratic')
    #parameters.put("temporalBaselineType",'Number of images')
    #parameters.put("maxTemporalBaseline",4)
    #parameters.put("integrationMethod",'L1 and L2')
    #parameters.put("doNotWriteTargetBands",False)
    #parameters.put("useSuppliedRangeShift",False)
    #parameters.put("overallRangeShift",0)
    return GPF.createProduct("Enhanced-Spectral-Diversity", parameters, product)


def interferogram(product):
    print('Creating interferogram ...')
    parameters.put("Subtract flat-earth phase", True)
    parameters.put("Degree of \"Flat Earth\" polynomial", 5)
    parameters.put("Number of \"Flat Earth\" estimation points", 501)
    parameters.put("Orbit interpolation degree", 3)
    parameters.put("Include coherence estimation", True)
    parameters.put("Square Pixel", True)
    parameters.put("Independent Window Sizes", False)
    parameters.put("Coherence Azimuth Window Size", 10)
    parameters.put("Coherence Range Window Size", 2)
    return GPF.createProduct("Interferogram", parameters, product)


def topsar_deburst(source):  
    print('Doing deburst ...')
    parameters = HashMap()
    parameters.put("Polarisations", "VV,VH")
    output=GPF.createProduct("TOPSAR-Deburst", parameters, source)
    return output


def topophase_removal(product):
    print('Doing top phase removal ...')
    parameters.put("Orbit Interpolation Degree", 3)
    parameters.put("Digital Elevation Model", "SRTM 1Sec HGT (Auto Download)")
    parameters.put("Tile Extension[%]", 100)
    parameters.put("Output topographic phase band", True)
    parameters.put("Output elevation band", False)
    return GPF.createProduct("TopoPhaseRemoval", parameters, product)


def goldstein_phasefiltering(product):
    print('Doing goldstein filtering ...')
    parameters.put("Adaptive Filter Exponent in(0,1]:", 1.0)
    parameters.put("FFT Size", 64)
    parameters.put("Window Size", 3)
    parameters.put("Use coherence mask", False)
    parameters.put("Coherence Threshold in[0,1]:", 0.2)
    output = GPF.createProduct("GoldsteinPhaseFiltering", parameters, product)
    #os.chdir('/home/harshit/Desktop/JDK/nf')
    ProductIO.writeProduct(output, date1, 'BEAM-DIMAP')
    

def SNAPHU_export(product,SNAPHU_exp_folder):
    parameters = HashMap()
    parameters.put('targetFolder', SNAPHU_exp_folder) # 
    output = GPF.createProduct('SnaphuExport', parameters, product)
    ProductIO.writeProduct(output, SNAPHU_exp_folder, 'Snaphu')
    
    
def snaphu_unwrapping(product,target_Product_File,outFolder,filename):
    parameters = HashMap()
    parameters.put('targetProductFile', target_Product_File) # from SNAPHU_export
    parameters.put('outputFolder', outFolder)
    parameters.put('copyOutputAndDelete', 'Snaphu-unwrapping-after.vm')
    parameters.put('copyFilesTemplate', 'Snaphu-unwrapping-before.vm')
    output1 = GPF.createProduct('snaphu-unwrapping', parameters, product)
    ProductIO.writeProduct(output1, date1, 'BEAM-DIMAP')
    ProductIO.writeProduct(output1, date1, 'ENVI')
    
    print('Phase unwrapping performed successfully …')

def do_terrain_correction(source,band):
#def do_terrain_correction(source, proj, downsample):
    print('\tTerrain correction...')
    parameters = HashMap()
    parameters.put('demName', 'SRTM 1Sec HGT') # 'SRTM 3Sec'
#   parameters.put('imgResamplingMethod', 'BILINEAR_INTERPOLATION')
#   parameters.put('mapProjection', proj)       # comment this line if no need to convert to UTM/WGS84, default is WGS84
#   parameters.put('saveProjectedLocalIncidenceAngle', False)
    parameters.put('sourceBands', band)
    parameters.put('saveSelectedSourceBand', True)
#   parameters.put('nodataValueAtSea', False)
#   parameters.put('pixelSpacingInMeter', 35)
#   while downsample == 1:                      # downsample: 1 -- need downsample to 40m, 0 -- no need to downsample
#        parameters.put('pixelSpacingInMeter', 40.0)
#        break
    output = GPF.createProduct('Terrain-Correction', parameters, source)
    return output


def write_BEAM_DIMAP_format(product, filename):
    print('Saving BEAM-DIMAP format...')
    #os.chdir('/home/Desktop/JDK/nf')
    ProductIO.writeProduct(product, filename + '.dim', 'BEAM-DIMAP')
   

def write_tif_format(product, filename):
    print('Saving BEAM-DIMAP format...')
    #os.chdir('/home/Desktop/JDK/nf')
    ProductIO.writeProduct(product, filename + '.tif', 'GeoTiff')

    
def InSAR_pipeline_I(filename_1, filename_2,IW,firstBurstIndex,lastBurstIndex,out_filename):
    product_TOPSAR_1 = topsar_split(filename_1,IW,firstBurstIndex,lastBurstIndex)
    product_TOPSAR_2 = topsar_split(filename_2,IW,firstBurstIndex,lastBurstIndex)   
    product_orbitFile_1 = do_apply_orbit_file(product_TOPSAR_1)
    product_orbitFile_2 = do_apply_orbit_file(product_TOPSAR_2)
    product = back_geocoding([product_orbitFile_1, product_orbitFile_2])
    product = Enhanced_Spectral_Diversity(product)
    product = interferogram(product)
    product = topsar_deburst(product)
    product = topophase_removal(product)
    product = goldstein_phasefiltering(product)
    #product = read(r'C:\\Users\\Desktop\\20221025T125547.dim')#given from written file of goldstein filtering 
    #SNAPHU_exp_folder = 'C:\\Users\\Desktop\\New folder (14)' 
    #product = SNAPHU_export(product,SNAPHU_exp_folder)
    #snaphu_unwrapping(product,target_Product_File,outFolder,filename)
    
    
def InSAR_pipeline_III(in_filename_III,out_filename_III):
   
    product = read(in_filename_III)
    band_names = product.getBandNames()
    #print("Band names: {}".format(", ".join(band_names)))
    a= format(", ".join(band_names)) # band names as a comma separated string 
    b= a.split(',') # split string into list
    #change band names as to mintpy accepts them
    product.getBand(b[3].strip()).setName('Phase_ifg')
    product.getBand(b[4].strip()).setName('coh')
    #interferogram_TC = do_terrain_correction(product,band='Phase_ifg') # interferogram terrain correction
    #write_BEAM_DIMAP_format(interferogram_TC, out_filename_III+'_filt_int_sub_tc')
    coherence_TC = do_terrain_correction(product,band='coh') # coherence terrain correction
    #write_BEAM_DIMAP_format(coherence_TC, out_filename_III+'_coh_tc')
    write_tif_format(coherence_TC, out_filename_III+'_coh_tc')
    print("InSAR_pipeline_III complete")
    

#Download Sentinel-1 SLC image giving a shapefile of area of interest, time frame in DD/MM/YYYY of same year

### 1. Read Shapefile using Geopandas
gdf = gpd.read_file('/home/Desktop/JDK/coherence case studies/A/b23.shp')
### 2. Extract the Bounding Box Coordinates
bounds = gdf.total_bounds
### 3. Create GeoDataFrame of the Bounding Box 
gdf_bounds = gpd.GeoSeries([box(*bounds)])
### 4. Get WKT Coordinates
wkt_aoi = gdf_bounds.to_wkt().values.tolist()[0]


import datetime
import os
from zipfile import ZipFile

date_1=input('Enter the starting date (DD/MM/YYYY):')
date_2=input('Enter the ending date (DD/MM/YYYY):')
year1=int(date_1[6:10])
year2=int(date_2[6:10])
month1=int(date_1[3:5])
month2=int(date_2[3:5])
print(year1)
print(month1)
days = [31,28,31,30,31,30,31,31,30,31,30,31]
months=(year2-year1)*12+(month2-month1)

for month in range(month1,month1+months+1):
    

    results = asf.search(
        platform= asf.PLATFORM.SENTINEL1A,
        processingLevel=[asf.PRODUCT_TYPE.SLC],
        start = date(year1+int(month/12), (month-1)%12+1, 1),
        end = date(year1+int(month/12), (month-1)%12+1, days[month-1]),
        intersectsWith = wkt_aoi
        )
    print(f'Total Images Found: {len(results)}')
    ### Save Metadata to a Dictionary
    metadata = results.geojson()
    print(metadata)
    df = pd.DataFrame(metadata)
    df
    print(df['features'])


    #give your own id and password below
    session = asf.ASFSession().auth_with_creds('XXXXXX', 'XXXXXX')

    n = len(df['features'])
    urls1=[]
    urls2=[]
    boolean = False
    for i in range(n):
        FlightDirection1 = df['features'][i]['properties']['flightDirection']
        PathNumber1 = df['features'][i]['properties']['pathNumber']
        # FileName1 = df['features'][i]['properties']['fileName']
        FrameNumber1 = df['features'][i]['properties']['frameNumber']
        Date1 = df['features'][i]['properties']['processingDate']
        Year1 = Date1[0:4]
        Month1 = Date1[5:7]
        Day1 = Date1[8:10]
        Year1 = int(Year1)
        Month1 = int(Month1)
        Day1 = int(Day1)
        ProcessingDate1 = datetime.datetime(Year1,Month1,Day1)
        URL1 = df['features'][i]['properties']['url']
        for j in range(i+1,n):

            FlightDirection2 = df['features'][j]['properties']['flightDirection']
            PathNumber2 = df['features'][j]['properties']['pathNumber']
            # FileName2 = df['features'][j]['properties']['fileName']
            FrameNumber2 = df['features'][j]['properties']['frameNumber']
            Date2 = df['features'][j]['properties']['processingDate']
            Year2 = Date2[0:4]
            Month2 = Date2[5:7]
            Day2 = Date2[8:10]
            Year2 = int(Year2)
            Month2 = int(Month2)
            Day2 = int(Day2)
            ProcessingDate2 = datetime.datetime(Year2,Month2,Day2)
            diff = ProcessingDate2 - ProcessingDate1
            URL2 = df['features'][j]['properties']['url']
            #keep diff.days=12 or multiple of 12 as images in case of Sentinel-1 is generally avaiable at 12 days time gap
            if FlightDirection1==FlightDirection2 and PathNumber1==PathNumber2 and FrameNumber1==FrameNumber2 and ((diff.days==-12)or(diff.days==12)) :
                urls1.append(URL1)
                urls2.append(URL2)
                #Reminder-use your path everywhere
                asf.download_urls(urls=urls1, path='/home/Desktop/JDK/p1', session=session)
                asf.download_urls(urls=urls2, path='/home/Desktop/JDK/p2', session=session)


                for file in os.listdir('/home/Desktop/JDK/p1'):
                    if file.endswith(".zip"):
                        with ZipFile('/home/Desktop/JDK/p1/'+file, 'r') as zObject1:
                            zObject1.extractall(path='/home/harshit/Desktop/JDK/p1')
                        zObject1.close()
                        os.remove('/home/Desktop/JDK/p1/'+file)
                for file in os.listdir('/home/Desktop/JDK/p2'):
                    if file.endswith(".zip"):
                        with ZipFile('/home/Desktop/JDK/p2/'+file, 'r') as zObject2:
                            zObject2.extractall(path='/home/harshit/Desktop/JDK/p2')
                        zObject2.close()
                        os.remove('/home/Desktop/JDK/p2/'+file)
                # processing function call
                urls1.clear()
                urls2.clear() 

                outpath1 = ("/home/Desktop/JDK/p1")
                for file1 in os.listdir(outpath1):
                    print("file1")
                    p3 = ("/home/Desktop/JDK/p1/"+file1)


                outpath2 = ("/home/Desktop/JDK/p2")
                for file2 in os.listdir(outpath2):
                    print("file2")
                    p4 = ("/home/Desktop/JDK/p2/"+file2)


                product_t1 = read(p3)
                product_t2 = read(p4)

                date1 = str(Year1)+str(Month1)+str(Day1)+'_'+str(Year2)+str(Month2)+str(Day2)+'IW1'
                date2 = str(Year2)+str(Month2)+str(Day2)+'_'+str(Year1)+str(Month1)+str(Day1)+'IW2'
                date3 = str(Year2)+str(Month2)+str(Day2)+'_'+str(Year1)+str(Month1)+str(Day1)+'IW3'
                

                
                # Directory 
                directory = str(Year1)
    
                # Parent Directory path 
                parent_dir = "/home/Desktop/JDK/"

                # Path 
                path = os.path.join(parent_dir, directory) 

                # Create the directory 
                os.mkdir(path) 
                os.chdir(path)
                print("Directory '% s' created" % directory) 

                InSAR_pipeline_I(product_t1, product_t2,'IW1',1,9,date1) 
               
                outpath3=path
                for file4 in os.listdir(outpath3):
                    for file5 in os.listdir(outpath3):
                        if file4.endswith(".dim") and file5.endswith(".data"):
                           InSAR_pipeline_III(outpath3+'/'+file4,date1)
                           os.remove(outpath3+'/'+file4)
                           shutil.rmtree(outpath3+'/'+file5)
                        
                       
                        
                InSAR_pipeline_I(product_t1, product_t2,'IW2',1,9,date2) 
         
                outpath3=path
                for file6 in os.listdir(outpath3):
                    for file7 in os.listdir(outpath3):
                        if file6.endswith(".dim") and file7.endswith(".data"):
                           InSAR_pipeline_III(outpath3+'/'+file6,date2)
                           os.remove(outpath3+'/'+file6)
                           shutil.rmtree(outpath3+'/'+file7)
                        
                                                
                        
                InSAR_pipeline_I(product_t1, product_t2,'IW3',1,9,date3)      
                  
                outpath3=path
                for file8 in os.listdir(outpath3):
                    for file9 in os.listdir(outpath3):
                        if file8.endswith(".dim") and file9.endswith(".data"):
                           InSAR_pipeline_III(outpath3+'/'+file8,date3)
                           os.remove(outpath3+'/'+file8)
                           shutil.rmtree(outpath3+'/'+file9)
                                   

                for file5 in os.listdir('/home/Desktop/JDK/p1'):
                        os.remove('/home/Desktop/JDK/p1/'+file5)

                for file6 in os.listdir('/home/Desktop/JDK/p2'):
                        os.remove('/home/Desktop/JDK/p2/'+file6)

                boolean=True
                break
        if boolean==True:
            break








