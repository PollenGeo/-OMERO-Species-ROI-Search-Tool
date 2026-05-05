# -OMERO-Species-ROI-Search-Tool
This Python script connects to an OMERO server and searches for specific species  names within ROI (Region of Interest) annotations across images. When matches are found, the script collects relevant metadata and generates a CSV file with direct links to visualize the matching ROIs in OMERO.web.

Additionally, the script can automatically open the first set of results in a web browser 
to streamline validation and review.

Features:
---------
- Connects to an OMERO server using user-provided credentials.
- Allows searching across all groups or a specific group.
- Iterates through images and reads ROI shape annotations.
- Matches user-defined species names against ROI text labels.
- Generates a CSV file with detailed results and OMERO links.
- Opens the first 20 matching results automatically in a browser.
- Supports configurable browser selection.
- Includes safeguards such as image processing limits and delays.

Requirements:
-------------
The script requires the following Python libraries:
- pandas
- omero-py
- tkinter (built-in for most Python distributions)
- webbrowser (built-in)
- time (built-in)

Installation:
-------------
Before running the script, install the required dependencies:

1. Install necessary Python packages:
pip install pandas pip install omero-py

2. If `tkinter` is not installed (Linux users only):
sudo apt-get install python3-tk

Configuration:
--------------
- Update the AVAILABLE_BROWSERS dictionary with the correct paths for your system.
- Adjust optional parameters if needed:
  - MAX_IMAGES_PER_GROUP (default: 50)
  - PAUSE_BETWEEN_IMAGES (default: 0.5 seconds)

Usage:
------
1. Run the script:
python shapebrowser.py

2. Enter OMERO server credentials when prompted:
   - Host 
   - Username
   - Password

3. Enter species names separated by commas.

4. Choose:
   - Search across all groups, or
   - Select a specific group by ID.

5. Select a location to save the CSV file.

6. Ensure you are logged into OMERO.web in your browser.

7. The script will:
   - Process images
   - Identify matches
   - Save results
   - Open the first 20 links automatically

Output:
-------
The generated CSV file contains the following fields:
- group_id
- group_name
- image_id
- shape_id
- species_name
- omero_link

Notes:
------
- The script limits processing to a maximum number of images per group to avoid long execution times.
- A delay is introduced between image processing requests to reduce server load.
- ROI loading errors are handled gracefully and skipped.

Author:
-------
This script was developed by **Daurys De Alba**.

For inquiries, contact:
- Email: daurysdealbaherra@gmail.com
- Email: DeAlbaD@si.edu
