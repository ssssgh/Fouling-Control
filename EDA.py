import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load the data from the uploaded CSV file
data = pd.read_csv('interpolated_dataset.csv')
activity_groups = ['0-30%', '31-60%', '61-100%']

plt.figure(figsize=(10, 6))

sns.boxplot(x='Pass/Fail', y='Performance Metric', data=data)
plt.title('Distribution of Performance Metric by Pass/Fail')
plt.xlabel('Fail/Pass')
plt.ylabel('Performance Metric')

min_value_0 = data[data['Pass/Fail'] == 0]['Performance Metric'].min()
max_value_1 = data[data['Pass/Fail'] == 1]['Performance Metric'].max()

plt.text(0, min_value_0, f'{min_value_0}', va='center', ha='center', backgroundcolor='w')
plt.text(1, max_value_1, f'{max_value_1}', va='center', ha='center', backgroundcolor='w')
plt.savefig('./plot/PMthresold.jpg', format='jpg')



plt.figure(figsize=(16, 15))

for index, group in enumerate(activity_groups, 1):
    plt.subplot(3, 1, index)
    sns.boxplot(x='Product Code', y='Performance Metric', data=data[data['Activity Group'] == group], order=data['Product Code'].value_counts().index)
    plt.title(f'Distribution of Performance Metric by Product Code for Activity Group: {group}')
    plt.xticks(rotation=45)
    plt.tight_layout()

plt.savefig('./plot/productcomp.jpg', format='jpg') 



plt.figure(figsize=(18, 10))
grouped_data = data[data['Scheme Group'].isin(['0-36', '37-60'])]
grouped_data = grouped_data[grouped_data['Activity Group'].isin(['0-30%', '31-60%', '61-100%'])]
# Looping through each activity group to create separate box plots
for index, activity in enumerate(activity_groups, 1):
    plt.subplot(1, 3, index)
    
    # Filtering the data for the current activity group
    subset = grouped_data[grouped_data['Activity Group'] == activity]
    
    # Plotting the box plot
    ax = sns.boxplot(x="Scheme Group", y="Performance Metric", data=subset, palette="viridis", boxprops=dict(alpha=.7))
    
    # Calculating mean values
    means = subset.groupby("Scheme Group")["Performance Metric"].mean().values
    
    # Annotating the mean values on the plot
    for i, mean_val in enumerate(means):
        ax.text(i, mean_val + 1, f"{mean_val:.2f}", horizontalalignment='center', color='black', weight='bold')
    
    plt.title(f"Distribution for Activity Group: {activity}")
    plt.ylabel("Performance Metric")
    if index != 1:
        plt.ylabel("")

plt.tight_layout()
plt.suptitle("Comparison of Performance Metric by Scheme Group for Each Activity Group (with Mean Values)", y=1.05)
plt.savefig('./plot/PMACSCE.jpg', format='jpg')