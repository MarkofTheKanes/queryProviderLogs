"""
Script: ParseExport.py
v1 - 20/8/24
Author: Mark O'Kane
Purpose: Parse rows from an exported feed csv file to a separate csv file based on their status
TO DO:
- check required modules are installed. if not, install them automatically
- write a wrapper to call this for >1 csv log files to be analysed
"""
import importlib.util
import subprocess
import sys
import logging
import csv
import platform
import os
import shutil
from datetime import datetime
import importlib.util

def check_and_install_modules(modules):
    """
    Checks if the required Python modules are installed. If not, it attempts to install them.

    :param modules: A list of module names (as strings) to check.
    """
    for module in modules:
        try:
            # Try to import the module
            importlib.import_module(module)
            print(f"> Module '{module}' is already installed.")
        except ImportError:
            # If the module is not found, try to install it
            print(f"*** Module '{module}' is not installed. Attempting to install...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", module])
            try:
                # Verify the installation
                importlib.import_module(module)
                print(f"> Module '{module}' was successfully installed.")
            except ImportError:
                print(f"** Failed to install module '{module}'.")

# Configure logging to write to a file
log_file_out = 'logfile.log'
logging.basicConfig(filename=log_file_out, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def clear_screen():
    current_os = platform.system()
    
    if current_os == "Windows":
        # Run Windows-specific command
        os.system("cls")  # Example: lists directory contents
    elif current_os == "Linux" or current_os == "Darwin":
        # Run Linux or macOS-specific command
        os.system("clear")  # Example: lists directory contents
    else:
        print(f"Unsupported OS: {current_os}")


def check_arguments(file_name):
    """
    Check script has been called correctly. If not, return syntax for using it and exits.
    """
    if len(sys.argv) < 2:
        print(f"\nUsage: {file_name} [source export feed filename]\n\nPlease provide the file name as an argument to this script. Exited script\n")
        logging.info("No argument provided with '%s'. Exited script", file_name)
        sys.exit()
    else:
        srcexport_filename = sys.argv[1]
        return srcexport_filename

def check_file_exists(src_filename):
    """
    Check source file to be queried exists. If not, exit with relevant error.
    """
    file_exists = os.path.exists(src_filename)
    if not file_exists:
        print(f"> File '{src_filename}' not found. Exited script\n")
        logging.info("File '%s' not found. Exited script", src_filename)
        sys.exit()
    
def check_file_csv(src_filename):
    """
    Check source file to be queried is in csv format. If not, exit with relevant error. 
    This is not a perfect check so errors may occur
    """
    try:
        with open(src_filename, newline='') as csvfile:
            # Attempt to read the first row
            csv.Sniffer().sniff(csvfile.read(1024))
            csvfile.seek(0)  # Reset file pointer to the start
            print(f"> '{src_filename}' is a csv formatted file.\n")
            logging.info("'%s' is a csv formatted file.", src_filename)
            return True
    except (csv.Error, UnicodeDecodeError):
        print(f"*** '{src_filename}' is not a csv formatted file.***\nExiting script.\n")
        logging.info("'%s' is not a csv formatted file. Exited script", src_filename)
        return False

def gen_output_filename(src_export_filename, statussearch_key):
    # Extract the filename and extension of the src file - they'll be used
    # to name the parsed output file
    base_name = os.path.basename(src_export_filename)
    name, ext = os.path.splitext(base_name)

    # Name the parsed output as src_filename-Status.csv
    parsed_results_fname = f"{name}-{statussearch_key}{ext}"
       
    logging.info("Parsed results output file name is: '%s''", parsed_results_fname)
    #print(f"> Parsed results output file name is: '{parsed_results_fname}'\n")
    return parsed_results_fname    

def backup_src_file(src_export_filename, timestamp):
    """
    Copy and timestamp the src file to keep it as a backup
    """
    # Extract the filename and extension
    base_name = os.path.basename(src_export_filename)
    name, ext = os.path.splitext(base_name)

    # Define the bkup file name
    bkp_src_filename = f"{name}_{timestamp}{ext}"
    #print(f"> Backed up Src File Name is: '{bkp_src_filename}'\n")
    
    # copy the src file to the bkup file
    shutil.copy2(src_export_filename, bkp_src_filename)
    logging.info("Src file '%s' backed up to '%s'", src_export_filename, bkp_src_filename)
    print(f"> Source file '{src_export_filename}' has been backed up to '{bkp_src_filename}'.\n")

def rename_rslts_file(outputfile_name, timestamp):
    """
    Rename (timestamp) the previous parsed output file
    """
    
    if os.path.exists(outputfile_name):
        # Extract the filename and extension
        base_name = os.path.basename(outputfile_name)
        name, ext = os.path.splitext(base_name)

        # Define the new file name
        bkp_src_filename = f"{name}_{timestamp}{ext}"
        
        # Rename the previous parsed results file
        os.rename(outputfile_name, bkp_src_filename)
        logging.info("Previous parsed output file %s' renamed to '%s'", outputfile_name, bkp_src_filename)
        print(f"> Previous parsed output file '{outputfile_name}' renamed to: '{bkp_src_filename}'\n")

def count_total_rows(src_export_filename):
    with open(src_export_filename, newline='') as csvfile:
        reader = csv.reader(csvfile)
        row_count = sum(1 for row in reader)  # Count each row
    return row_count

def find_column_number(src_export_filename, statussearch_key):
    with open(src_export_filename, newline='') as csvfile:
        reader = csv.reader(csvfile)
        
        # Iterate over each row in the CSV
        for row in reader:
            # Iterate over each column in the row
            for index, cell in enumerate(row):
                if cell == statussearch_key:
                    return index + 1  # Return 1-based column index
        
    return -1  # Return -1 if the word is not found

def number_to_excel_column(col_number):
    result = ""
    while col_number > 0:
        col_number -= 1  # Adjust because Excel columns start at 1, but we're working with 0-indexed
        result = chr(col_number % 26 + 65) + result
        col_number //= 26
    return result

def prompt_user(prtmsg):
    """
    Prompt user to check the status keyword is indeed in the stated column
    """  
    # Print msg to stdout
    print(f"\n {prtmsg} \n")
    user_choice = input("Hit any button to continue or 'n' to exit': ")

    # read in users selection to continue or otherwise
    if user_choice.lower() == "n":
        print(f"\n*** Exiting script. ***\n")
        logging.info("User entered '%s'. Exiting script", user_choice)
        sys.exit()
    else:
        print(f"\nContinuing....\n")
        logging.info("User entered '%s'. Executing the script.", user_choice)


def count_word_occurrences_in_csv_column(src_export_filename, col_number, statussearch_key):
    count = 0
    # col number reduced by 1 as indexing of columns starts at 0
    col_number -= 1
    statussearch_key = statussearch_key.strip()  # To handle any leading/trailing spaces in the search word
    with open(src_export_filename, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.reader(file)
        for row in reader:
            # Access the column by its index and ensure it's treated as a string
            if len(row) > col_number and row[col_number].strip() == statussearch_key:
                count += 1
    return count

def parse_status_record(input_file_path, output_file_path, column_index, keyword):
    """
    Filters rows from input CSV file based on keywords in a specific column
    and writes the matching rows to an output CSV file.

    :param input_file_path: Path to the input CSV file.
    :param output_file_path: Path to the output CSV file.
    :param column_index: The index of the column to check for keywords.
    :param keywords: A list of keywords to match.
    """
    # col number reduced by 1 as indexing of columns starts at 0
    column_index -= 1

    with open(input_file_path, mode='r', newline='', encoding='utf-8') as infile, \
         open(output_file_path, mode='w', newline='', encoding='utf-8') as outfile:
        
        reader = csv.reader(infile)
        writer = csv.writer(outfile)
        
        for row in reader:
            #if len(row) > column_index and keyword in row[column_index]:
            #    writer.writerow(row)
            if len(row) > column_index and row[column_index] == keyword:
                writer.writerow(row)

def print_results_to_stdout(src_filename, string_count, search_string, total_logs, percentage_of):
    # print results to stdout
    logging.info("Printing results to stdout")
    print(f"There are {string_count} '{search_string}' log entries in file '{src_filename}'.")
    print(f"This is {percentage_of:.1f}% of the total log entries of '{total_logs}'. \n")

def print_results_to_file(results_out_file, src_filename, string_count, search_string, total_logs, percentage_of): 
    # print results to defined results file
    logging.info("Printing results to results file")

    """ first format percentage_of to 1 decimal place so looks better in results file """
    formatted_percentage = f"{percentage_of:.1f}%"
    
    # Open the file and write to it
    with open(results_out_file, "a") as file1:
        logging.info("Results file '%s' has been opened for writing to.", results_out_file)
        file1.write("There are " + str(string_count) + " Severity type '" + search_string + "' entries in the file '" + src_filename + "'.\n")
        file1.write("This is " + str(formatted_percentage) + " of the total log entries of " + str(total_logs) + ".\n")
        logging.info("Results file '%s' has been closed.", results_out_file)
    return None

def main():

        # check required Pythin modules are isntalled, If not, exit with error
    required_modules = ['csv', 'platform', 'os', 'datetime', 'shutil', 'logging',]
    check_and_install_modules(required_modules)

    clear_screen()

    # Define the transaction record status to search for
    status_search_key = "Approved"
      
    # Get the full path of the script
    script_path = os.path.abspath(__file__)
    # Extract the script name from the full path
    script_name = os.path.basename(script_path)
    
    # check user has included the csv file name to be checked.
    srcexport_filename = check_arguments(script_name)

    # check csv log file exists. If not, exit
    check_file_exists(srcexport_filename)

    # check is a csv formatted file.  If not, exit
    check_file_csv(srcexport_filename)

    # Create the name of the parsed results file based on the src file used
    output_file_name = gen_output_filename(srcexport_filename, status_search_key)

    # create the timestamp
    current_timestamp = datetime.now()
    time_stamp = current_timestamp.strftime("%Y-%m-%d-%H-%M-%S")
    #print(f"timestamp = '{time_stamp}'")
  
    # Copy & timestamp the src file to be used for safety reasons
    backup_src_file(srcexport_filename, time_stamp)

    # Rename (timestamp) the existing output file for backup
    rename_rslts_file(output_file_name, time_stamp)
    
    # open the output file for writing the parsed records to
    #open_output_file(output_file_name)
  
    # Get total number of rows in the src file
    tot_num_rows = count_total_rows(srcexport_filename)
    # print(f"> The total number of rows in '{srcexport_filename}' is: {tot_num_rows}\n")  

    # Find column number
    column_number = find_column_number(srcexport_filename, status_search_key)
    #print(f"> The key search status word '{status_search_key}' is in column: {column_number}\n")  

    # convert it to excel column letter
    column_letter=number_to_excel_column(column_number)
    print(f"> The key search status word '{status_search_key}' is in column: {column_letter}.")  

    prt_msg=">> CHECK THIS IS CORRECT BEFORE PROCEEDING << "
    prompt_user(prt_msg)

    # count number of occurrences of the status word in the speicifc column in the src file
    status_count_total=count_word_occurrences_in_csv_column(srcexport_filename, column_number, status_search_key)
    src_file_count=status_count_total
    # (f"> The total number of key search status word '{status_search_key}' in column: {column_letter} of the source file '{srcexport_filename}' is: {status_count_total}\n") 

    # parse all rows with the required status to the output file
    parse_status_record(srcexport_filename, output_file_name, column_number, status_search_key)

    # count number of occurrences of the status word in the specifc column in the output file
    # and check it matches the original count
    status_count_total=count_word_occurrences_in_csv_column(output_file_name, column_number, status_search_key)
    #print(f"> The total number of key search status word '{status_search_key}' in column: {column_letter} of the output file file '{output_file_name}' is: {status_count_total}\n") 

    # verify counts in each file are the same
    if src_file_count == status_count_total:
        print(f">> The number of records in the src file '{srcexport_filename}' is the same as the generated output file '{output_file_name}' i.e. '{status_count_total}'\n")
    else:
        print(f"The variables have different values.\n")

    
    print(f">> Script has successfully finished running. All '{status_count_total}' records in state '{status_search_key}' have been written to the new file '{output_file_name}'\n\n")

if __name__ == "__main__":
    main()

