"""
Script: queryLogs.py
v1 - 15/3/24
Author: Mark O'Kane
Purpose: Query a csv formatted log file from a cloud provider and return the count and percentage of total of the log severity types - ERROR, WARNING, INFO and no-severity
TO DO:
- check required modules are installed. if not, install them automatically
- rename existing output files, create backup dir and move timestamped old file(s) to it
- write log entries with no severity to a separate file
- perform analysis of NO SEVERITY log entries
"""

import csv
import os
import sys
import pandas as pd
import shutil
import subprocess

def check_arguments(file_name):
    """
    Check script has been called correctly. If not, return syntax for using it and exits.
    """
    if len(sys.argv) < 1:
        print(f"\nUsage: {file_name} [csv log file name]\n\nPlease provide the csv file name as an argument to this script.\n")
        sys.exit()
    
def check_file_exists(logfile_name):
    """
    Check source file to be queried exists. If not, exit with relevant error.
    """
    file_exists = os.path.exists(logfile_name)
    if not file_exists:
        print(f"File '{logfile_name}' not found.\n")
        sys.exit()
    
def check_file_csv(logfile_name):
    """
    Check source file to be queried is in csv format. If not, exit with relevant error.
    """
    chk_filetype = f"file '{logfile_name}'"
    file_type = subprocess.getoutput(chk_filetype)

    if "CSV text" not in file_type:
        print(f"*** '{logfile_name}' is not a csv formatted file.***\nExiting script.\n")
        sys.exit()

def rename_existing_files(logfile_name, results_out_file, no_sev_file):
    """
    Timestamp previously generated files containing move them to
    n backup folder
    """
    print(f"Timestamp previous output file '{logfile_name}'\n")
    print(f"Timestamp previous output file '{results_out_file}'\n")
    print(f"Timestamp previous output file '{no_sev_file}'\n")
    return None

def prompt_commas_removed(logfile_name):
    """
    Prompt user to ensure all ,'s have been removed from the csv. file before it is processed
    """
    top_and_bottom = "========================"
    console_width = shutil.get_terminal_size().columns
    centered_text = top_and_bottom.center(console_width)  
    print(centered_text)
    print(f"""
Before proceeding to use this script, you need to remove/replace ALL comma's from cells within the source csv file '{logfile_name}'. The script will return inaccurate results if this is not done first.\n
Open the file in your CSV editor of choice e.g. Libreoffice Calc (DO NOT USE A TEXT EDITOR) and do a global replace with nothing or the character of your choice.
""")
    print(centered_text,"\n")
    user_choice = input("Hit any key to continue with the script or 'n' to exit: ")
    
    if user_choice.lower() == "n":
        print(f"*** Exiting script. ***\n")
        sys.exit()
    else:
        print(f"\nContinuing....\n")

def count_rows_without_header(logfile_name):
    """
    Counts the total number of rows in the log CSV file excluding the header row.
    """
    total_rows = 0
    with open(logfile_name, 'r', newline='') as file:
        reader = csv.reader(file)
        next(reader)  # Skip the header row
        for row in reader:
            total_rows += 1
    return total_rows

def find_column_number(logfile_name, col_search_string):
    """
    Finds the column number where the specified string occurs in the CSV file.
    Returns None if the string is not found.
    """
    with open(logfile_name, 'r', newline='') as file:
        reader = csv.reader(file)
        header = next(reader)
        for i, column_name in enumerate(header):
            if column_name.strip() == col_search_string:
                return i
    return None

def calculate_percentage(part, total):
    """
    Calculates the percentage of part in relation to total.
    """
    return (part / total) * 100

def count_string_in_column(logfile_name, string_col_number, search_string_val, no_sev_file):
    """
    Counts occurrences each log severity in the specified column of a CSV 
    log file.
    """
    count = 0
    with open(logfile_name, 'r', newline='') as file:
        reader = csv.reader(file)
        for row in reader:
            if len(row) > string_col_number and row[string_col_number].strip() == search_string_val:
                count += 1
    return count

def print_results(csv_logfile, string_count, search_string, total_logs, percentage_of):
    print(f"There are {string_count} '{search_string}' log entries in file '{csv_logfile}'.")
    print(f"This is {percentage_of:.1f}% of the total log entries. \n")
    return None

def main():
    os.system('clear')

    # set Variables
    csv_logfile = 'test_logs.csv' # Replace with your CSV log file name
    search_column = 'Severity' # Define the severity column header name to search for
    log_file_out = 'logfile.log'
    results_out = 'results.txt'
    nosev_file = 'no_sev.csv' # Name of output file to store log entries with no defined Severity
       
    # Get the full path of the script
    script_path = os.path.abspath(__file__)
    # Extract the script name from the full path
    script_name = os.path.basename(script_path)

    # open script log file
    with open(log_file_out, "w") as file:
        file.write("This is a line written to the file.\n")
     
    # open results file
    with open(results_out, "w") as file:
        file.write("This is a line written to the file.\n")
    
    # open file to store no severity logs for future analysis file
    with open(nosev_file, "w") as file:
        file.write("This is a line written to the file.\n")
    
    # check user has included the csv file name to be checked.
    check_arguments(script_name)

    # check csv log file exists. If not, exit
    check_file_exists(csv_logfile)

    # check is a csv formatted file.  If not, exit
    check_file_csv(csv_logfile)

    # Prompt user to ensure all ","'s are removed from the csv log file"
    prompt_commas_removed(csv_logfile)
    
    #rename_existing_files(csv_logfile)
    rename_existing_files(log_file_out, results_out, nosev_file)
    
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
            string_count = count_string_in_column(csv_logfile, column_number, search_string, nosev_file)
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
