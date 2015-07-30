=================================
PyAnUtils: Physics Analysis Utils
=================================
Container of utilities to do pysics analysis. It includes generic
software to do plots, make useful functions, etc; as well as more 
specific ATLAS/CMS oriented.                                      
                                                                  
author: Jordi Duarte-Campderros (Nov.2014)                        
email : jorge.duarte.campderros@cern                              


INSTALLATION
----------------
The package provides a (Distutils) 'setup.py' to build and install it. Just 
```bash
  % python setup.py install [--user] 
```
The --user option is used when you don't have root privilegies (or you 
don't want to install the package in the global site-packages directories). 
The package will be installed inside of the user directory '$HOME/.local'. 
You have to modify the enviroment variables: 
```bash
  % export PYTHONPATH=$PYTHONPATH:$HOME/.local/lib
  % export PATH=$PATH:$HOME/.local/bin
```
in order to use the new scripts and modules.

CONTENT
-------
  1. Modules
  ----------
   * PyAnUtils.plotsytyles:    ROOT styles 
   * PyAnUtils.pyanfunctions:  bunch of functions
   * PyAnUtils.histocontainer: helper class to plot histograms
   * jobSender: [Subpackage]   bunch of classes, functions and scripts related 
                               with sending jobs to a scientific cluster
   * dvAnUtils: [Subpackage]   software specific for the displaced vertex
                               ATLAS' analysis
   * mtgAnUtils:[Subpackge]    software specific for the Muon Spectrometer
                               Geometry ATLAS' analysis

  2. Scripts
  ------------
   * mtgfastfullcmp: plot and show differences between Full (G4) and Fast
   simulation in the MuonTrackingGeometry ATLAS's package
   * lazycmt:        compiles, config and clean ATLAS packages automaticaly
   * dvtrigeff:      ---

Use *help* function for detailed information of each module and script.
 
