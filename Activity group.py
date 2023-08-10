import pandas as pd

# Load the data
data = pd.read_csv('complete expand.csv')

# Groups based on Activity Group
group_0_30 = data[data['Activity Group'] == '0-30%']
group_31_60 = data[data['Activity Group'] == '31-60%']
group_61_100 = data[data['Activity Group'] == '61-100%']

# Rows and columns

rows = pd.Index(['a', 'f', 'g', 'i', 'k', 'm', 'n', 'o', 'q', 'r', 's'], name='Product')
columns = pd.Index([1, 2, 3, 4, 5, 6, 7, 8, 9], name='Route')
# Initialize the tables
table_0_30 = pd.DataFrame(index=rows, columns=columns)
table_31_60 = pd.DataFrame(index=rows, columns=columns)
table_61_100 = pd.DataFrame(index=rows, columns=columns)

# Function to populate tables
def populate_table(group, table):
    for row in rows:
        for column in columns:
            count = len(group[(group['Route Number'] == column) & (group['Product Code'] == row)])
            table.loc[row, column] = count

# Populate tables
populate_table(group_0_30, table_0_30)
populate_table(group_31_60, table_31_60)
populate_table(group_61_100, table_61_100)

# Save tables to CSV

table_0_30.to_csv('0-30.csv', index=True)
table_31_60.to_csv('31-60.csv', index=True)
table_61_100.to_csv('61-100.csv', index=True)
