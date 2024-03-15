"""

Script: queryLogs.py
v1 - 15/3/24
Author: Mark O'Kane
Purpose: Query a .csv log file from a cloud provider and return the count and percentage of total of the log severity types - ERROR, WARNING, INFO and no-severity

"""

import csv
import os

os.system('clear')

def msg(msg_text):
    # generate msg to std output and log file
    print("->", msg_text, "\n")
    return None

def err_msg(err_text):
    # generate error to std output and log file
    print("**", err_text, "\n")

# Check script has been called correctly. If not, return syntax for use
def check_call():
    msg("Check script called correctly")
    return None
    
def prompt_commas_removed(csv_file):
    """
    Prompt user to ensure all ,'s have been removed from the csv. file before it is processed
    """
    
    print(f"Before proceeding to use this script, you need to remove/replace ALL comma's from cells within the source csv file '{csv_file}'. \nThe script will return inaccurate results if this is not done first.\n")
	#read -p "Have you done this? If so, hit enter to proceed or do so now.?  '# {search_string}' is in column number {column_number}.")
    return None

def check_file(csv_file):
    """
    check source file to be queried exists and is in csv format. If not,exit with relevant error.
    """
    print(f"Check source file '{csv_file}'exists\n")
    return None


def rename_existing_files(csv_file):
    """
    Timestamp previously generated reports and file containing no severity
    logs and move them to Archive folder
    """
    print(f"Timestamp previous output file '{csv_file}'\n")
    return None

def count_rows_without_header(csv_file):
    """
    Counts the total number of rows in the log CSV file excluding the header row.
    """
    total_rows = 0
    with open(csv_file, 'r', newline='') as file:
        reader = csv.reader(file)
        next(reader)  # Skip the header row
        for row in reader:
            total_rows += 1
    return total_rows

def calculate_percentage(part, total):
    """
    Calculates the percentage of part in relation to total.
    """
    return (part / total) * 100

def find_column_number(csv_file, search_string):
    """
    Finds the column number where the specified string occurs in the CSV file.
    Returns None if the string is not found.
    """
    with open(csv_file, 'r', newline='') as file:
        reader = csv.reader(file)
        header = next(reader)
        for i, column_name in enumerate(header):
            if column_name.strip() == search_string:
                return i
    return None

def count_string_in_column(csv_file, column_number, search_string):
    """
    Counts occurrences each log severity in the specified column of a CSV 
    log file.
    """
    count = 0
    with open(csv_file, 'r', newline='') as file:
        reader = csv.reader(file)
        for row in reader:
            if len(row) > column_number and row[column_number].strip() == search_string:
                count += 1
    return count

def print_results(csv_file, string_count, search_string, total_logs, percentage_of):
    print(f"There are {string_count} '{search_string}' log entries in file '{csv_file}'")
    print(f"This is {percentage_of:.2f}% of the total log entries \n")
    return None

def main():
    csv_file = 'test_logs.csv' # Replace with your CSV log file name
    search_column = 'Severity' # Define the severity column header name to search for
    check_call()
    #prompt_commas_removed(csv_file)
    #check_file(csv_file)
    #rename_existing_files(csv_file)
    total_logs = count_rows_without_header(csv_file)
    print(f"Total rows = {total_logs}\n")

    # Find column number
    column_number = find_column_number(csv_file, search_column)
    if column_number is not None:
        print(f"The column number of '{search_column}' is: {column_number}\n")
        
        # Count occurrences of each log severity type in the found column
        sev_list = ["ERROR", "WARNING","INFO", ""]
        for search_string in sev_list:
            string_count = count_string_in_column(csv_file, column_number, search_string)
            percentage_of = calculate_percentage(string_count, total_logs)
            if search_string != "":
                print_results(csv_file, string_count, search_string, total_logs, percentage_of)
            else:
                search_string = "NO SEVERITY"
                print_results(csv_file, string_count, search_string, total_logs, percentage_of)
    else:
        print(f"'{search_column}' not found in the CSV file.\n")

if __name__ == "__main__":
    main()
