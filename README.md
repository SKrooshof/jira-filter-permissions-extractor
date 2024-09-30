# Jira Filter Permissions Extractor #

This Python script extracts filter permissions and roles from Jira instances, supporting both Jira Cloud and Jira Server. It processes the data concurrently and saves the output to a CSV file.

### Requirements ###

* Python 3.6 or higher
* The following Python modules:
	* requests
	* pandas
	* tqdm

### Installation ###

1. Clone the repository:
```
git clone git@bitbucket.org:prepend-eu/jira-filter-permissions-extractor.git
cd jira-filter-permissions-extractor
```
2. Set up a virtual environment:
```
python3 -m venv venv
source venv/bin/activate
```
3. Install the required modules:
```
pip install -r requirements.txt
```

### Running the Script ###

1. Activate the virtual environment (if not already activated):
```
source venv/bin/activate
```
2. Run the script:
```
python get_filter_permissions.py
```
3. Follow the prompts:
* Enter the instance type (cloud/server).
* Enter the Jira instance URL.
* Enter your username.
* Enter your password (for server) or API key (for cloud).

### Example Usage ###
```
$ python get_filter_permissions.py
Enter instance type (cloud/server): cloud
Enter Jira instance URL: https://yourcompany.atlassian.net
Enter username: your.username
Enter API key: 
Fetching Filter Details: 100%|███████████████████████████████| 889/889 [00:45<00:00, 19.34it/s]
2024-07-17 17:39:23,433 - INFO - Saving data to CSV: jira_filters.csv
Filter details saved to jira_filters.csv
...
```

### Notes ###

* Ensure you have the necessary permissions to access the Jira REST API.
* The script will handle projects that cannot be accessed due to permission issues by skipping them and continuing with the next project.
