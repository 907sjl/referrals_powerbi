< [Portfolio](https://907sjl.github.io) | [Full Report](https://907sjl.github.io/pdf/Referral%20Wait%20Time.pdf) | [Overview](https://907sjl.github.io/referrals_powerbi/referrals_report) 

## About  
This script was used to generate referrals data for the report of referrals volume and throughput for specialty clinics.  This report is one example of my work.    

I used Python to create a simple script style program that exports a comma separated variable (csv) file of referrals and the dates when each referral met processing milestones.    

The output file of referral data becomes a data source for the report.  

## Reference Tables 
A handful of reference tables in csv files are imported into the script using Pandas.  Items are selected from the reference tables at random for each referral record in the resulting output file.    

- assigned_personnel.csv
: Contains one row for each personnel who can be assigned to follow-up on a referral.    

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

< [Portfolio](https://907sjl.github.io) | [Full Report](https://907sjl.github.io/pdf/Referral%20Wait%20Time.pdf) | [Overview](https://907sjl.github.io/referrals_powerbi/referrals_report) 
