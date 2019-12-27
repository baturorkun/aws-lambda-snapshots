### Snapshot EBS Volumes of Instances

#### To include any Instance to Backup Process 

Add Tag "Backup" with value "true" 

The lambda script will select the instances has tag named Backup with value "true" or "True"

#### Cleaning Rule 

"retantion" value in event.json

#### Event Parameters (event.json) 

* account_id: Your AWS Account ID
* retantion : The day value which describe how long should they be archived.

#### Test Running & Deploy

###### Lambda Funcion Commands

`$ lambda invoke`  -> Run script once on AWS to test

`$ lambda deploy`  -> Deploy script to Lambda for scheduler task

##### Scheduled Job

You can run it automatically with different methods. The easy one is that using CloudWatch. 
You can add a events rule easily.