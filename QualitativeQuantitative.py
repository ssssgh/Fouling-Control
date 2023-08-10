from scipy.stats import norm
import pandas as pd
import numpy as np

data = pd.read_csv('complete expand.csv')

def qualitative_ranking(value):
    """Assign a qualitative ranking based on the pass rate value."""
    if value >= 75:
        return "Best"
    elif 60 <= value < 75:
        return "Better"
    elif 50 <= value < 60:
        return "Good"
    else:
        return "Lower"

def format_cell(value):
    """Format the cell to include both the qualitative ranking and the pass rate."""
    if pd.notnull(value):
        # Extract the numeric part of the pass rate
        numeric_value = float(value[:-1])
        return f"{qualitative_ranking(numeric_value)} ({value})"
    return value

def create_pivot_table(data, activity_group):
    # Calculate mean and sample size
    pivot = data[data['Activity Group'] == activity_group].pivot_table(
        index='Product Code',
        columns='Route Number',
        values='Pass/Fail',
        aggfunc='mean'
    ) * 100  # Convert to percentage
    
    pivot = pivot.applymap(lambda x: "{:.2f}%".format(x) if pd.notnull(x) else None)

    pivot_count = data[data['Activity Group'] == activity_group].pivot_table(
        index='Product Code',
        columns='Route Number',
        values='Pass/Fail',
        aggfunc='count',
    )

    mask_zero_count = pivot_count == 0
    
    # Apply the masks
    pivot[mask_zero_count] = None

    return pivot

# Define a function to calculate the B value
def calculate_B(n, N, sigma, alpha=0.1):
    z = norm.ppf(1 - alpha / 2)
    h = np.sqrt((((N * sigma**2) / n) - sigma**2) / (N - 1))
    B = z * h
    return B,h

# Create a function to apply on the groupby objects
def calculate_interval(df,product_code):
    if pd.isnull(df).all():  # Skip if all values are NaN
        return np.nan, np.nan
    mu = df.mean()
    sigma = df.std()
    n = len(df)
    N = len(data[data['Product Code'] == product_code])
    B,h = calculate_B(n, N, sigma)
    interval = '[{}, {}]'.format(round(mu - B, 2), round(mu + B, 2))
    return B, interval,h,sigma


# Define the activity groups to be considered
activity_groups = ['0-30%', '31-60%', '61-100%']
products_to_consider = ['a', 'f', 'g', 'i', 'k', 'm', 'n', 'o', 'q', 'r', 's']

# List to store results of each activity group
all_results = []

# Iterate over the defined activity groups
for activity_group in activity_groups:
    # Filter data for the current activity group
    grouped_data_current = data[data['Activity Group'] == activity_group].groupby(['Product Code', 'Route Number'])
    # Update N for the current activity group
    N = len(data[data['Activity Group'] == activity_group])
    
    # Create a list to store results for the current activity group
    results_current_list = []
    
    # Iterate over the groups in the groupby object
    for name, group in grouped_data_current:
        # Calculate the confidence interval
        
        B, interval, h, sigma = calculate_interval(group['Performance Metric'],name[0])
        
        # Calculate mean
        u = group['Performance Metric'].mean()
        
        # Add the results to the list
        results_current_list.append({'Activity Group': activity_group,
                                     'Product Code': name[0],
                                     'Route Number': name[1],
                                     'Mean': u,
                                     'B Value': B,
                                     'Confidence Interval': interval})
    
    # Convert the list to a DataFrame and append to the all_results list
    results_current_df = pd.DataFrame(results_current_list)
    all_results.append(results_current_df)

# Concatenate results of all activity groups
final_results = pd.concat(all_results, ignore_index=True)

final_results.to_csv('CI.csv', index=True)

# Filter the results DataFrame to include only the selected products
filtered_final_results = final_results[final_results['Product Code'].isin(products_to_consider)]
filtered_data_required = data[data['Product Code'].isin(products_to_consider)]

# Create pivot tables for each activity group for the filtered results

pivot_tables_filtered = {}
pivot_tables = {}

for activity_group in activity_groups:

    pivot_required = create_pivot_table(filtered_data_required, activity_group)
    pivot_tables[activity_group] = pivot_required
    pivot_tables[activity_group] = pivot_tables[activity_group].applymap(format_cell)

    pivot = filtered_final_results[filtered_final_results['Activity Group'] == activity_group].pivot(index='Product Code', 
                                                                                                   columns='Route Number', 
                                                                                                   values='Mean')
    pivot = round(pivot,2)
    pivot_B = filtered_final_results[filtered_final_results['Activity Group'] == activity_group].pivot(index='Product Code', 
                                                                                                         columns='Route Number', 
                                                                                                         values='B Value')
    pivot_B = round(pivot_B,2)
    pivot_interval = filtered_final_results[filtered_final_results['Activity Group'] == activity_group].pivot(index='Product Code', 
                                                                                                            columns='Route Number', 
                                                                                                            values='Confidence Interval')
    # Concatenate mean and confidence interval for each cell
    pivot_combined = pivot_tables[activity_group] + '\n' + pivot.astype(str) + "±" + pivot_B.astype(str) + '\n' + pivot_interval
    pivot_tables_filtered[activity_group] = pivot_combined


pivot_tables_filtered['0-30%'].to_csv('CIPS0-30.csv',index = True)
pivot_tables_filtered['31-60%'].to_csv('CIPS31-60.csv',index = True)
pivot_tables_filtered['61-100%'].to_csv('CIPS61-100.csv',index = True)
