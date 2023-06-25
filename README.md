< [Portfolio](https://907sjl.github.io) | [Full Report](https://907sjl.github.io/pdf/Referral%20Wait%20Time.pdf) | [Overview](https://907sjl.github.io/referrals_powerbi/referrals_report) 

One way to measure access to care is timeliness.  Long delays to see a healthcare provider can speak to availability issues, either a lack of resources or inefficiencies that result in a less than optimal conversion of referrals into appointments. Long delays can also speak to accomodation issues or accessibility issues if patients have difficulty attending their scheduled appointments.
This project is an example of a report that I created to look at the process times for referred patients at specialty clinics. 

## Why Power BI? 
Why would I choose Power BI to create this report?  Power BI reports are both quick to manipulate and page formatted.  The combination of Power Query M Scripts and DAX measure calculations makes Power BI extremely nimble, as does the visual design interface for building reports.  There is a plethora of community support and freely accessible training for those who are new to Power BI.  A dashboard created in Power BI can also function as a page formatted report.  If you are faced with a typical business intelligence, rapid and iterative prototyping scenario where exploratory analysis is refined into repeatable process measurement then Power BI is a good choice.    

## Overview
Click [here](https://907sjl.github.io/referrals_powerbi/referrals_report) for an overview of the report.  The numerical values in these reports are fabricated and do not represent any real healthcare organization. 

## Data sources 
For the purposes of demonstration this example report loads data from three Comma Separated Values files.  The data in these files has been fabricated as an example.  It does not represent any real healthcare organization.   

- Referrals.csv
: A file containing one row for each referral and columns with the dates when each referral reached a process milestone.  Other columns are also included that are helpful for monthly monitoring.    

- DirectSecureMessages.csv
: A file containing one row for each Direct Secure Message about a patient that was sent to a referral inbox. These are used to measure how often messages are used in place of referrals.     

- StandardCalendar.csv
: Contains the data for the standard date dimension table used across reports.     

## Power Query ELT
![A list of Power Query groups](images/query_groups.jpg)    
Four custom groups and the one default group organize the Power Query loads, transforms, and ancillary constructs. 

### Parameters and Functions
![Contents of the parameters group](images/parameters_group.jpg)    
Parameters are used here for two purposes.  The **data_date** parameter is used to fix the effective date of this report to a specific date.  Many of the measures in this report are based on the age of a referral.  Since this example is loaded from static files the effective date must be fixed in time in order to avoid every referral aging out of range.

```
= Table.AddColumn(#"Set Data Types", "Days to Accept", each if ([Date Accepted] = null) 
  then Duration.Days(Date.From(data_date) - [Date Referral Sent]) 
  else Duration.Days([Date Accepted] - [Date Referral Sent]))
```    
The **data_date** parameter is used to calculate the number of days that a referral waited to reach each of the process milestones.    

![Snapshot of the file Source configuration](images/file_path_parts.jpg)    
The **data_path** parameter provides a single, convenient location to set the directory where the report can find the data files to load.  The *Source* step of each source table references this parameter along with one of the other parameters containing the name of the file to load.    

![Contents of the functions group](images/functions_group.jpg)    
This Power Query ELT makes use of the **GetAgeCategory** function to template a column transform.  The function assigns a distribution grouping bin to the number of days leading up to a process milestone.  Encapsulating business logic into functions places that logic in an easy to find location.  It also templates a transformation that may potentially be used more than once.  Changes can be made in a single place.    

```
= (Days as any) as any => 
let
    Source = (if Days = null then null 
              else if Days <= 7 then "7d" 
              else if Days <= 14 then "14d" 
              else if Days <= 30 then "30d" 
              else if Days <= 60 then "60d" 
              else if Days <= 90 then "90d" else ">90d")
in
    Source
```    
The number of days is the parameter and the return value is the grouping bin name.    

### Data Loads
![Contents of the data loads group](images/data_loads_group.jpg)    
The Data Loads group contains the extracts and loads from the source data files.  **Referral**, **Direct Secure Message**, and **Standard Calendar** each refer to the similarly named CSV file data source.  

### Referral Table 
The query for the **Referral** table loads records of referrals and processing dates from referrals.csv.   
![Referral source file columns](images/referrals_source_columns.jpg)    
This source file contains a horizontal list of columns representing the dates that each referral first reached processing milestones such as the date written, date sent, accepted, scheduled, and seen.

![Referral table transforms #1](images/referral_steps_1.jpg)    
Table transforms add columns that indicate whether or not the referral has reached each process milestone.  These are used by DAX measures in the report.    

Adding calculated columns in Power Query balances out the overall time spent waiting for calculations while working with Power BI reports.  Calculations and filters written into DAX measures are processed when the filters change, the view page is changed, or visualization properties are changed.  In my time working with Power BI I have spent more time waiting for spinning wheel icons than actually working.  Loading a calculated column in Power Query shifts some processing to the data refresh.  

![Referral table transforms #2](images/referral_steps_2.jpg)    
The number of days between milestones are also added to the table as calculated columns.  These columns are used to age referrals from the date when they are sent.  These ages are used to calculate median process timings. 

![Referral table transforms #3](images/referral_steps_3.jpg)    
Along the lines of shifting work to the data refresh, the query calculates a set of extended date columns used by DAX measures in the report.  These date manipulations are present in most of the measures that are visualized.  There are useful functions and techniques in DAX to calculate time phased measures without these calculated date columns, but this would come at the cost of more complicated DAX measures and more processing when slicer values change or a new page is selected.    

### Processing Time Table  
![Processing Time query steps](images/processing_time_steps.jpg)    
**Processing Time** is a pivoted transformation of the referral process metrics into a vertical fact table rather than a horizontal list of milestone attributes.  Doing so grants the ability to filter visuals on specific metrics and apply the same aggregation across one or more selected metrics.  Using this data structure also simplifies the use of bar charts to place different metrics side by side for comparison.    

Pivoting a horizontal list of milestone columns into a vertical fact table results in a simplified data model in that there are fewer dimensions playing a single role.  There is a single relationship between the dimension table and the fact table instead of multiple sub-classes of age category for each process metric.    

The transforms:
1. Reference the source **Referrals** table
1. Select the columns that are relevant for this table
1. Unpivot from a horizontal list of milestone dates and times to a vertical list
1. Tag each milestone wait time with an age category (using the **GetAgeCategory** function)
1. Clean up the source file naming and data types

![Days to milestones example](images/days_to_milestone_example.jpg)    
Care has to be taken with this fact table because the days to each referral milestone are not additive.  In the example above the days until seen includes the days to accept and the days until scheduled.  The total days across all milestones is 13 days, and that is meaningless.  The median days to any one milestone across all referrals is meaningful, however.    

### Direct Secure Message Table 
The query for the **Direct Secure Message** table loads records of messages to referral inboxes from DirectSecureMessages.csv.  The query simply loads the file, typecasts, and renames columns.  These records are used to evaluate how often referrals are used to acquire new patients versus direct messaging.   

### Standard Calendar Table 
The query for the **Standard Calendar** table loads records of calendar dates and their pivotal attributes from StandardCalendar.csv.  This query simply loads the file and typecasts columns.  These records are used to create the date dimension for the report.  This dimension will play many roles in the data model.   

### Dimension Tables 
![Contents of the dimensions group](images/dimensions_group.jpg)    
The queries in the Dimensions group fill tables representing the pivotal dimensions for reporting.  These tables can be related to multiple other tables that contain facts used in measures.  They can also contain attributes used to sort or filter dimension values in visualizations by something other than the dimension name.    

Three dimensions are sourced directly from the report definition.  They are entered into the Power Query and stored as JSON: 
- **Age Category** is a table of bins used to group referrals in timing distributions.  
- **Process Metric** is a table of referral process milestones and other time calculations used to monitor performance.  
- **Test of CRM Use** is a table of measure names used to test how often a clinic uses their Clinic Referral Management system versus only using the clinic schedule book for new patients.    

The **Clinic** dimension is sourced from the **Referral** table and represents the list of unique clinic names where referrals are sent.    

### Other Tables 
![Contents of the Other Queries group](images/other_group.jpg)    
The default Other Queries group has one remaining table that doesn't fit with the other groups.  The **Report Measure** table is used to place separate metrics side-by-side in bar charts with axis labels.  Measures are added to a visualization by filtering on them instead of adding them to the visualization design.    

![Report Measure table sample data](images/measure_table.jpg)    
The records of the **Report Measure** table are entered into the Power Query and stored as JSON.  The name of each measure is stored along with columns that can be used to group measures together.  Bundles of related measures can be selected for a visualization by filtering on these columns.    

A DAX measure surfaces data for selected measures using a SWITCH statement on the measure name to pair it with the corresponding formula in DAX.  

## Power BI Data Model 
<a href="images/data_model.jpg"><img alt="Data model ERD" src="images/data_model.jpg?raw=true"/></a> 
Three tables host measures that are surfaced in report visualizations.  The **Referral**, **Processing Time**, and **Direct Secure Message** tables contain fact values.    

Specific data dimensions are persisted into tables due to their values existing in multiple fact tables, or their values are sorted by a column other than their description.  

![Age category table with sort by column](images/age_category_sort_by.jpg)    
The **Age Category** dimension table has an added column with a pre-defined sort order.  The sequence of the sort order reinforces the contextual meaning of the dimension name.  This sorting is neither based on alphabetical order nor volume of data.  This dimension's name column has its sort order overriden by the SortOrder column.     

![Clinic name slicer on report page](images/clinic_slicer.jpg)    
This slicer is an example of filtering a dimension table versus an attribute of a table.  The **Clinic** dimension table has one-to-many relationships to both the **Referral** and **Direct Secure Message** tables.  If this slicer were connected to the Clinic column in either of those two tables it would only filter the records in the table that the slicer was connected to.  Connecting the slicer, or any filter, to the **Clinic** table filters both of the tables that it is related to.  Filtering the **Referral** table will also filter the **Processing Time** table by transition since **Referral** acts as a dimension in that relationship.    

The **Standard Calendar** table is the time dimension.  It is a table of calendar dates and attributes such as year and month that are used to filter and sort visualizations by date.    

**Standard Calendar** participates in multiple relationships to both the **Referral** and **Direct Secure Message** tables.  Each of these relationships represents a role that dates play in measures.  The date when a referral is sent or the date when a referral is placed on hold, for example.  A single, more generalized date dimension creates a simpler data model compared to sub-classes of date dimensions for every role.  A single date slicer in a report filters measures by different dates using the USERELATIONSHIP function in DAX.    

## Power BI Report

Click [here](https://907sjl.github.io/referrals_powerbi/referrals_report) for an overview of the report.  The following sections describe the DAX measures behind some of the visualizations.    

This report surfaces operational metrics and process timings to convert referred patients to attended appointments.    

### Referral Status 
![State chart for a referral](images/referral_states.png)    
A referral will be in one of eight states from a process perspective.  A referral is written in the Clinic Referral Management system then sent to the specialty clinic.  The referral is also considered pending acceptance when it is sent.  At that point the referral is either accepted, cancelled, rejected, or sometimes closed because the referral must be forwarded to another organization.  The clinic accepts and schedules a referred patient when the case has been reviewed.  The patient is then seen and the referral is completed with a visit summary.    

### Volume of Referrals After 90 Days 
![Bar chart of referral volume after 90 days](images/volume_sent_90d.jpg)    

This horizontal bar chart represents the volume of referrals sent to a clinic alongside the number of those referrals that were canceled, rejected, or closed without being seen.  The referrals included in this visualization are all aged 90 days from the date they were sent to the clinic.  The timing for a referral to be scheduled, seen, and completed is calculated after 90 days.  The volumes in this bar chart explain the population size for the median timing metrics.    

This visualization is built upon a few layers of DAX measures.  
```
Count Sent after 90d = 
  MAX(
    CALCULATE(DISTINCTCOUNTNOBLANK(Referral[Referral ID])
      , KEEPFILTERS(Referral[# Sent] > 0)
      , USERELATIONSHIP('Standard Calendar'[Date], Referral[Date Reported after 90d]))
    , 0)
```    
The core layer calculates the number of referrals sent to the clinic that aged 90 days.  Two calculated columns from the Power Query assist with this measure.  **# Sent** is either 1 or 0 and sums to the number of referrals sent.  The **Date Reported after 90d** column adds 90 days to the date the referral was sent.  The DAX function DATEADD could also be used but at the expense of more frequent processing when each visualization is rendered.  The 90 day age is a static concept that is built into the report.    

```
Count Canceled after 90d = 
MAX(
  CALCULATE([Count Sent after 90d] 
    , KEEPFILTERS(Referral[Referral Status] IN {"Cancelled"})
  ) 
  , 0) 

Count Rejected after 90d = 
MAX(
  CALCULATE([Count Sent after 90d] 
    , KEEPFILTERS(Referral[Referral Status] IN {"Rejected"})
  ) 
  , 0) 
```    
The counts of canceled and rejected referrals build on to the **Count Sent after 90d** measure by adding filters to focus on those specific subsets of referrals that were sent.  The canceled and rejected referrals are highlighted here because they are not considered in the percentage of referrals seen.  It is possible to reach 100%.    

```
Count Referrals Closed WBS after 90d = 
MAX(
  CALCULATE([Count Sent after 90d] 
    , KEEPFILTERS( Referral[Referral Status] IN {"Completed", "Closed"} 
                   && ISBLANK(Referral[Date Referral Seen]) 
                   && ISBLANK(Referral[Date Patient Checked In]))
  ) 
  , 0) 
```    
Referrals are counted as closed without being seen if they are sent but then completed or closed without any data to indicate that the patient was seen.  These referrals are also removed from the percentages of referrals that are seen.    

An additional layer of DAX overlays these measures and surfaces them to the bar chart visual.  This is the **Report Measure** table described in the Power Query ELT.  **Report Measure** holds a measure that acts as a switchboard of measures.  

```
Measured Whole Number Value = 
  SWITCH(MIN('Report Measure'[Measure Name]), 
    "Count Linked after 90d", [Count Linked after 90d], 
    "Count Scheduled after 90d", [Count Scheduled after 90d],
    "Count Tagged as Seen after 90d", [Count Tagged as Seen after 90d],
    "Count Seen or Checked In after 90d", [Count Seen or Checked In after 90d],
    "Count Rejected after 90d", [Count Rejected after 90d],
    "Count Canceled after 90d", [Count Canceled after 90d],
    "Count Referrals Closed WBS after 90d", [Count Referrals Closed WBS after 90d],
    "Count Sent after 90d", [Count Sent after 90d],
    ...
```    
This measure is assigned to the bar chart visual as the X-axis.  
![X-axis of volume sent](images/volume_sent_x_axis.jpg)    
This allows multiple, separate measures like the ones shown above to appear side-by-side as bars with labels in the Y-axis.  This also allows measures to be included using filters on the visual.    
![Filters on volume sent](images/volume_sent_x_measure_filter.jpg)    
This visual includes all measures with an attribute value of **Sent** in the **Milestone** column.  If this report is published interactively in the cloud service this also introduces interesting capabilities for the viewer to customize the page.    

### Display Folders for Data Elements
