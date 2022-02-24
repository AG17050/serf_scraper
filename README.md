# serf_scraper

## What it does
Used to scrape to scrape the 
* CA CDI: https://interactive.web.insurance.ca.gov/apex_extprd/f?p=102:InteractiveReport:0::NO:4,RIR::
* CA DMHC: https://wpso.dmhc.ca.gov/premiumratereview/FilingList.aspx
* The SERF sites for the other states.

The files that are downloaded are tracked and stored in `file_collection/downloaded_files.pkl`
To wipe the downloaded records, run `wipe.py` DO NOT DO THIS IF YOU ARE GINA.
wiping is only done for development and testing.

Whatever is downloaded is stored in the Downloads folder.

## How to run: 
* Set the sites that you want to run with the `serf_states_to_run.csv`
* Set the submission date you want using the `serf_submission_dates.txt`
* run `main.py` *or* double click the `serf_filing.bat` file.

## How to run with task scheduler:
If you wish to use windows scheduler to run the scraper, ensure you've put your username and the appropriate virtual environment in the
`serf_filing.bat` file, as well as the appropriate path to the file (assuming you cloned the repo on your desktop).
* Open up `task scheduler` -> `Task Scheduler Library`
* If the task present, *click* Run (in Actions)
* The task should already be created for Gina.
  * *right click* -> properties -> Triggers

## Updating the chrome driver.
You also need to make sure you have the necessary chromedriver in the main folder (typically the lastest stable release).
https://chromedriver.chromium.org/downloads <br> 
Refer to chrome://settings/help (plug into browser url) for the exact chrome version you might need.
Unzip the chrome driver zip file and put the `chromedriver.exe` in the `serf_scraper` folder.

## How to git pull
* Open up `git bash`
* *enter the command* `cd "<the file path to serf_scraper>"`
  * ie for me, I would do `cd "C:\Users\AG17050\OneDrive - Anthem\Desktop\Gina\serf_scraper"`
* *enter the command* `git pull`

## What to try if something breaks
* Check the chromedriver and chrome version. Update if necessary
* Check the urls of `CA`. they tend to break.
* Check the urls of the `SERF` sites since they've broken before.
* Set the states with broken urls to `No` in the `states_to_run.csv` file.
* Check the downloads folder to see if the program is trying to move something into `Moved_Downloads_Content` with the same name.

`"C:/Users/<username>/AppData/Local/conda/conda/envs/<virtualenv>/python.exe" "C:/Users/<username>/OneDrive - Anthem/Desktop/serf_scraper/main.py"`
edit

