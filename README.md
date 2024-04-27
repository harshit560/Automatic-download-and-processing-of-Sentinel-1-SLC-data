# Automatic-download-and-processing-of-Sentinel-1-SLC-data
This code downloads and does InSAR processing on Sentinel-1 data using snappy. 
Installing snappy can be difficult, use the steps explained in the link below- 
https://senbox.atlassian.net/wiki/spaces/SNAP/pages/50855941/Configure+Python+to+use+the+SNAP-Python+snappy+interface+SNAP+versions+9

Check forums and other sources in case you face difficulty downloading snappy in your system.

What code does- 
Downloads S1 SLC pair using user input of time duration and .shp of your AOI then processes and IW 1,2 and 3 all at once and generate InSAR coherence and other products depending upon your use.

