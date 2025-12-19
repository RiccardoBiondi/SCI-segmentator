import os
import itk
import logging
import argparse
from typing import List, Tuple
import FreeSimpleGUI as sg

#from gui.panels.popups import PopupProgressBar


def _read_dicom_study(folder: str, logger=logging):

    ImageType = itk.Image[itk.F, 3]
    logging.info(f"Parsing DICOM Series in {folder}")
    namesGenerator = itk.GDCMSeriesFileNames.New()
    namesGenerator.SetUseSeriesDetails(True)
    namesGenerator.AddSeriesRestriction("0008|0021")
    namesGenerator.SetGlobalWarningDisplay(False)
    namesGenerator.SetDirectory(folder)

    dicomIO = itk.GDCMImageIO.New()
    dicomIO.LoadPrivateTagsOn()
    reader = itk.ImageSeriesReader[ImageType].New()
    reader.SetImageIO(dicomIO)
    
    seriesUIDs = namesGenerator.GetSeriesUIDs()
    
    logging.info(f"Found a total of {len(seriesUIDs)} unique series")
    images = []
    metadatas = []


    #with PopupProgressBar(bar_max=len(seriesUIDs), title="Loading DICOM Series", text="Loaded Series") as pb:
    for i, seriesUID in enumerate(seriesUIDs):
        
        logging.info(f"Loading Series {seriesUID}")
        sg.one_line_progress_meter("Loading DICOM Series", i+1, len(seriesUIDs))
        
        try:
            UIDsFileNames = namesGenerator.GetFileNames(seriesUID)
            reader = itk.ImageSeriesReader[ImageType].New()
            reader.SetImageIO(dicomIO)
            reader.SetFileNames(UIDsFileNames)
            _ = reader.Update()
            images.append(reader.GetOutput())
            metadata = dicomIO.GetMetaDataDictionary()
            
            metadatas.append({k: metadata[k] for k in metadata.GetKeys()})
        except Exception as e:
            logger.error(e)

    return images, metadatas


# Patient Name (‘0010’, ‘0010’)
# Patient ID (‘0010’, ‘0020’)
# Patient Sex (‘0010’, ‘0040’)
# Series Description (0008,103E)
# Modality 0008|0060
# Series Number 0020|0011

if __name__ == "__main__":
    

    parser = argparse.ArgumentParser(description="")

    _ = parser.add_argument(
        "-in",
        "--input",
        dest="input",
        action="store",
        type=str,
        required=True,
        help=""
    )

    args = parser.parse_args()


    _read_dicom_study(args.input)