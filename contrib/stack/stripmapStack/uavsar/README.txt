Processing multiple UAVSAR segments 
UAVSAR may acquire a flight line into segments. These segments can be concatenated and processed as a single interferogram. Adaptations to ISCE were made to ease these task. The following scripts will be used:

prepareUAVSAR_coregStack_segmets.py
unpackFrame_UAVSAR_segments.py
uavsar_concatenate_slc.py
uavsar_update_shelve.py

Copy the scripts listed above, located within the isce_uavsar folder into the following ISCE directory:

$ISCE_HOME/share/stripmapStack 

An additional script located within the UAVSARpythoncode (section 2.4) folder will be used to generate basic metadata grouping. This script can be placed at any desired location, however placing it in a folder together with the JPL UAVSAR processing algorithm would be best. 

group_segments_dayhrmin_4isce.py 
 
1. Generate image.json file using the script  group_segments_dayhrmin_4isce.py and indicating the location of the folder where the SLC’s are located:

python3 group_seg.py download/ > images.json ↵
 
2. Unpack the UAVSAR segments into two folders, one per segment:

prepareUAVSAR_coregStack_segments.py -i download/ -d eterre_08705_02_BU.dop -o SLC_seg1 -s 1 ↵
prepareUAVSAR_coregStack_segments.py -i download/ -d eterre_08705_02_BU.dop -o SLC_seg2 -s 2 ↵

3. After preparing both segments, a concatenation process is computed to form a merged SLC.
 
uavsar_concatenate_slc.py -w ./ -s1 SLC_seg1 -o SLC_merged ↵
 
4. Once the segments are connected, compute interferograms normally.  

python3 /usr/local/opt/isce/share/stripmapStack/crossmul_uavsar.py -s SLC_merged/ -a 12 -r 3 -n 3 -o Igrams ↵
