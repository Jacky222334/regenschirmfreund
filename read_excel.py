import pandas as pd

# Path to the Excel file
excel_file = 'data/employees.xlsx'

def read_excel_file(file_path):
    # Read the Excel file
    df = pd.read_excel(file_path, engine='openpyxl')
    
    # Display the contents
    print('Contents of the Excel file:')
    print(df)

if __name__ == "__main__":
    read_excel_file(excel_file) 