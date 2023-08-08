< [Portfolio](https://907sjl.github.io) | [Full Report](https://907sjl.github.io/pdf/Referral%20Wait%20Time.pdf) | [Power BI example](https://907sjl.github.io/referrals_powerbi/) 

## About  
This folder contains two scripts that were used to generate referrals data for the report of referrals volume and throughput for specialty clinics.  This report is one example of my work.    

I used Python to create simple script-style programs that randomly generate referral processing data.  
- create_referral_data.py
: This script creates a random number of referrals for every calendar day between two dates.  The referrals are sent to randomly selected clinics from randomly selected sources.  The dates when each referral reaches processing milestones are then randomly selected.  The result is a comma separated variable (csv) file of referrals and the dates when each referral met processing milestones.    

- create_dsm_data.py
: This script creates receipt data for a random number of dsm messages for every calendar day between two dates.  A random number of these messages are for patients with referrals that were tracker with the clinic referral management system.    

Both scripts export their data to Comma Separated Variable (csv) files.  The output files become data sources for the report.  

## Reference Tables 
A handful of reference tables in csv files are imported into the scripts using Pandas.  Items are selected from the reference tables at random to create each record in the resulting output files.    

- assigned_personnel.csv
: Contains one row for each personnel who can be assigned to follow-up on a referral.    

- dsm_sender_category.csv
: Contains one row for each grouping of direct secure message senders based on their organization.    

- last_referral_update_by.csv
: Contains one row for each personnel who can update referrals.    

- provider_referred_to.csv
: Contains one row for each provider where referrals can be sent, along with the location, clinic, and organization where the provider practices.    

- reason_for_hold.csv
: Contains one row for each reason for placing a referral on hold.    

- referral_substatus.csv
: Contains one row for each processing queue sub-status that can be assigned to a referral for more information about the next step.    

- source_locations.csv
: Contains one row for each location that can send referrals.    

< [Portfolio](https://907sjl.github.io) | [Full Report](https://907sjl.github.io/pdf/Referral%20Wait%20Time.pdf) | [Power BI example](https://907sjl.github.io/referrals_powerbi/) 
