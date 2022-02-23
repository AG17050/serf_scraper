# serf_scraper

## What it does
Used to scrape to scrape the 
* CA CDI: https://interactive.web.insurance.ca.gov/apex_extprd/f?p=102:InteractiveReport:0::NO:4,RIR::
* CA DMHC: https://wpso.dmhc.ca.gov/premiumratereview/FilingList.aspx
* The SERF sites for the other states.

The files that are downloaded are tracked and stored in `file_collection/downloaded_files.pkl`
To wipe the downloaded records, run `wipe.py`

Whatever is downloaded is stored in the Downloads folder.

## How to run: 
* Set the sites that you want to run with the `serf_states_to_run.csv`
* Set the submission date you want using the `serf_submission_dates.txt`
* run `main.py`

## How to run with windows scheduler:
If you wish to use windows scheduler to run the scraper, ensure you've put your username and the appropriate virtual environment in the
`serf_filing.bat` file, as well as the appropriate path to the file (assuming you cloned the repo on your desktop).

You also need to make sure you have the necessary chromedriver in the main folder (typically the lastest stable release).
https://chromedriver.chromium.org/downloads

`"C:/Users/<username>/AppData/Local/conda/conda/envs/<virtualenv>/python.exe" "C:/Users/<username>/OneDrive - Anthem/Desktop/serf_scraper/main.py"`
edit

