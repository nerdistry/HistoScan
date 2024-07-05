<h1 align="center">
  <br>
    <img src="./images/histoscan-logo.png" alt="HistoScan Image" width="200">
  <br>
  HistoScan
  <br>
</h1>

<div align="center">
    <img src="https://img.shields.io/badge/JavaScript-F7DF1E.svg?style=for-the-badge&logo=javascript&logoColor=black" alt="JavaScript" style="border-radius: 50%;">
    <img src="https://img.shields.io/badge/Vue.js-4FC08D.svg?style=for-the-badge&logo=vue.js&logoColor=white" alt="Vue.js" style="border-radius: 50%;">
    <img src="https://img.shields.io/badge/Jupyter-F37626.svg?style=for-the-badge&logo=jupyter&logoColor=white" alt="Jupyter Notebook" style="border-radius: 50%;">
    <img src="https://img.shields.io/badge/ResNet-0071C5.svg?style=for-the-badge&logo=resnet&logoColor=white" alt="ResNet" style="border-radius: 50%;">
    <img src="https://img.shields.io/badge/PyTorch-EE4C2C.svg?style=for-the-badge&logo=pytorch&logoColor=white" alt="PyTorch" style="border-radius: 50%;">
</div>

## Overview

The api overview is explained below

```text
                                                                                                                                                                                                                                                                                                                     
 ┌──────────────────┐        ┌──────────────────┐     ┌─────────────────────────────────────────────┐                            
 │                  │        │                  │     │                                             │                            
 │                  │        │                  │     │                                             │                            
 │    IMAGE         │        │   Torch Model    │     │  {                                          │                            
 │    Served Via    ├───────►│                  ├─────┤      "prediction": "No Cancer Detected",    │                            
 │    REST API      │        │   1->Cancer      │     │      "probability": 0.10497161746025085     │                            
 │                  │        │   0 -> No cancer │     │  }                                          │                            
 │                  │        │                  │     │                                             │                            
 │                  │        │                  │     │                                             │                            
 └──────────────────┘        └──────────────────┘     └─────────────────────────────────────────────┘                                 
```


An image undergoes the following transofrmations to output
Normalization uses `mean=[0.485, 0.456, 0.406]` and `std=[0.229, 0.224, 0.225]` (similar to the Resnet Model)

```text
                                                                                                               
   ┌────────────────┐            ┌──────────────┐         ┌───────────────────┐       ┌─────────────────┐        
   │                │            │              │         │                   │       │                 │        
   │                │            │  TRANSFORM   │         │  PRETRAINED       │       │                 │        
   │  IMAGE         │            │ - RESIZE (256)         │  MODEL            │       │  OUTPUT         │        
   │                ├───────────►│              ┌─────────► - BASE (RESNET24) │       │                 │        
   │                │            │ - TOTENSOR() │         │                   │       │                 │        
   │                │            │ - NORMALIZE  │         │                   ├───────►                 │        
   │                │            │              │         │                   │       │                 │        
   └────────────────┘            └──────────────┘         └───────────────────┘       └─────────────────┘            
```

## Model Architecture

The model base is a pretrained resnet34 model from [Deep Residual Learning for Image Recognition](https://arxiv.org/abs/1512.03385)

Resnet is a `Residual Learning Framework`, instead of optimizing weights that fit an underlying mapping, we optimize residual coefficients explain fit the same mapping.


Reason: 
  1.  won the 1st place in the ILSVRC2015 classification competition. 

  2. 1st places on: ImageNet detection, ImageNet localization,
  3. 1st place COCO detection, and COCO segmentation in ILSVRC &COCO 2015 competitions


The architecture doesn't suffer from degradation problem present in deep plain neural nets, but actually gains more accuracy with more layers