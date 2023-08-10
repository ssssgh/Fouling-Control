import pandas as pd
import numpy as np

# Load the data
data = pd.read_csv('interpolated_dataset.csv')

# Rename the 'Unnamed: 0' column to an empty string
data.rename(columns={'Unnamed: 0': ''}, inplace=True)
data_use = data[data['Scheme Group'] == '37-60']

# Function to expand data based on the activity group
def expand_data_by_activity_group(original_data, source_group, target_group):
    expanded_data = original_data.copy()
    copied_data_storage = pd.DataFrame(columns=original_data.columns)
    source_data = original_data[original_data['Activity Group'] == source_group]
    
    for route in original_data['Route Number'].unique():
        for product_code in original_data['Product Code'].unique():
            target_data_count = len(expanded_data[(expanded_data['Activity Group'] == target_group) &
                                                  (expanded_data['Route Number'] == route) &
                                                  (expanded_data['Product Code'] == product_code)])
            source_data_count = len(source_data[(source_data['Route Number'] == route) & 
                                                (source_data['Product Code'] == product_code)])
            
            # If data in the target group is less than data in the source group for a specific route and product code
            if target_data_count == 0:
                if target_data_count < source_data_count:              
                    # Copy data from the source group
                    copied_data = source_data[(source_data['Route Number'] == route) &
                                              (source_data['Product Code'] == product_code)].copy()
                    # Change the activity group of the copied data to the target group
                    copied_data['Activity Group'] = target_group
                    copied_data_storage = pd.concat([copied_data_storage, copied_data])

    return copied_data_storage

# Expand the data based on the activity groups
activity_data_31_60 = expand_data_by_activity_group(data_use, '0-30%', '31-60%')

activity_data_61_100 = expand_data_by_activity_group(data_use, '31-60%', '61-100%')

transition_expanded_data = pd.concat([data_use,activity_data_31_60])
F_expanded_data = pd.concat([transition_expanded_data,activity_data_61_100])
print(F_expanded_data.shape)
F_expanded_data.to_csv('Activity_expand.csv', index=False)

# by time
# First, filter the original data for 'Scheme Group' as '0-36'
scheme_0_36_data = data[data['Scheme Group'] == '0-36']

# Create an empty DataFrame to store the copied data
copied_data_storage = pd.DataFrame(columns=data.columns)

# Iterate over the unique values of 'Activity Group', 'Route Number', and 'Product Code' in the expanded data
for activity_group in F_expanded_data['Activity Group'].unique():
    for route in F_expanded_data['Route Number'].unique():
        for product_code in F_expanded_data['Product Code'].unique():
            # Get the count of rows for the current combination in the expanded data
            expanded_data = F_expanded_data[(F_expanded_data['Activity Group'] == activity_group) &
                                                (F_expanded_data['Route Number'] == route) &
                                                (F_expanded_data['Product Code'] == product_code)].copy()
            # If the count is less than 10
            if len(expanded_data) < 10:
                # Find the matching rows in the '0-36' data
                matching_rows = scheme_0_36_data[(scheme_0_36_data['Activity Group'] == activity_group) &
                                                (scheme_0_36_data['Route Number'] == route) &
                                                (scheme_0_36_data['Product Code'] == product_code)].copy()
                if len(matching_rows) > 0:
                    if len(expanded_data) == 0:
                    # Change the 'Scheme Group' of the matching rows to '37-60'
                        matching_rows['Scheme Group'] = '37-60'
                    else:
                        original_mean = expanded_data['Performance Metric'].mean()
                        alternative_mean = matching_rows['Performance Metric'].mean()
                        adjust_value = original_mean - alternative_mean
                        matching_rows['Performance Metric'] = matching_rows['Performance Metric'] + adjust_value
                        matching_rows['Performance Metric'] = matching_rows['Performance Metric'].clip(0, 100)
                        matching_rows['Performance Metric'] = matching_rows['Performance Metric'].round(2)
                        matching_rows['Pass/Fail'] = matching_rows['Performance Metric'].apply(lambda x: 0 if x > 10 else 1)
                        matching_rows['Scheme Group'] = '37-60'
                    copied_data_storage = pd.concat([copied_data_storage, matching_rows])

# Concatenate the copied data with the expanded data
time_data = pd.concat([F_expanded_data, copied_data_storage])
print(time_data.shape)
time_data.to_csv('time_expand.csv', index=False)


# by product
# Define rules for product expansion
expansion_rules = {
    'i': [],
    'o': ['f'],
    'm': ['a'],
    'h': ['c']
}

# Function to expand data bidirectionally within the same route and activity group
def bidirectional_expand(original_data, product_to_change, products_to_reference):
    expanded_data = original_data.copy()
    
    for route in original_data['Route Number'].unique():
        for activity_group in original_data['Activity Group'].unique():
            # For the special case of products 'i', 'd', and 'b'
            if product_to_change == 'i':
                d_data = original_data[(original_data['Product Code'] == 'd') & 
                                        (original_data['Route Number'] == route) &
                                        (original_data['Activity Group'] == activity_group)]
                if len(d_data) >= 1:
                    products_to_reference = ['d']
                else:
                    products_to_reference = ['b']

            for product in [product_to_change] + products_to_reference:
                # Check if there are enough data points for the product within the group
                product_data = original_data[(original_data['Product Code'] == product) & 
                                             (original_data['Route Number'] == route) &
                                             (original_data['Activity Group'] == activity_group)]
                
                if len(product_data) < 10:
                    # List of potential products to copy from
                    potential_references = [product_to_change] + products_to_reference
                    potential_references.remove(product)  # Remove the current product from the list
                    
                    for product_to_reference in potential_references:
                        # Check if there are enough data points for the product to reference within the group
                        reference_data = original_data[(original_data['Product Code'] == product_to_reference) & 
                                                       (original_data['Route Number'] == route) &
                                                       (original_data['Activity Group'] == activity_group)]
                        if len(reference_data) >= 1:
                            # Copy the data points
                            copied_data = reference_data.copy()
                            # Change the product code
                            copied_data['Product Code'] = product
                            #copied_data['Scheme Group'] = '37-60'
                            # Append the copied data to the expanded data
                            expanded_data = pd.concat([expanded_data, copied_data])
                            break
                        
    return expanded_data

# Apply the bidirectional expansion function for each product
bidirectional_expanded_data = time_data.copy()
for product_to_change, products_to_reference in expansion_rules.items():
    bidirectional_expanded_data = bidirectional_expand(bidirectional_expanded_data, product_to_change, products_to_reference)

product_relationships = {
    'a': ['n'],
    'c':['l'],
    'f': ['c', 'h', 'l'],
    'g': ['s'],
    'h':['l'],
    'i': ['k'],
    'k': ['i','d'],
    'm': ['n'],
    'n': ['a', 'm', 'q'],
    'o': ['c', 'h', 'l'],
    'q': ['n'],
    's': ['p', 'g'],
}
additional_data_storage = pd.DataFrame(columns=data.columns)

product_data = bidirectional_expanded_data[bidirectional_expanded_data['Product Code'].isin(['a', 'f', 'g', 'i', 'k', 'm', 'n', 'o', 'q', 's'])]

prodata = bidirectional_expanded_data.copy()
for activity_group in product_data['Activity Group'].unique():
    for route in product_data['Route Number'].unique():
        for product_code in product_data['Product Code'].unique():
            group_noted = product_data[(product_data['Activity Group'] == activity_group) &
                                    (product_data['Route Number'] == route) &
                                    (product_data['Product Code'] == product_code)].copy()
            if len(group_noted) < 10:
                matching_rows = scheme_0_36_data[(scheme_0_36_data['Activity Group'] == activity_group) &
                                        (scheme_0_36_data['Route Number'] == route) &
                                        (scheme_0_36_data['Product Code'] == product_code)].copy()
                if len(matching_rows) > 0:
                    current_mean = matching_rows['Performance Metric'].mean()

                    related_products = product_relationships.get(product_code, [])
                    for related_product in related_products:
                    # Get the matching rows from the scheme data
                        matching_rows_alternative = scheme_0_36_data[(scheme_0_36_data['Activity Group'] == activity_group) &
                                                                     (scheme_0_36_data['Route Number'] == route) &
                                                                    (scheme_0_36_data['Product Code'] == related_product)].copy()
                        if len(matching_rows_alternative) > 0:
                            # Calculate the mean of the performance metric for the matching rows
                            matching_mean = matching_rows_alternative['Performance Metric'].mean()
                            # Calculate the adjustment value
                            adjustment_value = current_mean - matching_mean
                            # Adjust the performance metric of the matching rows
                            matching_rows_change = time_data[(time_data['Activity Group'] == activity_group) &
                                                                (time_data['Route Number'] == route) &
                                                                (time_data['Product Code'] == related_product)].copy()
                            if len(matching_rows_change) > 0:
                                matching_rows_change['Performance Metric'] = matching_rows_change['Performance Metric'] + adjustment_value
                                matching_rows_change['Performance Metric'] = matching_rows_change['Performance Metric'].clip(0, 100)
                                matching_rows_change['Performance Metric'] = pd.to_numeric(matching_rows_change['Performance Metric'], errors='coerce')
                                matching_rows_change['Performance Metric'] = matching_rows_change['Performance Metric'].round(2)
                                matching_rows_change['Pass/Fail'] = matching_rows_change['Performance Metric'].apply(lambda x: 0 if x > 10 else 1)
                                # Change the product   
                                matching_rows_change['Product Code'] = product_code
                                additional_data_storage = pd.concat([additional_data_storage, matching_rows_change])

# Concatenate the additional data with the current dataset
expanded_time_data_final = pd.concat([bidirectional_expanded_data, additional_data_storage])
expanded_time_data_final.to_csv('complete expand.csv', index=False)
print(expanded_time_data_final.shape)