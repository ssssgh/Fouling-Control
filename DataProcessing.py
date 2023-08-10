import pandas as pd

data = pd.read_csv('RAWdataforEdinburghMasters1.csv')

mean_scheme = data.groupby(['Vessel Group','Scheme Group', 'Activity Group','Route Number'])['Scheme'].mean()

mean_scheme = mean_scheme.round()

for index, row in data.iterrows():
    if pd.isna(row['Scheme']):
        Vessel_Group = row['Vessel Group']
        scheme_group = row['Scheme Group']
        Activity_Group = row['Activity Group']
        Route_Numer = row['Route Number']
        data.loc[index, 'Scheme'] = mean_scheme[Vessel_Group,scheme_group, Activity_Group,Route_Numer]

data = data[data['Scheme'] <= 60]

mean_in_service_period = data.groupby(['Vessel Group','Scheme Group', 'Activity Group','Route Number'])['In Service Period'].mean()
mean_activity = data.groupby(['Vessel Group','Scheme Group','Route Number'])['% Activity'].mean()

for index, row in data.iterrows():
    if pd.isna(row['In Service Period']):
        Vessel_Group = row['Vessel Group']
        scheme_group = row['Scheme Group']
        Activity_Group = row['Activity Group']
        Route_Numer = row['Route Number']
        data.loc[index, 'In Service Period'] = mean_in_service_period[Vessel_Group,scheme_group, Activity_Group,Route_Numer]

    if pd.isna(row['% Activity']):
        Vessel_Group = row['Vessel Group']
        scheme_group = row['Scheme Group']
        Route_Numer = row['Route Number']
        data.loc[index, '% Activity'] = mean_activity[Vessel_Group,scheme_group,Route_Numer]
data['Activity Group'] = pd.cut(data['% Activity'], bins=[0, 30.1, 60.1, 100], labels=['0-30%', '31-60%', '61-100%'], right=False) 

data_without_columns = data.drop(columns=['Unnamed: 0', 'Performance Metric', 'Unique Identifier'])
# Sort the data by 'Performance Metric' in ascending order so that the smallest values come first
data_sorted = data.sort_values(by='Performance Metric')

# Drop duplicates based on all columns except 'Performance Metric', 'Unnamed: 0', and 'Unique Identifier'
# This way, for each group of duplicates, only the first row (with the smallest 'Performance Metric') will be kept
cleaned_data = data_sorted.drop_duplicates(subset=data_without_columns.columns.tolist(), keep='first')
sorted_cleaned_data = cleaned_data.sort_values(by='Unnamed: 0')
sorted_cleaned_data.rename(columns={'Unnamed: 0': ''}, inplace=True)
sorted_cleaned_data.to_csv('interpolated_dataset.csv', index=False)

