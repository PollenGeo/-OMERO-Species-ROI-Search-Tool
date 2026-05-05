import pandas as pd
import time
import webbrowser
from omero.gateway import BlitzGateway
import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox

# Configuration
MAX_IMAGES_PER_GROUP = 50
PAUSE_BETWEEN_IMAGES = 0.5  # seconds

# Dictionary of available browsers: modify paths according to your operating system
AVAILABLE_BROWSERS = {
    "chrome": "C:/Program Files/Google/Chrome/Application/chrome.exe",
    "firefox": "C:/Program Files/Mozilla Firefox/firefox.exe",
    "edge": "C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe",
    "brave": "C:/Program Files/BraveSoftware/Brave-Browser/Application/brave.exe",
    "opera": "C:/Users/DeAlbaD/AppData/Local/Programs/Opera/opera.exe"
}

def choose_and_configure_browser():
    options = list(AVAILABLE_BROWSERS.keys())
    browser = simpledialog.askstring(
        "Select Browser",
        f"Please enter one of these browsers:\n{', '.join(options)}",
        initialvalue="chrome"
    )

    if browser not in AVAILABLE_BROWSERS:
        messagebox.showerror("Error", "Invalid browser. The system default will be used.")
        return None

    path = AVAILABLE_BROWSERS[browser]
    webbrowser.register(browser, None, webbrowser.BackgroundBrowser(path))
    return browser

def connect_to_omero():
    root = tk.Tk()
    root.withdraw()

    host = simpledialog.askstring("OMERO Login", "Enter OMERO Host:", initialvalue="mendel.si.edu")
    username = simpledialog.askstring("OMERO Login", "Enter OMERO Username:")
    password = simpledialog.askstring("OMERO Login", "Enter OMERO Password:", show="*")

    conn = BlitzGateway(username, password, host=host, port=4064, secure=True)
    if not conn.connect():
        raise ConnectionError("Failed to connect to OMERO. Check your credentials.")

    print("Connected to OMERO successfully.")
    groups = conn.getGroupsMemberOf()
    group_dict = {g.getId(): g.getName() for g in groups}

    return conn, group_dict, host

def search_species(conn, group_id, species_list, host):
    results = []
    conn.setGroupForSession(group_id)
    group_name = conn.getGroupFromContext().getName()
    print(f"\nSearching in Group: {group_name} (ID: {group_id})")

    start = 0
    limit = 25
    image_count = 0
    processed = 0

    while True:
        images = list(conn.getObjects("Image", opts={'start': start, 'limit': limit}))
        if not images:
            break

        for image in images:
            if processed >= MAX_IMAGES_PER_GROUP:
                print(f"Limit of {MAX_IMAGES_PER_GROUP} images reached for this group.")
                break

            image_count += 1
            processed += 1
            image_id = image.getId()
            print(f"  Processing image: {image.getName()} (ID: {image_id})")

            time.sleep(PAUSE_BETWEEN_IMAGES)

            try:
                rois = image.getROIs()
            except Exception as e:
                print(f"  Skipping image {image_id} due to ROI loading error: {e}")
                continue

            for roi in rois:
                for shape in roi.getShapes():
                    if shape.getTextValue():
                        shape_text = shape.getTextValue().getValue().lower()
                        for species in species_list:
                            if species.lower() == shape_text.lower():
                                shape_id = shape.getId().getValue()
                                results.append({
                                    "group_id": group_id,
                                    "group_name": group_name,
                                    "image_id": image_id,
                                    "shape_id": shape_id,
                                    "species_name": species,
                                    "omero_link": f"http://{host}/omero/iviewer?shape={shape_id}"
                                })

        start += limit
        if processed >= MAX_IMAGES_PER_GROUP:
            break

    print(f"Finished group {group_name}. Images processed: {processed}. Matches found: {len(results)}")
    return results

def save_results_to_csv(results, custom_browser):
    if not results:
        print("No matches found.")
        return

    df = pd.DataFrame(results)
    file_path = filedialog.asksaveasfilename(
        title="Save CSV File",
        defaultextension=".csv",
        filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
    )

    if file_path:
        df.to_csv(file_path, index=False)
        print(f"Results saved to {file_path}")

        messagebox.showinfo(
            "Important",
            "Before opening the first 20 links, please make sure you are logged into OMERO Web in your browser."
        )

        top_links = df["omero_link"].head(20)
        for link in top_links:
            if custom_browser:
                webbrowser.get(custom_browser).open_new_tab(link)
            else:
                webbrowser.open_new_tab(link)
    else:
        print("No file selected. Exiting.")

if __name__ == '__main__':
    root = tk.Tk()
    root.withdraw()
    custom_browser = choose_and_configure_browser()

    try:
        conn, group_dict, host = connect_to_omero()
        species_input = simpledialog.askstring("Search Species", "Enter species names separated by commas:")

        if not species_input:
            print("No species name entered. Exiting.")
        else:
            species_list = [s.strip() for s in species_input.split(",")]
            group_option = messagebox.askyesno(
                "Group Selection",
                "Do you want to search in ALL groups?\nYes = All groups\nNo = Choose a specific group"
            )
            results = []

            if group_option:
                if len(group_dict) > 5:
                    proceed = messagebox.askyesno(
                        "Confirm",
                        f"There are {len(group_dict)} groups. This may take time.\nDo you want to continue?"
                    )
                    if not proceed:
                        exit()

                for gid in group_dict:
                    results.extend(search_species(conn, gid, species_list, host))

            else:
                group_info_list = [f"ID: {gid} - Name: {gname}" for gid, gname in group_dict.items()]
                group_list_str = "\n".join(group_info_list)
                selected_group_id_str = simpledialog.askstring(
                    "Select Group ID",
                    f"Available groups:\n{group_list_str}\n\nEnter the group ID to search in:"
                )

                if not selected_group_id_str or not selected_group_id_str.isdigit():
                    print("Invalid input. Exiting.")
                    conn.close()
                    exit()

                selected_group_id = int(selected_group_id_str)
                if selected_group_id not in group_dict:
                    print("Group ID not found. Exiting.")
                    conn.close()
                    exit()

                results = search_species(conn, selected_group_id, species_list, host)

            save_results_to_csv(results, custom_browser)

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        if conn:
            conn.close()
