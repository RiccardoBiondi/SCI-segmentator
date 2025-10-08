![](logo_scritta.svg)



| **Authors**  | **Project** |  **Build** |**License** |
|:------------:|:-----------:|:----------:|:----------:|
| [**R. Biondi**](https://github.com/RiccardoBiondi) </br> [**N. Biondini**](https://github.com/bionano94)| **SCI-Segmentation** |  **Ubuntu** : [![Ubuntu CI]()] | [![license](https://img.shields.io/github/license/mashape/apistatus.svg)](https://github.com/RiccardoBiondi/SCI-segmentator/blob/master/LICENSE.md) |

[![GitHub pull-requests](https://img.shields.io/github/issues-pr/RiccardoBiondi/SCI-segmentator.svg?style=plastic)](https://github.com/RiccardoBiondi/SCI-segmentator/pulls)
[![GitHub issues](https://img.shields.io/github/issues/RiccardoBiondi/SCI-segmentator.svg?style=plastic)](https://github.com/RiccardoBiondi/SCI-segmentator/issues)

[![GitHub stars](https://img.shields.io/github/stars/RiccardoBiondi/SCI-segmentator.svg?label=Stars&style=social)](https://github.com/RiccardoBiondi/SCI-segmentator/stargazers)
[![GitHub watchers](https://img.shields.io/github/watchers/RiccardoBiondi/SCI-segmentator.svg?label=Watch&style=social)](https://github.com/RiccardoBiondi/SCI-segmentator/watchers)
[![GitHub forks](https://img.shields.io/github/watchers/RiccardoBiondi/SCI-segmentator.svg?label=Forks&style=social)](https://github.com/RiccardoBiondi/SCI-segmentator/forks)

# Silent Cerebral Infarction Segmentator

- [Silent Cerebral Infarction Segmentator](#silent-cerebral-infarction-segemtator)
  - [Overview](#overview)
  - [Installation](#installation)
  - [Getting Started](#getting-started)
    - [Segmentation](#segmentation)
    - [Re-Training](#re-traning)
  - [License](#license)
  - [Contribute](#contribute)
  - [Authors](#authors)
  - [Citation](#citation)

## Overview

Sickle cell disease (SCD) is a hereditary hemoglobinopathy that leads to complications like ischemic stroke and neurocognitive decline.
Despite advances in care, silent cerebral infarcts (SCIs), remain prevalent, thus contributing to cognitive impairment and poor quality of life.
There is a lack of standardized guidelines for SCI screening, and real-world practices are suboptimal.

This study, held in the context of the GenoMed4All project, presents the adaptation of an existing White Matter Hyperintensities segmentation tool to construct a dataset from real-world, multi-center MRIs and an automated tool for SCI segmentation.
The segmentation was evaluated by Dice Coefficient and Volume Similarity.
SCI discrimination was evaluated using Balanced Accuracy and Dice Score.

The datasets consist of 79 MRIs of pediatric and adult patients from four different ERN-EurobloodNet centers, split into train and test.
27 MRIs (15 with and 12 without SCI) were collected from an additional center and constitute the external test set.
The discrimination performances between presence and absence of SCI shown a Balanced Accuracy of 0.77, and a Dice Coefficient of 0.86.
The median Dice similarities were 0.37 and 0.43 in internal and external test sets respectively.
The volume similarity of the identified lesions burden was 0.74 and 0.62 for the internal and external test set. 	
The study highlights the potential of deep learning in automating SCI segmentation even with limited and variable data. The proposed pipeline can be easily adapted to datasets from different clinical centers, offering an efficient, tailored solution for SCI identification in SCD patients.



## Installation

### Requirements

Berfore procedings with the installation, please ensure to have all the requirements satisfied: 

- working freesurfer instance. [here](https://surfer.nmr.mgh.harvard.edu/fswiki/DownloadAndInstall) the installation documentation.

- working conda installation, suggested [miniforge](https://github.com/conda-forge/miniforge), but any distribution should work.


### Installation Configuration

The first installation step, is the creation of a working [snakemake](https://snakemake.readthedocs.io/en/stable/) environment.
To do so, please run the following command from bash

```bash
conda create -c conda-forge -c bioconda -c nodefaults -n snakemake snakemake
```

Secondly,  download of the source code:

```bash
git clone https://github.com/RiccardoBiondi/SCI-segmentator
cd SCI-segmentator
```

Finally, download all the required fixtures (i.e. atlases and network weights).

```bash
./download_fixtures.sh
```
Now the software download and configuration is complete.

## Getting Started

The present code allow both the segmentation of SCI in MRIs and the fine tuning of network on your dataset.
The network is implemented using tensorflow, but GPU support is not required.
Specifically, the GPU support is disabled for the segmentation part, allowing parallel running of the different rules.
For the re-training step, the availability of GPU is suggested but not mandatory.

### Segmentation

The segmentation framework is fully automated by Snakemake.
Therefore, it requires a specific folder structure to automatically run.
Before starting the segmentation, please organize the images in a single directory for each study to segment. 
In each study directory, please put the FLAIR and the T1 sequences in `.nii.gz` format and named `FLAIR.nii.gz` and `T1W.nii.gz` respectively.
Here the full structure:
```
/path/to/study-1
    |
    |FLAIR.nii.gz
    |T1W.nii.gz
/path/to/study2
    !
    |FLAIR.nii.gz
    |T1W.nii.gz
```

Then, modify the `config.yaml` by adding the path to the each study folder to process under the `samples` field: 
```yaml
ensamble_0: "fixtures/volcanic-serenity-119/weights.h5"
ensamble_1: "fixtures/toasty-jazz-115/weights.h5"
ensamble_2: "fixtures/denim-flower-118/weights.h5"
ensamble_3: "fixtures/rare-galaxy-113/weights.h5"
ensamble_4: "fixtures/prime-terrain-112/weights.h5"

samples: [
  "/path/to/study-1",
  "/path/to/study-2"
]

activation_threshold: .2
```

Now you are ready to run the segmentation; all the results (final and intermediate) will be stored in the target study folder.

```bash
conda activate snakemake
snakemake -jN --use-conda --rerun-incomplete
```

where `N` indicates the number of process to run in parallel.

Please notice that the first run could take several time because of the creation of the conda environment and the freesurfer segmentation.

### Re-Traning


## Authors

<img src="https://avatars3.githubusercontent.com/u/48323959?s=400&v=4" style="width:25px; height:25px; border-radius:50%;"> **Riccardo Biondi** [github](https://github.com/RiccardoBiondi),  [unibo](https://www.unibo.it/sitoweb/riccardo.biondi7)

<img src="https://www.unibo.it/uniboweb/utils/UserImage.aspx?IdAnagrafica=863087&IdFoto=d16dc4d7" style="width:25px; height:25px; border-radius:50%;"> **Nicolas Biondini** [github](https://github.com/bionano94),  [unibo](https://www.unibo.it/sitoweb/nicolas.biondini2)

## Citation

If you have found this tool useful for your research, please consider citing the original paper.

```BibTeX
@misc{catopuma,
  author = {Biondi, Riccardo},
  title = {CATOPUMA - Customizable Advanced Tensorflow Objects to Preprocess, Upload, Model and Augment},
  year = {2023},
  publisher = {GitHub},
  howpublished = {\url{https://github.com/RiccardoBiondi/Catopuma}},
}

```
