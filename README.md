### Creating Snapshot for EBS Volumes of Instances

#### To include any Instance to Backup Process 

Add Tag "Backup" with value "true" 

The lambda script will select the instances has tag named Backup with value "true" or "True"

#### Cleaning Rule 

"retention" value in event.json

### Settings

#### Event Parameters (event.json) 

* account_id: Your AWS Account ID
* retention : The day value which describe how long should they be archived.
* keep_last_snap: Do not delete last snapshot

#### AWS Credentials

If you set AWS Credentials already in OS, you don't need write your credentials to config.yaml. However if you have not yet, you must write your credentials to  config.yaml. 

* aws_access_key_id: XXXXX
* aws_secret_access_key: XXXXXXXXXXXX

This setting is required just "lambda invoke" command. 

#### Test Running & Deploy

###### Lambda Funcion Commands

`$ lambda invoke`  -> Run script once on AWS to test

`$ lambda deploy`  -> Deploy script to Lambda for scheduler task

##### Scheduled Job

You can run it automatically with different methods. The easy one is that using CloudWatch. 
You can add a events rule easily.