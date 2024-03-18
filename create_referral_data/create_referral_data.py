"""
create_referral_data.py
Author: Steven J Leathard

A script to create synthetic specialty clinic referral data for my examples of prior work.
"""


import pandas as pd
import numpy as np
from math import floor

from datetime import datetime 
from dateutil.relativedelta import relativedelta

import random 


# Load table of locations that send referrals 
source_locations = pd.read_csv("source_locations.csv", encoding="cp1252") 
source_location_count = len(source_locations.index) 
source_location_column = source_locations.columns.get_loc("Source Location")

# Load table of locations where referrals are sent 
provider_referred_to = pd.read_csv("provider_referred_to.csv", encoding="cp1252") 
provider_referred_to_count = len(provider_referred_to.index) 
provider_referred_to_column = provider_referred_to.columns.get_loc("Provider Referred To")
location_referred_to_column = provider_referred_to.columns.get_loc("Location Referred To")
organization_referred_to_column = provider_referred_to.columns.get_loc("Organization Referred To")
clinic_column = provider_referred_to.columns.get_loc("Clinic")

# Each refer-to location has a randomized performance factor
provider_referred_to['rate_adjustment'] = (np.random.random(len(provider_referred_to.index)) * 0.6) - 0.3 
rate_adjustment_column = provider_referred_to.columns.get_loc("rate_adjustment")

# Load table of people who make updates to referrals 
last_referral_update_by = pd.read_csv("last_referral_update_by.csv", encoding="cp1252") 
last_referral_update_by_count = len(last_referral_update_by.index) 
last_referral_update_by_column = last_referral_update_by.columns.get_loc("Last Referral Update By")

# Load table of people who are assigned to follow-up on referrals
assigned_personnel = pd.read_csv("assigned_personnel.csv", encoding="cp1252") 
assigned_personnel_count = len(assigned_personnel.index) 
assigned_personnel_column = assigned_personnel.columns.get_loc("Assigned Personnel")

# Load table of reasons for referrals to be on hold
reason_for_hold = pd.read_csv("reason_for_hold.csv", encoding="cp1252") 
reason_for_hold_count = len(reason_for_hold.index) 
reason_for_hold_column = reason_for_hold.columns.get_loc("Reason for Hold")

# Load table of referral queue sub-statuses
referral_substatus = pd.read_csv("referral_substatus.csv", encoding="cp1252") 
referral_substatus_count = len(referral_substatus.index) 
referral_substatus_column = referral_substatus.columns.get_loc("Referral Sub-Status")

# Dictionary of parameters used to shape the random data set
data_parameters = {
  'minimum_referrals_daily': 30,
  'maximum_referrals_daily': 240,
  'first_referral_date': datetime(2019, 9, 1),
  'last_referral_date': datetime(2023, 4, 3),
  'urgent_priority': 0.1,
  'referral_written_weights': [0.89, 0.96, 0.98, 0.99],
  'accepted_rate': 0.9,
  'days_to_accept': [1, 10],
  'scheduled_rate': 0.7,
  'referral_scheduled_weights': [0.65, 0.73, 0.81, 0.88, 0.93, 0.96],
  'seen_rate': 0.86,
  'referral_seen_weights': [0.19, 0.31, 0.48, 0.68, 0.86, 0.95],
  'similar_scheduled_rate': 0.84,
  'similar_scheduled_weights': [0.43, 0.57, 0.7, 0.8, 0.87, 0.92],
  'similar_seen_rate': 0.9,
  'similar_seen_weights': [0.23, 0.35, 0.51, 0.69, 0.87, 0.95],
  'seen_completed_rate': 0.85,
  'seen_completed_weights': [0.41, 0.5, 0.57, 0.64, 0.71, 0.77],
  'not_seen_completed_rate': 0.06,
  'not_seen_completed_weights': [0.32, 0.43, 0.5, 0.59, 0.68, 0.76],
  'days_to_update': [0, 10],
  'completed_and_closed_rate': 0.07,
  'not_completed_and_closed_rate': 0.02,
  'rejected_rate': 0.26,
  'cancelled_rate': 0.20,
  'on_hold_rate': 0.05,
  'on_hold_weights': [0.29, 0.35, 0.43, 0.57, 0.81, 0.99],
  'pending_reschedule_rate': 0.16,
  'pending_reschedule_weights': [0.2, 0.23, 0.28, 0.4, 0.71, 1],
  'closed_rate': 0.05,
  'earlier_appt_weights': [0.0, 0.03, 0.1, 0.2, 0.3, 0.6]
}

# Bins of maximum days to reach process milestones 
weighting_bins = {
  'Routine': [2, 3, 5, 10, 20, 40, 80],
  'Urgent': [1, 2, 3, 5, 10, 20, 40]
}

# The effective data "as-of" date of the data set with the date when referrals on hold can start to appear
data_date = datetime(2023, 3, 1) 
holds_start_date = datetime(2022, 9, 1) 


# FUNCTIONS

def get_referral_date(test: int,
                      chance_parameter: str,
                      chance_adjustment: float,
                      weights_parameter: str,
                      base_date: datetime,
                      priority: str) -> tuple[datetime, str, int]:
    """
    Randomly decides if a process date should be calculated for a single referral and returns a random process date
    that is a random number of days after a given base date.

    Args:
      test: if >0 then a date is calculated, otherwise none
      chance_parameter: the name of an entry in data_parameters that contains the rate of returning a date
      chance_adjustment: the amount to subtract from the rate used to determine if a date should be returned
      weights_parameter: the name of an entry in data_parameters that contains weightings for the number of days
      base_date: the date added to in order to calculate the date that is returned
      priority: the referral priority

    Returns:
      A tuple of three values:
      - the datetime value calculated or the value datetime(1, 1, 1) for none
      - the text rendering of the date value or an empty string for none
      - 1 if a date was calculated, 0 otherwise
    """

    # Default assumption that this process milestone will not be met
    return_test = 0

    # If the previous milestone test has been passed, calculate random chance of
    # meeting this milestone
    if test > 0:
        chance = random.random()

        # If this milestone will be met calculate the date when it was met
        if chance < (data_parameters[chance_parameter] + chance_adjustment):

            # Small chance of this referral date being very different from the others
            if random.random() < 0.15:
                chance_adjustment = chance_adjustment * -1.0 * (random.random() + 1.0)

            # Randomly select a bin of days to reach milestone, then based on the
            # bin randomly select the number of days to reach the milestone
            chance = random.random()
            if chance < data_parameters[weights_parameter][0]+chance_adjustment:
                days = round(random.random() * weighting_bins[priority][0])
            elif chance < data_parameters[weights_parameter][1] + chance_adjustment:
                days = round(random.random() * weighting_bins[priority][1]) + weighting_bins[priority][0]
            elif chance < data_parameters[weights_parameter][2] + chance_adjustment:
                days = (round(random.random() * weighting_bins[priority][2]) +
                        weighting_bins[priority][1] +
                        weighting_bins[priority][0])
            elif chance < data_parameters[weights_parameter][3] + chance_adjustment:
                days = (round(random.random() * weighting_bins[priority][3]) +
                        weighting_bins[priority][2] +
                        weighting_bins[priority][1] +
                        weighting_bins[priority][0])
            elif chance < data_parameters[weights_parameter][4] + chance_adjustment:
                days = (round(random.random() * weighting_bins[priority][4]) +
                        weighting_bins[priority][3] +
                        weighting_bins[priority][2] +
                        weighting_bins[priority][1] +
                        weighting_bins[priority][0])
            elif chance < data_parameters[weights_parameter][5] + chance_adjustment:
                days = (round(random.random() * weighting_bins[priority][5]) +
                        weighting_bins[priority][4] +
                        weighting_bins[priority][3] +
                        weighting_bins[priority][2] +
                        weighting_bins[priority][1] +
                        weighting_bins[priority][0])
            else:
                days = (round(random.random() * weighting_bins[priority][6]) +
                        weighting_bins[priority][5] +
                        weighting_bins[priority][4] +
                        weighting_bins[priority][3] +
                        weighting_bins[priority][2] +
                        weighting_bins[priority][1] +
                        weighting_bins[priority][0])
            return_date = base_date + relativedelta(days=days)
            return_date_str = return_date.strftime("%m/%d/%Y")
            return_test = 1
        else:
            # This milestone will not be met so return no date
            return_date = datetime(1, 1, 1)
            return_date_str = ''
    else:
        # The previous milestone test was not met so return no date
        return_date = datetime(1, 1, 1)
        return_date_str = ''
    return return_date, return_date_str, return_test
# END get_referral_date


def get_earlier_date(weights_parameter: list[float],
                     referral_sent_date: datetime,
                     referral_seen_date: datetime) -> tuple[datetime, str, bool]:
    """
    Calculate random earlier appointment dates that were booked for referrals that were seen. This
    is called for one referral at a time.

    Args:
      weights_parameter: a list of chances that a referral in an age bin has an earlier appointment
      referral_sent_date: the date when the referral was sent to the clinic
      referral_seen_date: the date when the referral was seen

    Returns:
      A tuple with three values:
      - The alternate, earlier appointment date, or minimum date
      - A string representation of the earlier date, or empty string
      - A boolean holding true if an alternate date was returned
    """
    days_to_seen = (referral_seen_date - referral_sent_date).days
    chance = random.random()
    delay_factor = random.random()
    delay = 0.0
    early_date = datetime(1, 1, 1)
    early_date_str = ''
    return_test = False
    if days_to_seen <= 7.0:
        if chance <= weights_parameter[0]:
            delay = delay_factor * 7.0
            return_test = True
    elif days_to_seen <= 14.0:
        if chance < weights_parameter[1]:
            delay = delay_factor * 14.0
            return_test = True
    elif days_to_seen <= 30.0:
        if chance < weights_parameter[2]:
            delay = delay_factor * 30.0
            return_test = True
    elif days_to_seen <= 60.0:
        if chance < weights_parameter[3]:
            delay = delay_factor * 60.0
            return_test = True
    elif days_to_seen <= 90.0:
        if chance < weights_parameter[4]:
            delay = delay_factor * 90.0
            return_test = True
    elif chance < weights_parameter[5]:
        delay = delay_factor * days_to_seen
        return_test = True

    if return_test:
        early_date = referral_seen_date - relativedelta(days=floor(delay))
        early_date_str = early_date.strftime("%m/%d/%Y")

    return early_date, early_date_str, return_test
# END get_earlier_date


# MAIN

# Output the referrals data set direct to a csv text file 
f = open("referrals.csv", "w")

# Column headers in first row 
record_str = (
    "Referral ID,Source Location,Provider Referred To,Location Referred To,Referral Priority,Referral Status,"
    "Date Referral Written,Date Referral Sent,Date Accepted,Date Referral Completed,Date Referral Scheduled,"
    "Date Referral Seen,Patient ID,Clinic,Date Similar Appt Scheduled,Date Patient Checked In,Date Held,"
    "Date Pending Reschedule,Date Last Referral Update,Last Referral Update By,Assigned Personnel,"
    "Organization Referred To,Reason for Hold,Referral Sub-Status,Earliest Appt Date\n")
f.write(record_str)

# Initialize referral ID #s
referral_id = 1 

# Loop over each calendar day over the given time period to create random referrals
referral_date = data_parameters['first_referral_date']  
last_referral_month = referral_date.month 
while referral_date <= data_parameters['last_referral_date']: 

    # With each new month recalculate random performance adjustments per clinic
    referral_month = referral_date.month
    if referral_month != last_referral_month:
        provider_referred_to['rate_adjustment'] = (np.random.random(len(provider_referred_to.index)) * 0.6) - 0.3
    
    # Loop over a random number of referrals for each date and create them one at a time
    num_referrals = round((random.random() * (data_parameters['maximum_referrals_daily'] -
                                              data_parameters['minimum_referrals_daily'])) +
                          data_parameters['minimum_referrals_daily'])
    print(referral_date.strftime("%m/%d/%Y"), ", ", num_referrals, " referrals")
    referral_num = 0
    while referral_num < num_referrals:

        # Initialize referral process dates
        completed_date = datetime(1, 1, 1)
        similar_seen_date = datetime(1, 1, 1)
        similar_scheduled_date = datetime(1, 1, 1)
        seen_date = datetime(1, 1, 1)
        schedule_date = datetime(1, 1, 1)
        accept_date = datetime(1, 1, 1)
        referral_written_date = datetime(1, 1, 1)
        on_hold_date = datetime(1, 1, 1)

        # Choose a random patient id
        patient_id = round(random.random() * (num_referrals * 10.0))

        # Choose a random referral source location from the reference list
        idx = round(random.random() * (source_location_count - 1))
        source_location_val = source_locations.iloc[idx, source_location_column]

        # Choose a random refer-to provider from the reference list
        idx = round(random.random() * (provider_referred_to_count - 1))
        provider_referred_to_val = provider_referred_to.iloc[idx, provider_referred_to_column]
        location_referred_to_val = provider_referred_to.iloc[idx, location_referred_to_column]
        organization_referred_to_val = provider_referred_to.iloc[idx, organization_referred_to_column]
        clinic_val = provider_referred_to.iloc[idx, clinic_column]
        rate_adjustment = provider_referred_to.iloc[idx, rate_adjustment_column]

        # Choose a random last person to update referral from the reference list
        idx = round(random.random() * (last_referral_update_by_count - 1))
        last_referral_update_by_val = last_referral_update_by.iloc[idx, last_referral_update_by_column]

        # Choose a random assignee to manage the referral from the reference list
        idx = round(random.random() * (assigned_personnel_count - 1))
        assigned_personnel_val = assigned_personnel.iloc[idx, assigned_personnel_column]

        # In case this referral ends up on hold, preselect a random reason for the hold from the reference list
        idx = round(random.random() * (reason_for_hold_count - 1))
        reason_for_hold_val = reason_for_hold.iloc[idx, reason_for_hold_column]

        # Choose a random queue substatus from the reference list
        idx = round(random.random() * (referral_substatus_count - 1))
        referral_substatus_val = referral_substatus.iloc[idx, referral_substatus_column]

        # Choose a priority at random
        idx = random.random()
        if idx <= data_parameters['urgent_priority']:
            referral_priority_val = 'Urgent'
        else:
            referral_priority_val = 'Routine'

        # Referral written dates
        idx = random.random()
        if idx < data_parameters['referral_written_weights'][0]:
            days_to_send = round(random.random() * 2.0)
        elif idx < data_parameters['referral_written_weights'][1]:
            days_to_send = round(random.random() * 3.0) + 2
        elif idx < data_parameters['referral_written_weights'][2]:
            days_to_send = round(random.random() * 5.0) + 5
        elif idx < data_parameters['referral_written_weights'][3]:
            days_to_send = round(random.random() * 10.0) + 10
        else:
            days_to_send = round(random.random() * 20.0) + 20
        referral_written_date = referral_date - relativedelta(days=days_to_send)
        referral_written_date_str = referral_written_date.strftime("%m/%d/%Y")

        # Randomly accept referrals and calculate the days to accept
        accepted = 0
        idx = random.random()
        if idx < data_parameters['accepted_rate']:
            days_to_accept = (round(random.random() * (data_parameters['days_to_accept'][1] -
                                                       data_parameters['days_to_accept'][0])) +
                              data_parameters['days_to_accept'][0])
            accept_date = referral_date + relativedelta(days=int(days_to_accept))
            accept_date_str = accept_date.strftime("%m/%d/%Y")
            accepted = 1
        else:
            accept_date = datetime(1, 1, 1)
            accept_date_str = ''
            accepted = 0

        # Randomly schedule referrals if they are accepted and calculate the days to schedule
        schedule_date, schedule_date_str, scheduled = get_referral_date(accepted,
                                                                        'scheduled_rate',
                                                                        rate_adjustment,
                                                                        'referral_scheduled_weights',
                                                                        accept_date,
                                                                        referral_priority_val)

        # Randomly see referrals if they are scheduled and calculate the days to seen
        seen_date, seen_date_str, seen = get_referral_date(scheduled,
                                                           'seen_rate',
                                                           rate_adjustment,
                                                           'referral_seen_weights',
                                                           schedule_date,
                                                           referral_priority_val)

        # Randomly select referrals to have similar appointments that aren't updated in the referral status
        # to reflect real life data quality issue
        similar_scheduled_date, similar_scheduled_date_str, similar_scheduled = (
            get_referral_date(1,
                              'similar_scheduled_rate',
                              rate_adjustment,
                              'similar_scheduled_weights',
                              referral_written_date,
                              referral_priority_val))

        # Randomly select referrals to have similar appointments checked in that aren't updated in the referral status
        # to reflect real life data quality issue
        similar_seen_date, similar_seen_date_str, similar_seen = (
            get_referral_date(similar_scheduled,
                              'similar_seen_rate',
                              rate_adjustment,
                              'similar_seen_weights',
                              similar_scheduled_date,
                              referral_priority_val))

        # Randomly select referrals to be completed, either after seen or before being seen
        # Also randomly choose earlier appt times for referrals that were seen
        delayed = False
        earlier_date_str = ''
        if (seen == 0) and (similar_seen == 0):
            completed_date, completed_date_str, completed = (
                get_referral_date(1,
                                  'not_seen_completed_rate',
                                  rate_adjustment,
                                  'not_seen_completed_weights',
                                  referral_written_date,
                                  referral_priority_val))
        else:
            either_date = max(similar_seen_date, seen_date)
            completed_date, completed_date_str, completed = (
                get_referral_date(1,
                                  'seen_completed_rate',
                                  rate_adjustment,
                                  'seen_completed_weights',
                                  either_date,
                                  referral_priority_val))
            earlier_date, earlier_date_str, delayed = (
                get_earlier_date(data_parameters['earlier_appt_weights'], referral_date, either_date))
        earlier_date_str = earlier_date_str if delayed else seen_date_str

        # Choose a random last update date after the latest process date
        latest_date = max(completed_date,
                          similar_seen_date,
                          similar_scheduled_date,
                          seen_date,
                          schedule_date,
                          accept_date,
                          referral_written_date)
        days_to_update = (round(random.random() * (data_parameters['days_to_update'][1] -
                                                   data_parameters['days_to_update'][0])) +
                          data_parameters['days_to_update'][0])
        update_date = latest_date + relativedelta(days=int(days_to_update))
        update_date_str = update_date.strftime("%m/%d/%Y")

        # Set the referral status based on process milestone dates
        referral_status = 'Pending Acceptance'
        if accepted == 1:
            referral_status = 'Accepted'
        if scheduled == 1:
            referral_status = 'Scheduled'
        if seen == 1:
            referral_status = 'Patient Seen'
        if completed == 1:
            referral_status = 'Completed'
            idx = random.random()
            if idx < data_parameters['completed_and_closed_rate']:
                referral_status = 'Closed'
        if completed == 0:
            idx = random.random()
            if idx < data_parameters['not_completed_and_closed_rate']:
                referral_status = 'Closed'
        if accepted == 0:
            idx = random.random()
            if idx < data_parameters['rejected_rate']:
                referral_status = 'Rejected'

        # Referrals in a pending status might be on hold or pending reschedule
        still_pending = 0
        if referral_status in ['Pending Acceptance', 'Accepted', 'Scheduled']:
            still_pending = 1

        # Randomly select referrals to be on hold
        holds_ok = 0
        if referral_date > holds_start_date:
            holds_ok = 1
        on_hold_date, on_hold_date_str, on_hold = (
            get_referral_date(still_pending * holds_ok,
                              'on_hold_rate',
                              0,
                              'on_hold_weights',
                              referral_date,
                              referral_priority_val))
        if on_hold == 1:
            referral_status = 'On Hold'
        else:
            reason_for_hold_val = ''

        # Randomly select referrals to be pending reschedule unless they are already on hold
        still_pending = still_pending - on_hold
        pending_reschedule_date, pending_reschedule_date_str, pending_reschedule = (
            get_referral_date(still_pending * holds_ok,
                              'pending_reschedule_rate',
                              0,
                              'pending_reschedule_weights',
                              referral_date,
                              referral_priority_val))
        if pending_reschedule == 1:
            referral_status = 'Pending Reschedule'

        # Randomly select pending referrals to be closed unless they are on hold or pending reschedule
        still_pending = still_pending - pending_reschedule
        closed = 0
        if still_pending == 1:
            idx = random.random()
            if idx < data_parameters['closed_rate']:
                referral_status = 'Closed'
                closed = 1

        # If not within the time frame to remain on hold then cancel
        cancelled = 0
        if (still_pending == 1) and (holds_ok < 1):
            referral_status = 'Cancelled'
            cancelled = 1

        # Randomly select pending referrals to be canceled unless they are on hold, pending reschedule, or closed
        still_pending = still_pending - cancelled
        if still_pending == 1:
            idx = random.random()
            if idx < data_parameters['cancelled_rate']:
                referral_status = 'Cancelled'

        # Export referral record
        referral_date_str = referral_date.strftime("%m/%d/%Y")
        record_str = (
            f'{referral_id},"{source_location_val}","{provider_referred_to_val}",'
            f'"{location_referred_to_val}","{referral_priority_val}","{referral_status}",'
            f'{referral_written_date_str},{referral_date_str},{accept_date_str},{completed_date_str},'
            f'{schedule_date_str},{seen_date_str},{patient_id},"{clinic_val}",{similar_scheduled_date_str},'
            f'{similar_seen_date_str},{on_hold_date_str},{pending_reschedule_date_str},{update_date_str},'
            f'"{last_referral_update_by_val}","{assigned_personnel_val}","{organization_referred_to_val}",'
            f'"{reason_for_hold_val}","{referral_substatus_val}",{earlier_date_str}\n')
        f.write(record_str)

        # Next referral
        referral_id = referral_id + 1
        referral_num = referral_num + 1
    # END of num referrals loop

    # Next referral date
    last_referral_month = referral_date.month
    referral_date = referral_date + relativedelta(days=1)
# END of dates loop

f.close()
