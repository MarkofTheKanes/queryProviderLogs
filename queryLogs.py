"""
Script: queryLogs.py
v1 - 15/3/24
Author: Mark O'Kane
Purpose: Query a .csv log file from a cloud provider and return the count and percentage of total of the log severity types - ERROR, WARNING, INFO and no-severity
TO DO:
- check is a csv formatted file - using pandas not working
- output to std output and also to log file at same time
    - rename existing output files
    - create backup dir and move timestamped old files to it
- write log entries with no severity to a separate file
- perform analysis of these NO SEVERITY log entries
"""

import csv
import os
import sys
import pandas as pd
import shutil

def msg(msg_text):
    # generate msg to std output and log file
    print("->", msg_text, "\n")
    return None

def err_msg(err_text):
    # generate error to std output and log file
    print("***", err_text, "***\n")

def check_arguments(script_name):
    """
    Check script has been called correctly. If not, return syntax for using it
    """
    if len(sys.argv) < 2:
        print(f"\nUsage: {script_name} [csv file name]\n\nPlease provide the csv file name as an argument to this script.\n")
        sys.exit()
    else:
        return True
    
def prompt_commas_removed(csv_logfile):
    """
    Prompt user to ensure all ,'s have been removed from the csv. file before it is processed
    """
    top_and_bottom = "========================"
    console_width = shutil.get_terminal_size().columns
    centered_text = top_and_bottom.center(console_width)  
    print(centered_text)
    print(f"""
Before proceeding to use this script, you need to remove/replace ALL comma's from cells within the source csv file '{csv_logfile}'. The script will return inaccurate results if this is not done first.\n
Open the file in Excel or Libreoffice Calc and do a global replace with nothing or the character of your choice.\n
DO NOT EDIT IT IN A TEXT EDITOR.
""")
    print(centered_text,"\n")
    user_choice = input("Hit any key to continue with the script or 'n' to exit: ")
    
    if user_choice.lower() == "n":
        err_msg("Exiting script.")
        sys.exit()
    else:
        msg("Continuing....\n")

def check_file_exists(csv_logfile):
    """
    check source file to be queried exists. If not, exit with relevant error.
    """
    file_exists = os.path.exists(csv_logfile)
    if not file_exists:
        print(f"File '{csv_logfile}' not found.\n")
        sys.exit()
    else:
        #print(f"File '{csv_logfile}' found.\n")
        return True    
    
def check_file_csv(csv_logfile):
    """
    TO DO check source file to be queried is in csv format. If not,exit with relevant error. using pandas does not work for some reason
    """
    #msg("hello")
    # Open the file in 'r' mode
    try:
        pd.read_csv(csv_logfile)
        return True
    except pd.errors.ParserError:
        return False

def rename_existing_files(csv_logfile):
    """
    Timestamp previously generated reports and file containing no severity
    logs and move them to Archive folder
    """
    print(f"Timestamp previous output file '{csv_logfile}'\n")
    return None

def count_rows_without_header(csv_logfile):
    """
    Counts the total number of rows in the log CSV file excluding the header row.
    """
    total_rows = 0
    with open(csv_logfile, 'r', newline='') as file:
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

def find_column_number(csv_logfile, search_string):
    """
    Finds the column number where the specified string occurs in the CSV file.
    Returns None if the string is not found.
    """
    with open(csv_logfile, 'r', newline='') as file:
        reader = csv.reader(file)
        header = next(reader)
        for i, column_name in enumerate(header):
            if column_name.strip() == search_string:
                return i
    return None

def count_string_in_column(csv_logfile, column_number, search_string):
    """
    Counts occurrences each log severity in the specified column of a CSV 
    log file.
    """
    count = 0
    with open(csv_logfile, 'r', newline='') as file:
        reader = csv.reader(file)
        for row in reader:
            if len(row) > column_number and row[column_number].strip() == search_string:
                count += 1
    return count

def print_results(csv_logfile, string_count, search_string, total_logs, percentage_of):
    print(f"There are {string_count} '{search_string}' log entries in file '{csv_logfile}'.")
    print(f"This is {percentage_of:.2f}% of the total log entries. \n")
    return None

def main():
    os.system('clear')

    csv_logfile = 'test_logs.csv' # Replace with your CSV log file name
    search_column = 'Severity' # Define the severity column header name to search for
       
    # Get the full path of the script
    script_path = os.path.abspath(__file__)
    # Extract the script name from the full path
    script_name = os.path.basename(script_path)
    
    # check user has included the csv file name to be checked.
    check_arguments(script_name)

    # check file exists. If not, exit
    check_file_exists(csv_logfile)

    # check is a csv formatted file.  If not, exit
    #check_file_csv(csv_logfile)

    # Prompt user to ensure all ","'s are removed from the csv log file"
    prompt_commas_removed(csv_logfile)
    
    #rename_existing_files(csv_logfile)
    
    # required in order to calculate percentages
    total_logs = count_rows_without_header(csv_logfile)

    # Find column number
    column_number = find_column_number(csv_logfile, search_column)
    if column_number is not None:       
        """
        Count the number of occurrences of each log SEVERITY type in the found column as well as those with NO SEVERITY
        """
        sev_list = ["ERROR", "WARNING","INFO", ""]
        for search_string in sev_list:
            string_count = count_string_in_column(csv_logfile, column_number, search_string)
            percentage_of = calculate_percentage(string_count, total_logs)
            if search_string != "":
                print_results(csv_logfile, string_count, search_string, total_logs, percentage_of)
            else:
                # added this to so I can print "No Severity" in the results message
                search_string = "NO SEVERITY"
                print_results(csv_logfile, string_count, search_string, total_logs, percentage_of)
    else:
        print(f"'{search_column}' not found in the CSV log file.\n")

if __name__ == "__main__":
    main()
