"""
Script: queryLogs.py
v1 - 15/3/24
Author: Mark O'Kane
Purpose: Query a csv formatted log file from a cloud provider and return the count and percentage of total of the log severity types - ERROR, WARNING, INFO and no-severity
TO DO:
- check required modules are installed. if not, install them automatically
- writing to log
- write log entries with no severity to a separate file
- perform analysis of NO SEVERITY log entries
"""

import csv
import os
import sys
import pandas as pd
import shutil
import subprocess
from datetime import datetime
import logging

# Configure logging to write to a file
log_file_out = 'logfile.log'
logging.basicConfig(filename=log_file_out, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Write log messages
"""
logging.debug('This is a debug message')
logging.info('This is an info message')
logging.warning('This is a warning message')
logging.error('This is an error message')
logging.critical('This is a critical message')
"""
#logging.info("New time stamped file name to be used is '%s'", tsed_file_name)


def check_arguments(file_name):
    """
    Check script has been called correctly. If not, return syntax for using it and exits.
    """
    if len(sys.argv) < 1:
        print(f"\nUsage: {file_name} [csv log file name]\n\nPlease provide the csv file name as an argument to this script.\n")
        logging.info("No argument provided with '%s'. Exited script", file_name)
        sys.exit()
    
def check_file_exists(csvlog_filename):
    """
    Check source file to be queried exists. If not, exit with relevant error.
    """
    file_exists = os.path.exists(csvlog_filename)
    if not file_exists:
        print(f"File '{csvlog_filename}' not found.\n")
        logging.info("File '%s' not found. Exited script", csvlog_filename)
        sys.exit()
    
def check_file_csv(csvlog_filename):
    """
    Check source file to be queried is in csv format. If not, exit with relevant error.
    """
    chk_filetype = f"file '{csvlog_filename}'"
    file_type = subprocess.getoutput(chk_filetype)

    if "CSV text" not in file_type:
        print(f"*** '{csvlog_filename}' is not a csv formatted file.***\nExiting script.\n")
        logging.info("'%s' is not a csv formatted file. Exited script", csvlog_filename)
        sys.exit()

def rename_existing_files(results_out_file, no_sev_file, backup_dir_name):
# def rename_existing_files(logfile_out, results_out_file, no_sev_file,backup_dir_name):
    """
    Timestamp previously generated files and move them to a backup folder
    """
    # create the timestamp
    current_timestamp = datetime.now()
    time_stamp = current_timestamp.strftime("%Y-%m-%d_%H:%M:%S")

    """"
    For each generated output file, check if they already exist.
    If they do, first check if the backup_dir_name exists. If it doesn't
    create it, append the timestamp to the file and move the file to
    the backup_dir_name.
    If the backup_dir_name does exist, append the timestamp to the file and move the file to the backup_dir_name
    """
    # for check_file in [logfile_out, results_out_file, no_sev_file]:
    for check_file in [results_out_file, no_sev_file]:
        if os.path.exists(check_file):
            
            # check if each generated file already exists
            logging.info("File '%s' already exists and will be time stamped and backed up", check_file)
            if os.path.isdir(backup_dir_name):
                """ if backup_dir_name already exists, timestamp the file and move it to the backup dir"""
                logging.info("Backup Dir '%s' already exists", backup_dir_name)
                
                # create the new time stamped name for the file
                tsed_file_name = check_file + "-" + time_stamp
                logging.info("New time stamped file name to be used is '%s'", tsed_file_name)
                
                # timestamp the file
                os.rename(check_file, tsed_file_name)
                logging.info("'%s' renamed to '%s'", check_file, tsed_file_name)
                
                # move the timestamped file to backup_dir_name 
                shutil.move(tsed_file_name, backup_dir_name)
                logging.info("Timestamped file '%s' moved to '%s'", tsed_file_name, backup_dir_name)
            else:
                """ If backup dir does not exist, create it, timestamp the file and move it to the backup_dir_name"""
                # create the backup dir
                os.makedirs(backup_dir_name)
                logging.info("Backup directory '%s' created", backup_dir_name)
                
                # create the new time stamped name for the file
                tsed_file_name = check_file + "-" + time_stamp
                logging.info("New time stamped file name to be used is '%s'", tsed_file_name)
                
                # timestamp the file
                os.rename(check_file, tsed_file_name)
                logging.info("'%s' renamed to '%s'", check_file, tsed_file_name)
                
                # move the timestamped file to backup_dir_name 
                shutil.move(tsed_file_name, backup_dir_name)
                logging.info("Timestamped file '%s' moved to '%s'", tsed_file_name, backup_dir_name)

def prompt_commas_removed(csvlog_filename):
    """
    Prompt user to ensure all ,'s have been removed from the csv. file before it is processed
    """
    top_and_bottom = "========================"
    # format the message on the terminal. First get it's width
    console_width = shutil.get_terminal_size().columns
    centered_text = top_and_bottom.center(console_width)  
    print(centered_text)
    print(f"""
Before proceeding to use this script, you need to remove/replace ALL comma's from cells within the source csv file '{csvlog_filename}'. The script will return inaccurate results if this is not done first.\n
Open the file in your CSV editor of choice e.g. Libreoffice Calc (DO NOT USE A TEXT EDITOR) and do a global replace with nothing or the character of your choice.
""")
    print(centered_text,"\n")
    user_choice = input("Hit any key to continue with the script or 'n' to exit: ")
    
    if user_choice.lower() == "n":
        print(f"\n*** Exiting script. ***\n")
        logging.info("User entered '%s'. Exiting script", user_choice)
        sys.exit()
    else:
        print(f"\nContinuing....\n")
        logging.info("User entered '%s'. Executing the script.", user_choice)

def create_new_output_files(results_out_file, no_sev_file):
    for file_names in [results_out_file, no_sev_file]:
        if not os.path.exists(file_names):
            with open(file_names, "w"):
                logging.info("File '%s' has been created for writing to later.", file_names)
                pass

def count_rows_without_header(csvlog_filename):
    """
    Counts the total number of rows in the log CSV file excluding the header row.
    """
    total_rows = 0
    with open(csvlog_filename, 'r', newline='') as file:
        reader = csv.reader(file)
        next(reader)  # Skip the header row
        for row in reader:
            total_rows += 1
    logging.info("Total number of rows is '%s'", total_rows)
    return total_rows

def find_column_number(csvlog_filename, col_search_string):
    """
    Finds the column number where the specified string occurs in the CSV file.
    Returns None if the string is not found.
    """
    with open(csvlog_filename, 'r', newline='') as file:
        reader = csv.reader(file)
        header = next(reader)
        for col_number, column_name in enumerate(header):
            if column_name.strip() == col_search_string:
                logging.info("The Severity column number is '%s'. Column numberings start at 0 (zero)", col_number)
                return col_number
    return None

def calculate_percentage(part, total):
    """
    Calculates the percentage of part in relation to total.
    """
    logging.info("Calculating percentage of '%s' as total of all log entries '%s'", part, total)
    return (part / total) * 100

def count_string_in_column(csvlog_filename, string_col_number, search_string_val):
    """
    Counts occurrences each log severity in the specified column of a CSV log file as well as those with no defined severity
    """
    logging.info("Counting number of occurrences for severity type '%s'", search_string_val)
    count = 0
    with open(csvlog_filename, 'r', newline='') as file:
        reader = csv.reader(file)
        for row in reader:
            if len(row) > string_col_number and row[string_col_number].strip() == search_string_val:
                count += 1
    logging.info("Total number of severity type '%s' is '%s'", search_string_val, count)
    return count

def print_results(csvlog_filename, string_count, search_string, total_logs, percentage_of):
    print(f"There are {string_count} '{search_string}' log entries in file '{csvlog_filename}'.")
    print(f"This is {percentage_of:.1f}% of the total log entries of '{total_logs}'. \n")

def print_to_log(results_out_file, csvlog_filename, string_count, search_string, total_logs, percentage_of):  
    # write to the results file
    with open(results_out_file, "a") as file1:
        logging.info("Results file '%s' has been opened for writing to.", results_out_file)
        file1.write("There are " + str(string_count) + " Severity type '" + search_string + "' entries in the file '" + csvlog_filename + "'.\n")
        #file1.write("This is " + str(percentage_of:.1f) + " of the total log entries of " + total_logs + "in the file\n")
        file1.close()
        logging.info("Results file '%s' has been closed.", results_out_file)
    return None

def main():
    os.system('clear')

    # set Variables
    csv_logfile = 'test_logs.csv' # Replace with your CSV log file name
    search_column = 'Severity' # Define the severity column header name to search for
    
    results_out = 'results.txt'
    nosev_file = 'no_sev.csv' # Name of output file to store log entries with no defined Severity
    backup_dir = 'Backup'
       
    # Get the full path of the script
    script_path = os.path.abspath(__file__)
    # Extract the script name from the full path
    script_name = os.path.basename(script_path)
    
    # check user has included the csv file name to be checked.
    check_arguments(script_name)

    # check csv log file exists. If not, exit
    check_file_exists(csv_logfile)

    # check is a csv formatted file.  If not, exit
    check_file_csv(csv_logfile)

    # Prompt user to ensure all ","'s are removed from the csv log file"
    prompt_commas_removed(csv_logfile)
    
    #rename_existing_files(csv_logfile)
    #rename_existing_files(log_file_out, results_out, nosev_file,backup_dir)
    rename_existing_files(results_out, nosev_file,backup_dir)

    # create new output files for appending info to
    create_new_output_files(results_out, nosev_file)
    
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
            #string_count = count_string_in_column(csv_logfile, column_number, search_string, nosev_file)
            string_count = count_string_in_column(csv_logfile, column_number, search_string)

            percentage_of = calculate_percentage(string_count, total_logs)
            if search_string != "":
                print_results(csv_logfile, string_count, search_string, total_logs, percentage_of)
                print_to_log(results_out, csv_logfile, string_count, search_string, total_logs, percentage_of)
            else:
                # added this to so I can print "No Severity" in the results message
                search_string = "with no defined severity"
                print_results(csv_logfile, string_count, search_string, total_logs, percentage_of)
                print_to_log(results_out, csv_logfile, string_count, search_string, total_logs, percentage_of)
    else:
        print(f"'{search_column}' not found in the CSV log file.\n")
  
    print(f"Script has successfully finished running. Results have been written to the file '{results_out}' and log entries with no defined severity have been written to '{nosev_file}'")

if __name__ == "__main__":
    main()
