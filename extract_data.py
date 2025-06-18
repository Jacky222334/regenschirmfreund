import pandas as pd

# Load the CSV data
csv_file = 'data/employees.csv'
excel_file = 'data/employees.xlsx'

def convert_csv_to_excel(csv_path, excel_path):
    # Read the CSV file
    df = pd.read_csv(csv_path)
    
    # Write to Excel file
    df.to_excel(excel_path, index=False, engine='openpyxl')
    print(f'Converted {csv_path} to {excel_path}')

if __name__ == "__main__":
    convert_csv_to_excel(csv_file, excel_file) 