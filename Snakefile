import os

configfile: "./config.yaml"


paths = list(map(lambda x: os.path.dirname(x), config["samples"]))
samples = list(map(lambda x: os.path.basename(x), config["samples"]))

rule all:
    input:
        in0 = expand(os.path.join("{subjdir}", "{sample}", "sci_segmentation.nii.gz"), zip, subjdir=paths, sample=samples)

# Post-processing: compute features from the segmentation and select

rule select_lesions:
    input:
        am_ =  os.path.join("{subjdir}", "{sample}", "combined_activation_map_onto_flair.nii.gz"),
        ft_ =  os.path.join("{subjdir}", "{sample}", "features.csv")
    output:
        out_ = os.path.join("{subjdir}", "{sample}", "sci_segmentation.nii.gz")
    conda:
        "./conda_env/scd_itk.yaml"
    params:
        at_ = config["activation_threshold"]
    shell:
        "python sci_segmentator/apply_postprocessing.py -in='{input.am_}' -ft='{input.ft_}' -at='{params.at_}' -out='{output.out_}'"

rule extract_features:
    input:
        am_ = os.path.join("{subjdir}", "{sample}", "combined_activation_map_onto_flair.nii.gz"),
        ex_ = os.path.join("{subjdir}", "{sample}", "exclusion_region_onto_flair.nii.gz"),
        wm_ = os.path.join("{subjdir}", "{sample}", "wm_mask_onto_flair.nii.gz")
    output:
        out_ = os.path.join("{subjdir}", "{sample}", "features.csv")
    conda:
        "./conda_env/scd_itk.yaml"
    params:
        at_ = config["activation_threshold"]
    shell:
        "python sci_segmentator/extract_features.py -in='{input.am_}' -ex='{input.ex_}' -wm='{input.wm_}' -at='{params.at_}' -out='{output.out_}'"

# combine all the segmentation and remap it on to the FLAIR space
rule remap_average_activation_map:
    input:
        am_ =  os.path.join("{subjdir}", "{sample}", "combined_activation_map.nii.gz"),
        fl_ =  os.path.join("{subjdir}", "{sample}", "FLAIR_RAS.nii.gz")
    output:
        out_ =  os.path.join("{subjdir}", "{sample}", "combined_activation_map_onto_flair.nii.gz")
    conda:
        "./conda_env/scd_itk.yaml"
    shell:
        "python  sci_segmentator/resample_onto_reference.py -in='{input.am_}' -ref='{input.fl_}' -out='{output.out_}' -c"


rule combina_activation_maps:
    input:
        am0_ = os.path.join("{subjdir}", "{sample}", "predict_element_0.nii.gz"),
        am1_ = os.path.join("{subjdir}", "{sample}", "predict_element_1.nii.gz"),
        am2_ = os.path.join("{subjdir}", "{sample}", "predict_element_2.nii.gz"),
        am3_ = os.path.join("{subjdir}", "{sample}", "predict_element_3.nii.gz"),
        am4_ = os.path.join("{subjdir}", "{sample}", "predict_element_4.nii.gz")
    output:
        out_ = os.path.join("{subjdir}", "{sample}", "combined_activation_map.nii.gz")
    conda:
        "./conda_env/scd_itk.yaml"
    shell:
        "python sci_segmentator/combine_activation_maps.py -am '{input.am0_}' -am '{input.am1_}' -am '{input.am2_}' -am '{input.am3_}'  -am '{input.am4_}' -out '{output.out_}'"


# Now, it is possible to start the segmentations from the different ensambles.
rule predict_w4:
    input:
        in_ = os.path.join("{subjdir}", "{sample}", "FLAIR_RES.nii.gz")
    output:
        out_ = os.path.join("{subjdir}", "{sample}", "predict_element_4.nii.gz")
    params:
        w_ = config["ensamble_4"]
    conda:
        "./conda_env/scd_itk.yaml"
    shell:
        "python sci_segmentator/predict.py -in '{input.in_}' -out '{output.out_}' -w '{params.w_}'"


rule predict_w3:
    input:
        in_ = os.path.join("{subjdir}", "{sample}", "FLAIR_RES.nii.gz")
    output:
        out_ = os.path.join("{subjdir}", "{sample}", "predict_element_3.nii.gz")
    params:
        w_ = config["ensamble_3"]
    conda:
        "./conda_env/scd_itk.yaml"
    shell:
        "python sci_segmentator/predict.py -in '{input.in_}' -out '{output.out_}' -w '{params.w_}'"


rule predict_w2:
    input:
        in_ = os.path.join("{subjdir}", "{sample}", "FLAIR_RES.nii.gz")
    output:
        out_ = os.path.join("{subjdir}", "{sample}", "predict_element_2.nii.gz")
    params:
        w_ = config["ensamble_2"]
    conda:
        "./conda_env/scd_itk.yaml"
    shell:
        "python sci_segmentator/predict.py -in '{input.in_}' -out '{output.out_}' -w '{params.w_}'"



rule predict_w1:
    input:
        in_ = os.path.join("{subjdir}", "{sample}", "FLAIR_RES.nii.gz")
    output:
        out_ = os.path.join("{subjdir}", "{sample}", "predict_element_1.nii.gz")
    params:
        w_ = config["ensamble_1"]
    conda:
        "./conda_env/scd_itk.yaml"
    shell:
        "python sci_segmentator/predict.py -in '{input.in_}' -out '{output.out_}' -w '{params.w_}'"


rule predict_w0:
    input:
        in_ = os.path.join("{subjdir}", "{sample}", "FLAIR_RES.nii.gz")
    output:
        out_ = os.path.join("{subjdir}", "{sample}", "predict_element_0.nii.gz")
    params:
        w_ = config["ensamble_0"]
    conda:
        "./conda_env/scd_itk.yaml"
    shell:
        "python sci_segmentator/predict.py -in '{input.in_}' -out '{output.out_}' -w '{params.w_}'"

#
# Cropping and Normalization
# Now the GL of the FLAIR image are normalized 
#
rule resample_flair_to_isotropic_size:
    input:
        in_ = os.path.join("{subjdir}", "{sample}", "FLAIR_CP.nii.gz")
    output:
        out_ = os.path.join("{subjdir}", "{sample}", "FLAIR_RES.nii.gz")
    conda:
        "./conda_env/scd_itk.yaml"
    shell:
        "python sci_segmentator/resample.py -in '{input.in_}' -out '{output.out_}'"

rule crop_flair_around_brain:
    input:
        in_ = os.path.join("{subjdir}", "{sample}", "FLAIR_normalized.nii.gz"),
        ms_ = os.path.join("{subjdir}", "{sample}", "HEADontoFLAIR.nii.gz")
    output:
        out_ = os.path.join("{subjdir}", "{sample}", "FLAIR_CP.nii.gz")
    conda:
        "./conda_env/scd_itk.yaml"
    shell:
        "python sci_segmentator/crop.py -in '{input.in_}' -ms '{input.ms_}' -out '{output.out_}'"


rule normalize_flair_gray_level:
    input:
        in_ = os.path.join("{subjdir}", "{sample}", "FLAIR_N4.nii.gz"),
        ms_ = os.path.join("{subjdir}", "{sample}", "HEADontoFLAIR.nii.gz")
    output:
        out_ = os.path.join("{subjdir}", "{sample}", "FLAIR_normalized.nii.gz")
    conda:
        "./conda_env/scd_itk.yaml"
    shell:
        "python sci_segmentator/normalize.py -in '{input.in_}' -ms '{input.ms_}' -out '{output.out_}'"
#
# Co-Registration and Mapping
# Register T1W onto FLAIR and apply the transform onto the head, exclusion region and wm 
# labels estimated from T1W image
#

rule map_wm_region_onto_flair:
    input:
        in_ = os.path.join("{subjdir}", "{sample}", "wm_mask_onto_t1.nii.gz"),
        t0_ = os.path.join("{subjdir}", "{sample}", "t1_onto_flair_transform_0.txt"),
        t1_ = os.path.join("{subjdir}", "{sample}", "t1_onto_flair_transform_1.txt")
    output:
        out_ = os.path.join("{subjdir}", "{sample}", "wm_mask_onto_flair.nii.gz")
    conda:
        "./conda_env/scd_itk.yaml"
    shell:
        "python sci_segmentator/apply_transforms.py -in '{input.in_}' -tr '{input.t0_}' -tr '{input.t1_}' -out '{output.out_}' -b"
    

rule map_excusion_region_onto_flair:
    input:
        in_ = os.path.join("{subjdir}", "{sample}", "exclusion_region_onto_t1.nii.gz"),
        t0_ = os.path.join("{subjdir}", "{sample}", "t1_onto_flair_transform_0.txt"),
        t1_ = os.path.join("{subjdir}", "{sample}", "t1_onto_flair_transform_1.txt")
    output:
        out_ = os.path.join("{subjdir}", "{sample}", "exclusion_region_onto_flair.nii.gz")
    conda:
        "./conda_env/scd_itk.yaml"
    shell:
        "python sci_segmentator/apply_transforms.py -in '{input.in_}' -tr '{input.t0_}' -tr '{input.t1_}' -out '{output.out_}' -b"


rule map_head_region_onto_flair:
    input:
        in_ = os.path.join("{subjdir}", "{sample}", "HEADontoT1W.nii.gz"),
        t0_ = os.path.join("{subjdir}", "{sample}", "t1_onto_flair_transform_0.txt"),
        t1_ = os.path.join("{subjdir}", "{sample}", "t1_onto_flair_transform_1.txt")
    output:
        out_ = os.path.join("{subjdir}", "{sample}", "HEADontoFLAIR.nii.gz")
    conda:
        "./conda_env/scd_itk.yaml"
    shell:
        "python sci_segmentator/apply_transforms.py -in '{input.in_}' -tr '{input.t0_}' -tr '{input.t1_}' -out '{output.out_}' -b"


rule register_t1_onto_flair:
    input:
        t1_ = os.path.join("{subjdir}", "{sample}", "T1W_N4.nii.gz"),
        fl_ = os.path.join("{subjdir}", "{sample}", "FLAIR_N4.nii.gz")
    output:
        t0_ = os.path.join("{subjdir}", "{sample}", "t1_onto_flair_transform_0.txt"),
        t1_ = os.path.join("{subjdir}", "{sample}", "t1_onto_flair_transform_1.txt"),
        out_ = os.path.join("{subjdir}", "{sample}", "T1W_onto_FLAIR.nii.gz")
    params:
        pr_ = os.path.join("{subjdir}", "{sample}", "t1_onto_flair_transform")
    conda:
        "./conda_env/scd_itk.yaml"
    shell:
        "python sci_segmentator/scan_registration.py -in '{input.t1_}' -ref  '{input.fl_}' -ot '{params.pr_}' -out '{output.out_}' -t 'rigid' -t 'affine'"

#
# The second step of the pre-processing, is the creation of required mask for
# both the pre and post processing. 
# The created masks are: Head, White matter and Exclusion region
# The masks as well as the t1 image will be further registered on the FLAIR scan 
#
rule select_white_matter_labels:
    input: 
        in_ = os.path.join("{subjdir}", "{sample}",  "aseg.nii.gz")
    output:
        out = os.path.join("{subjdir}", "{sample}",'wm_mask_onto_t1.nii.gz')
    params:
        label_1 =  2, # Left-Cerebral-White-Matter     
        label_2 = 41, # Right-Cerebral-White-Matter    
        label_3 = 77 # WM-hypointensities              
    conda:
        "./conda_env/scd_itk.yaml" 
    shell:
        "python sci_segmentator/label_selector.py -in='{input.in_}' -out='{output.out}' -lb '{params.label_1}' -lb '{params.label_2}' -lb '{params.label_3}'"


rule mgz_to_nii:
    input: 
        in_ = os.path.join("{subjdir}", "{sample}", "-".join(["{sample}", "wm-freesurfer"]), "mri", "aseg.auto.mgz")
    output:
        out_ = os.path.join("{subjdir}", "{sample}", "aseg.nii.gz")
    shell:
        "mri_convert '{input.in_}' '{output.out_}'"


rule compute_white_matter_mask:
    input:
        in_ = os.path.join("{subjdir}", "{sample}", "T1W_N4.nii.gz")
    output:
        out_ = os.path.join("{subjdir}", "{sample}", "-".join(["{sample}", "wm-freesurfer"]), "mri", "aseg.auto.mgz")
    params:
        sdir = os.path.join("{subjdir}", "{sample}"),
        sid = "-".join(["{sample}", "wm-freesurfer"])
    shell:
        "recon-all -s '{params.sid}' -sd '{params.sdir}' -i '{input.in_}' -autorecon1 -autorecon2" #&& mv '{params.sdir}'/'{params.sid}'/mri/aseg.auto.mgz '{params.sdir}'/aseg.auto.mgz"

rule apply_transform_to_exclusion_region_mask:
    input:
        tr0_ = os.path.join("{subjdir}", "{sample}", "atlas_onto_t1_transforms_0.txt"),
        tr1_ = os.path.join("{subjdir}", "{sample}", "atlas_onto_t1_transforms_1.txt"),
        tr2_ = os.path.join("{subjdir}", "{sample}", "atlas_onto_t1_transforms_2.txt"),
        in_ = "fixtures/MNI152_Exclusion_Region.nii"
    output:
        out_ = os.path.join("{subjdir}", "{sample}", "exclusion_region_onto_t1.nii.gz")
    conda:
        "./conda_env/scd_itk.yaml"
    shell:
        "python sci_segmentator/apply_transforms.py -in '{input.in_}' -tr '{input.tr0_}' -tr '{input.tr1_}' -tr '{input.tr2_}' -out '{output.out_}' -b"

rule register_mni_atlas_onto_t1:
    input:
        in_ = os.path.join("{subjdir}", "{sample}", "T1W_N4.nii.gz"),
        at_ = "./fixtures/MNI152_T1_1mm.nii.gz"
    output:
        tr0_ = os.path.join("{subjdir}", "{sample}", "atlas_onto_t1_transforms_0.txt"),
        tr1_ = os.path.join("{subjdir}", "{sample}", "atlas_onto_t1_transforms_1.txt"),
        tr2_ = os.path.join("{subjdir}", "{sample}", "atlas_onto_t1_transforms_2.txt")
    params:
        pr_ = os.path.join("{subjdir}", "{sample}", "atlas_onto_t1_transforms")

    conda:
        "./conda_env/scd_itk.yaml"
    shell:
        "python sci_segmentator/scan_registration.py -in '{input.at_}' -ref  '{input.in_}' -ot '{params.pr_}' -t 'rigid' -t 'affine' -t 'bspline'"


rule compute_head_mask:
    input:
        in_ = os.path.join("{subjdir}", "{sample}", "T1W_N4.nii.gz")
    output:
        out_ = os.path.join("{subjdir}", "{sample}", "HEADontoT1W.nii.gz")
    conda:
        "./conda_env/scd_itk.yaml"
    shell:
        "python ./sci_segmentator/compute_head_region.py -in '{input.in_}' -out '{output.out_}'"

#
# Here the first step of the preprocessing.
# A bias field correction is performed on both FLAIR and T1W images.
# The corrected scan will be used as input for all the subsequent processing fases.
#

rule t1_bias_field_correction:
    input:
        in_ = os.path.join("{subjdir}", "{sample}", "T1W_RAS.nii.gz")
    output:
        out_ = os.path.join("{subjdir}", "{sample}", "T1W_N4.nii.gz")
    conda:
        "./conda_env/scd_itk.yaml"
    shell:
        "python ./sci_segmentator/bias_field_correction.py -in '{input.in_}' -out '{output.out_}'"


rule flair_bias_field_correction:
    input:
        in_ = os.path.join("{subjdir}", "{sample}", "FLAIR_RAS.nii.gz")
    output:
        out_ = os.path.join("{subjdir}", "{sample}", "FLAIR_N4.nii.gz")
    conda:
        "./conda_env/scd_itk.yaml"
    shell:
        "python ./sci_segmentator/bias_field_correction.py -in '{input.in_}' -out '{output.out_}'"



#
# The first step is to ensure the RAS (Right, Anterior, Superior ) orientation
# for both T1W and FLAIR scan. This ensure correct processing in subsequent pipeline steps.
#

rule flair_to_RAS:
    input:
        in_ = os.path.join("{subjdir}", "{sample}", "FLAIR.nii")
    output:
        out_ = os.path.join("{subjdir}", "{sample}", "FLAIR_RAS.nii.gz")
    conda:
        "./conda_env/scd_itk.yaml"
    shell:
        "python ./sci_segmentator/scan_ras_orienter.py -in '{input.in_}' -out '{output.out_}'"


rule t1_to_RAS:
    input:
        in_ = os.path.join("{subjdir}", "{sample}", "T1W.nii")
    output:
        out_ = os.path.join("{subjdir}", "{sample}", "T1W_RAS.nii.gz")
    conda:
        "./conda_env/scd_itk.yaml"
    shell:
        "python ./sci_segmentator/scan_ras_orienter.py -in '{input.in_}' -out '{output.out_}'"