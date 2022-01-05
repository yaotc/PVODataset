# POVDataset



PVOD has total 271,968 records and is constructed from two data sources with a 15-min interval, namely, Numerical Weather Prediction (NWP) from meteorological service and Local Measurements Data (LMD) from PV power stations. 

- NWP includes 7 features, i.e., global irradiance, direct irradiance, temperature, humidity, wind speed, wind direction, and pressure.
- Local Measurements Data includes 7 features, i.e., global irradiance, diffuse irradiance, temperature, pressure, wind direction, wind speed, and photovoltaic output records.


# Requirements

numpy==1.18.4

pandas==1.1.3

pvlib==0.8.1

pysolar==0.9

pytz==2018.9


# Citation

**Research Paper**:

Plain Text:

Yao, Tiechui, et al. "A photovoltaic power output dataset: Multi-source photovoltaic power output dataset with Python toolkit." Solar Energy 230 (2021): 122-130.

BibTeX:

@article{yao2021photovoltaic,
  title={A photovoltaic power output dataset: Multi-source photovoltaic power output dataset with Python toolkit},
  author={Yao, Tiechui and Wang, Jue and Wu, Haoyan and Zhang, Pei and Li, Shigang and Wang, Yangang and Chi, Xuebin and Shi, Min},
  journal={Solar Energy},
  volume={230},
  pages={122--130},
  year={2021},
  publisher={Elsevier}
  issn = {0038-092X},
  doi = {https://doi.org/10.1016/j.solener.2021.09.050},
  url = {https://www.sciencedirect.com/science/article/pii/S0038092X21008070}
}


URL:

https://www.sciencedirect.com/science/article/pii/S0038092X21008070

https://www.researchgate.net/publication/355389908_A_photovoltaic_power_output_dataset_Multi-source_photovoltaic_power_output_dataset_with_Python_toolkit


**Dataset**: 

Tiechui Yao; Jue Wang; Haoyan Wu; Pei Zhang; Shigang Li; Yangang Wang; Xuebin Chi; Min Shi. PVOD v1.0 : A photovoltaic power output dataset. (V4). 2021. Science Data Bank. 2021-08-24. doi:10.11922/sciencedb.01094; http://www.doi.org/10.11922/sciencedb.01094

URL: 

http://www.doi.org/10.11922/sciencedb.01094


# Getting support

If you have any questions relate to PVOD and code, please let us know. 

Email: yaotiechui@gmail.com

# License

MIT License.



# Demo: Pearson correlation between features 

![](./src/corr.png "Pearson correlation between features")