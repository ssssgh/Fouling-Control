### Dependencies
```
numpy
matplotlib
pandas
Seaborn
```

### How to run the code
Preprocess the dataset by running 
```shell
python3 DataProcessing.py
```
Make sure `RAWdataforEdinburghMasters1.csv` and 
code are in the same path.

Ensure that you have preprocessed the dataset by
```shell
python3 DataProcessing.py
```
and then run the following.

```shell
python3 EDA.py
```
Here EDA will generate some relevant graphs

```shell
python3 Data Expand.py
```
Here Data Expand will use three extrapolation method.

### Ensure that you have run the Data Expand
Then run the following to get Qualitative & Quantitative result
```shell
python3 QualitativeQuantitative.py
```

### About Activity group code
You can choose any data you want to process when loading the data, 
and the code will generate three ship checklists according to 
the different activity groups of the data set.
```shell
python3 Activity group.py
```