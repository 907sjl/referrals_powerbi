import pandas as pd 
import numpy as np 

from datetime import datetime 
from dateutil.relativedelta import relativedelta

import random 

# Load table of dsm sender categories 
dsm_sender_category = pd.read_csv("dsm_sender_category.csv", encoding="cp1252") 
dsm_sender_category_count = len(dsm_sender_category.index) 
dsm_sender_category_column = dsm_sender_category.columns.get_loc("Sender Category")

# Load table of locations where referrals are sent 
provider_referred_to = pd.read_csv("provider_referred_to.csv", encoding="cp1252") 
provider_referred_to_count = len(provider_referred_to.index) 
provider_referred_to_column = provider_referred_to.columns.get_loc("Provider Referred To")
location_referred_to_column = provider_referred_to.columns.get_loc("Location Referred To")
organization_referred_to_column = provider_referred_to.columns.get_loc("Organization Referred To")
clinic_column = provider_referred_to.columns.get_loc("Clinic")

# Each refer-to location has a randomized performance factor
provider_referred_to['rate_adjustment'] = (np.random.random(len(provider_referred_to.index)) * 0.8) - 0.4 
rate_adjustment_column = provider_referred_to.columns.get_loc("rate_adjustment")

# Dictionary of parameters used to shape the random data set
data_parameters = {
  'minimum_messages_daily': 30 
  , 'maximum_messages_daily': 138 
  , 'first_message_date': datetime(2019, 9, 1) 
  , 'last_message_date': datetime(2023, 4, 3) 
  , 'referral_rate': 0.33 
} 

# The effective data "as-of" date of the data set
data_date = datetime(2023, 3, 1) 


## Main 

# Output the referrals data set direct to a csv text file 
f = open("DirectSecureMessages.csv", "w") 

# Column headers in first row 
record_str = 'Message ID,Message Date,Clinic,Sender Category,Sent From,Referral ID,Date Referral Sent,Person ID\n' 
f.write(record_str)

# Initialize message ID #s
message_id = 1 

# Loop over each calendar day over the given time period to create random messages
message_date = data_parameters['first_message_date']  
while message_date <= data_parameters['last_message_date']: 
 
  # Loop over a random number of messages for each date and create them one at a time 
  num_messages = round((random.random() * (data_parameters['maximum_messages_daily'] - data_parameters['minimum_messages_daily'])) + data_parameters['minimum_messages_daily']) 
  print(message_date.strftime("%m/%d/%Y"), ", ", num_messages, " messages") 
  message_num = 0 
  while message_num < num_messages: 
    
    # Initialize referral process dates
    referral_sent_date = datetime(1, 1, 1) 
    
    # Choose a random patient id 
    patient_id = round(random.random() * (num_messages * 10.0)) 
    
    # Choose a message sender category from the reference list
    idx = round(random.random() * (dsm_sender_category_count - 1)) 
    sender_category_val = dsm_sender_category.iloc[idx, dsm_sender_category_column] 

    # Create a random sender address 
    sender_id = round(random.random() * 20.0) 
    sender = sender_category_val + r'.' + str(sender_id) + r'@direct.health.com' 

    # Choose a random refer-to provider from the reference list 
    idx = round(random.random() * (provider_referred_to_count - 1)) 
    clinic_val = provider_referred_to.iloc[idx, clinic_column] 
    rate_adjustment = provider_referred_to.iloc[idx, rate_adjustment_column] 

    # Randomly select messages to also have a referral associated  
    referral = 0
    referral_id_str = '' 
    idx = random.random() 
    if (idx < (data_parameters['referral_rate'] + rate_adjustment)): 
      days_to_referral = round(random.random() * 60.0) - 30   
      referral_sent_date = message_date + relativedelta(days=days_to_referral) 
      referral_sent_date_str = referral_sent_date.strftime("%m/%d/%Y") 
      referral_id = round(random.random() * 180000.0) 
      referral_id_str = str(referral_id) 
      referral = 1 
    else:
      referral_sent_date = datetime(1, 1, 1) 
      referral_sent_date_str = '' 
      referral_id = 0 
      referral_id_str = '' 
      referral = 0 

    # Export message record 
    message_date_str = message_date.strftime("%m/%d/%Y") 
    record_str = f'{message_id},"{message_date_str}","{clinic_val}","{sender_category_val}","{sender}",{referral_id_str},"{referral_sent_date_str}",{patient_id}\n' 
    f.write(record_str) 

    # Next message 
    message_id = message_id + 1 
    message_num = message_num + 1 
    # END of num message loop

  # Next message date 
  message_date = message_date + relativedelta(days=1) 
  #END of dates loop

f.close()
