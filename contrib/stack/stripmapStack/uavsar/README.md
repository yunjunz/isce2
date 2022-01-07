## Processing multiple UAVSAR segments 

UAVSAR may acquire a flight line into segments. These segments can be concatenated and processed as a single interferogram. Adaptations to ISCE were made to ease these task. To run these scripts, setup the path as below:

```bash
export PATH=${PATH}:${ISCE_STACK}/stripmapStack:${ISCE_STACK}/stripmapStack/uavsar
```

1. Create an project directory and download the SLC stack from UAVSAR website using the provided batch wget commands:

```bash
mkdir SanAndreasUav09015; cd SanAndreasUav09015
mkdir download; cd download
# run the batch wget commands to download files in the download folder
mv *.dop ..
```

2. Generate image.json file using the script  group_segments_dayhrmin_4isce.py and indicating the location of the folder where the SLC’s are located:

```bash
group_seg.py download/ > images.json
```

3. Unpack the UAVSAR segments into two folders, one per segment:

```bash
prepUAVSAR_coregStack_seg.py -i download/ -d *.dop -o download/SLC_seg1 -s 1
prepUAVSAR_coregStack_seg.py -i download/ -d *.dop -o download/SLC_seg2 -s 2
prepUAVSAR_coregStack_seg.py -i download/ -d *.dop -o download/SLC_seg3 -s 3
```

4. After preparing both segments, a concatenation process is computed to form a merged SLC.

```bash
mergeSegments_UAVSAR.py -w ./ -s download/SLC_seg1 -o SLC
```

5. Once the segments are connected, compute interferograms normally.  

```bash
crossmul.py -s SLC/ -a 12 -r 3 -n 3 -o Igrams
```

### To-do list suggestions

We should merge step 2-4 above all into one script, `prepUAVSAR_coregStack.py`. And support `prepUAVSAR_coregStack.py -s all` to handle the multiple segments scenario [concatenating]. To this end, here is my suggestions flow inside `prepUAVSAR_coregStack.py`:

For single segment [same as the current version on isce-framework/isce-2]:
+ move and rename .slc file
+ generate shelve file
+ generate XML file

For multiple segments [-s all] or [-s 1 2 3] or [-s 1 2] or ...:
+ generate the `images.json` file by merging `group_seg.py` into a sub-function inside prep*.py
+ concatenate the .slc file from the download folder [there is no need to change the location before this]
+ generate/update the shelve file
+ generate XML file

To achive this:
+ `prepUAVSAR_coregStack_seg.py` should be merged into `prepUAVSAR_coregStack.py`.
+ `mergeSegments_UAVSAR.py` should be merged into `prepUAVSAR_coregStack.py`
+ One should be able to turn ON or OFF the `YYYYMMDDTHHMM` convention, via a command line option. This option by default should be ON if there are multiple acquisitions within one date in the dataset and be OFF in the other cases.
