import zipfile
import csv
import tempfile
import os
import argparse

def filter_csv(input_file, output_file, activity_types):
    """Filters a Strava activities.csv file based on the list of specified activity types.

    Args:
        input_file (str): Path to the input activities.csv file.
        output_file (str): Path to write the filtered activities.csv file.
            NOTE: fields containing "" become empty but it shoudn't affect the parsing.
        activity_types (list): List of activity types to keep.

    Returns:
        list: List of extracted activity filenames.
    """

    activities = []
    with open(input_file, mode='r', newline='') as infile, open(output_file, mode='w', newline='') as outfile:
        reader = csv.reader(infile)
        writer = csv.writer(outfile)

        # Write the header to the output file
        header = next(reader)
        writer.writerow(header)

        # Find the index of the "Activity Type" column
        activity_type_index = header.index('Activity Type')
        filename_type_index = header.index('Filename')

        # Filter and write the rows
        for row in reader:
            activity_type = row[activity_type_index].strip()
            if activity_type in activity_types:
                writer.writerow(row)
                # Include the actity file only if it's defined (Manual activities have no GPS data)
                if row[filename_type_index].startswith('activities/'): 
                    activities.append(row[filename_type_index])

    return activities

def list_zip(zip_path, filename):
    """Lists the contents of a ZIP file and returns False if at last one element is missing.

    Args:
        zip_path (str): Path to the input ZIP file.
        filename (list): List of files to look for in the ZIP archive.

    Returns:
        boolean: True is all files are found, otherwise False.
    """

    if isinstance(filename, str): filename = [filename]
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            file_list = zip_ref.namelist()
            for file in filename:
                if not file in file_list:
                    print(f"The file '{file}' does not exist in the ZIP archive.")
                    return False
        return True
    except zipfile.BadZipFile:
        print(f"The file '{zip_path}' is not a valid ZIP file.")
    except FileNotFoundError:
        print(f"The file '{zip_path}' does not exist.")
    except Exception as e:
        print(f"An error occurred while listing: {e}")
    return False

# Extracts a list of files from a ZIP archive
def extract_zip(zip_path, filename, destination):
    """Extracts a list of files from a ZIP archive.

    Args:
        zip_path (str): Path to the input ZIP file.
        filename (list): List of files to extract from the ZIP archive.
        destination (str): Destination directory where to extract the files.

    Returns:
        Boolean: True if no exception, otherwise False.
    """

    if isinstance(filename, str): filename = [filename]
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(path=destination, members=filename)
            return True
    except zipfile.BadZipFile:
        print(f"The file '{zip_path}' is not a valid ZIP file.")
    except FileNotFoundError:
        print(f"The file '{zip_path}' does not exist.")
    except Exception as e:
        print(f"An error occurred while extracting: {e}")
    return False

# 
def create_zip_archive(zip_path, folder_path):
    """Creates a new ZIP archive with the files from folder_path which becomes the root of the archive.

    Args:
        zip_path (str): Path to the output ZIP file.
        folder_path (str): Folder path of the contents to add to the ZIP file.

    Returns:
        Boolean: True if no exception, otherwise False.
    """

    try:
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    if not os.path.isfile(file_path):
                        print (f"Activity file {file_path} is missing!")
                    else:
                        # Ensure the path in the zip file is relative to the folder_path
                        zipf.write(file_path, os.path.relpath(file_path, folder_path))
        return True
    except Exception as e:
        print(f"An error occurred while creating the ZIP file: {e}")
        return False

# Run the sauce
if __name__ == "__main__":
    # Arguments parsing
    parser = argparse.ArgumentParser(description="Strava ZIP archive activity filter. Creates a new ZIP archive with only the activities matching certain activity types, ignore media and other stuff.")
    parser.add_argument("file", metavar='zip_path', type=str, help="Strava archive ZIP file. Should be like \"path/to/strava_export_123456-20241110.zip\" unless renamed.")
    parser.add_argument("-o", "--output", default="strava_output.zip", help="Output ZIP file. Defaults to \"strava_output.zip\"")
    parser.add_argument("-k", "--keep", default="Ride,Walk,Hike,Run,Snowshoe,E-Bike Ride", help="Comma-separated values of activity types to keep. Remember to quote it when including spaces. Defaults to: \"Ride,Walk,Hike,Run,Snowshoe,E-Bike Ride\"")

    args = parser.parse_args()    

    zip_path = args.file
    output_zip = args.output

    # Create a list from the comma-separated keep argument and strip spaces
    filter = [x.strip() for x in args.keep.split(',')]

    # Check if this is the ZIP file from Strava by verifying if activities.csv is present in the archive
    check=list_zip(zip_path, 'activities.csv')

    if not check:
       print("Couldn't find a file named activities.csv in the ZIP file. Looks like it's not a Strava archive.")
       exit(1)
    
    # Do all the work in a temporary directory
    with tempfile.TemporaryDirectory() as tmpdirname:
        print('Created temporary directory:', tmpdirname)

        # Extract activities.csv
        extract=extract_zip(zip_path, 'activities.csv', tmpdirname)

        # Filter activities.csv content to filtered_activities.csv
        activities = filter_csv(f'{tmpdirname}/activities.csv', f'{tmpdirname}/filtered_activities.csv', filter)

        if len(activities) == 0:
            print("Sorry, there is no activity matching the filtered 'Activity Type' requirement.")
        else:
            print("Number of activities to extract and ZIP:", len(activities))

            # Extract activities from new filtered_activities.csv
            extract=extract_zip(zip_path, activities, tmpdirname)

            # Replace activities.csv with new filtered_activities.csv
            os.rename(f'{tmpdirname}/filtered_activities.csv', f'{tmpdirname}/activities.csv')

            # Create a zip archive
            output=create_zip_archive(output_zip, tmpdirname)
            if not output:
                print("An error occurred, see above.")
                exit(1)
