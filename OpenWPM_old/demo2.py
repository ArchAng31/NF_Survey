from automation import TaskManager
import sys
import json
import os
import time
from urlparse import urlparse
import sqlite3
import lists_helper

#master site is the list of previously visited websites
master_site_list = {}
LH = lists_helper.ListHelper()
suffix_list = LH.get_public_suffix_list()
base_folder = os.path.dirname(os.path.realpath(__file__))
#example run command for this file:
#python resources_crawl.py crawl_db.sqlite preloaded_site_list -proxy true -headless true &


# This methods loads a list of websites from a text file
def load_sites(site_path):
    sites = []
    f = open(site_path)
    for site in f:
        cleaned_site = site.strip() if site.strip().startswith("http") else "https://" + site.strip()
        sites.append(cleaned_site)
    f.close()
    return sites


#this method add all previously visited sites to the master_list
def set_initial_master_list(db_path):
    conn = sqlite3.connect(db_path)
    c = conn.execute('SELECT resource_url, content_type FROM Resource_Loads_Static')
    extension_data = c.fetchall()
    for row in extension_data:
        if row[1] == 'A TAG':
            if row[0] and row[0] != '':
                resource_url = urlparse(row[0])
                if resource_url.scheme == "https":
                    link_url = "https://" + resource_url.netloc + resource_url.path
                    if not master_site_list.get(link_url, False):
                        master_site_list[link_url] = True
    print("Length of master site list is:", len(master_site_list))


def get_depth_list(site, db_path):
    conn = sqlite3.connect(db_path)
    depth_sites = {}
    c = conn.execute('SELECT resource_url, content_type FROM Resource_Loads_Static WHERE crawl_url = ?', (site,))
    extension_data = c.fetchall()
    added_sites = 0
    for row in extension_data:
        if row[1] == 'A TAG':
            if row[0] and row[0] != '':
                resource_url = urlparse(row[0])
                if LH.check_if_link(resource_url.path):
                    domain_url = urlparse(site)
                    #check if a https link
                    if resource_url.scheme == "https":
                        #Subdomain Check
                        if LH.check_common_domain(domain_url[1], resource_url[1]):
                            link_url = "https://" + resource_url.netloc + resource_url.path
                            if not master_site_list.get(link_url, False):
                                master_site_list[link_url] = True
                                if "logout" in resource_url.path.lower():
                                    print("Found LOGOUT LINK " + link_url)
                                else:
                                    depth_sites[link_url] = True
                                    added_sites += 1
        #I cap the depth at 50 just for some consistency
        if added_sites > 5:
            #break if added 50 sites already
            return depth_sites
    return depth_sites


# runs the crawl itself
# <db_loc> is the absolute path of where we want to dump the database
# <db_name> is the name of the database
# <preferences> is a dictionary of preferences to initialize the crawler
def run_site_crawl(db_path, sites, preferences, dump_location, depth_crawl, logged_crawl):
    logged = logged_crawl
    manager = TaskManager.TaskManager(db_path, preferences, 1)
    #set_initial_master_list(os.path.join(base_folder, 'old_crawl.sqlite'))
    for site in sites:
        print(site)
        time.sleep(30)
        start_time = time.time()
        #If I am doing a logged crawl, this is a simple hack to give me time to log in to the various sites
        #before the automation takes over
        if logged:
            manager.get(site)
            time.sleep(30)
            logged = False
        manager.get(site)
        manager.extract_links(site)
        manager.dump_storage_vectors(site, start_time)
        #handle depth search
        if depth_crawl:
            #give time to make sure in database
            time.sleep(.3)
            master_site_list[site[8:len(site)]] = True
            depth_sites = get_depth_list(site, db_path)
            for path in depth_sites:
                start_time = time.time()
                manager.get(path)
                manager.extract_links(path)
                manager.dump_storage_vectors(path, start_time)

    if dump_location:
        manager.dump_profile(dump_location, True)

    manager.close()


# prints out the help message in the case that too few arguments are mentioned
def print_help_message():
    """ prints out the help message in the case that too few arguments are mentioned """
    print "\nMust call simple crawl script with at least one arguments: \n" \
        "The absolute directory path of the new crawl DB\n" \
        "Other command line argument flags are:\n" \
        "-browser: specifies type of browser to use (firefox or chrome)\n" \
        "-donottrack: True/False value as to whether to use the Do Not Track flag\n" \
        "-tp_cookies: string designating third-party cookie preferences: always, never or just_visted\n" \
        "-proxy: True/False value as to whether to use proxy-based instrumentation\n" \
        "-headless: True/False value as to whether to run browser in headless mode\n" \
        "-timeout: timeout (in seconds) for the TaskManager to default time out loads\n" \
        "-profile_tar: absolute path of folder in which to load tar-zipped user profile\n" \
        "-dump_location: absolute path of folder in which to dump tar-zipped user profile\n" \
        "-bot_mitigation: True/False value as to whether to enable bot-mitigation measures"

def main(argv):
    """ main helper function, reads command-line arguments and launches crawl """
    # filters out bad arguments
    if len(argv) < 3 or len(argv) % 2 == 0:
        print_help_message()
        return

    db_path = argv[1] # absolute path for the database
    site_file = argv[2] # absolute path of the file that contains the list of sites to visit
    sites = load_sites(site_file)

    # loads up the default preference dictionary
    fp = open(os.path.join(os.path.dirname(__file__), 'automation/default_settings.json'))
    preferences = json.load(fp)
    fp.close()

    dump_location = None
    # overwrites the default preferences based on command-line inputs

    for i in xrange(3, len(argv), 2):
        if argv[i] == "-browser":
            preferences["browser"] = "chrome" if argv[i+1].lower() == "chrome" else "firefox"
        elif argv[i] == "-donottrack":
            preferences["donottrack"] = True if argv[i+1].lower() == "true" else False
        elif argv[i] == "-tp_cookies":
            preferences["tp_cookies"] = argv[i+1].lower()
        elif argv[i] == "-proxy":
            preferences["proxy"] = True if argv[i+1].lower() == "true" else False
        elif argv[i] == "-headless":
            preferences["headless"] = True if argv[i+1].lower() == "true" else False
        elif argv[i] == "-bot_mitigation":
            preferences["bot_mitigation"] = True if argv[i+1].lower() == "true" else False
        elif argv[i] == "-timeout":
            preferences["timeout"] = float(argv[i+1]) if float(argv[i]) > 0 else 30.0
        elif argv[i] == "-profile_tar":
            preferences["profile_tar"] = argv[i+1]
        elif argv[i] == "-disable_flash":
            preferences["disable_flash"] = True if argv[i+1].lower() == "true" else False
        elif argv[i] == "-dump_location":
            dump_location = argv[i+1]

    #This is the line that adds the extension. "Desktop" saves all dynamic resources to Requests.sqlite
    #on the desktop. Anything else sends the data via socket to same database as the crawl,
    # but has issues with too many files (open sockets).
    #preferences["pinning"] = "Desktop"
    preferences["pinning"] = False

    #turns on lastpass - I use lastpass for logged in crawls
    preferences["lastpass"] = False

    #Copy site_file to Desktop
    #copy_path = os.path.expanduser('~/Desktop/crawl_sites.txt')
    #shutil.copy2(site_file, copy_path)
    
    # launches the crawl with the updated preferences
    run_site_crawl(db_path, sites, preferences, dump_location, False, False)

    #remove site_file from desktop
    #if os.path.exists(copy_path):
    #    os.remove(copy_path)

if __name__ == "__main__":
    main(sys.argv)
