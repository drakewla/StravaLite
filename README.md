# Strava Activity Filter

This Python script helps you filter activities from your Strava ZIP archive and create a new ZIP containing only activities matching specific types.

## Get the Strava archive

You need to request a download of your Strava data in the account section "Download or Delete Your Account" on Strava, located at the (scary!) URL: https://www.strava.com/athlete/delete_your_account.
Select "Request Your Archive" and wait for an email from Strava (be patient, it took two weeks before I received it).

## How to Use

1. **Save the script:** Save the script as a Python file (e.g., `strava_filter.py`).
2. **Install dependencies:** They are likely already installed on your system. If some dependencies are missing, make sure you have the required Python libraries installed (`zipfile`, `csv`, `tempfile`, `os`, `argparse`). You can install them using your package manager or :

  ```bash
   pip3 install zipfile csv tempfile os argparse
  ``` 
3. **Run the script**: Open a terminal, navigate to the directory where you saved the script, and run the following command:

   ```bash
   python3 strava_filter.py "path/to/your/strava_archive.zip"
   ``` 
    -   Replace `"path/to/your/strava_archive.zip"` with the actual path to your Strava ZIP archive file.

## Arguments

*   `-o`, `--output`: (Optional) Specify the output ZIP filename. Defaults to "strava_output.zip".
*   `-k`, `--keep`: (Optional) Comma-separated list of activity types to keep in the output ZIP (e.g., `"Ride,Walk,Hike"`). Defaults to "Ride,Walk,Hike,Run,Snowshoe,E-Bike Ride".

## Notes

*   This script assumes the Strava ZIP archive contains a file named `activities.csv`.
*   The script creates a temporary directory to process the files. This directory is automatically cleaned up after the script finishes.
*   If no activities match the specified types, the script will inform you and exit without creating an output ZIP.
*   The script uses the Python ZipFile module, which is slower than a native zip command.

## Example Usage

```bash
python strava_filter.py "Strava_Export_12345.zip" -o filtered_activities.zip -k "Ride,Run"
```
This command will filter activities from "Strava_Export_12345.zip", create a new ZIP named "filtered_activities.zip", and only include activities of type "Ride" and "Run".

### Runtime and file size on my computer:

```bash
time python3 StravaLite.py ~/Documents/strava_export_2843295-20241110.zip
Created temporary directory: /tmp/tmpvreyexvq
Number of activities to extract and ZIP: 13430

real    1m15.067s
user    0m40.716s
sys     0m10.890s
```
My output archive is a compact 900 MiB compared to a hefty 26 GiB in the original archive.
