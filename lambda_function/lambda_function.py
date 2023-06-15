import boto3
import json
import boto3 
import pandas as pd 
import io

def lambda_handler(event, context):
    # create s3 client 
    s3_client = boto3.client("s3")
    row_count = 0
    df_list = []
    bucket_name = "tri-test-bucket"
    response = s3_client.list_objects_v2(Bucket=bucket_name,Prefix='')
    for file in response['Contents']:
        if file['Key'].endswith('.csv'):
            obj = s3_client.get_object(Bucket=bucket_name, Key=file['Key'])
            df = pd.read_csv(io.BytesIO(obj['Body'].read()))
            row_count +=len(df)
            df_list.append(df)
            
    # combine all df 
    df_combined = pd.concat(df_list)
    
    # Data quality check 
    ## Check for total row count 
    row_count_check = (len(df_combined)==row_count)
    
    # Save combined df to output folder 
    output_bucket = 'tri-test-bucket'
    output_folder = 'output-folder/'
    output_filename = 'combined-data.csv'
    output_key = output_folder + output_filename
    
    #Save df to output folder 
    csv_buffer = io.StringIO()
    df_combined.to_csv(csv_buffer,index=False)
    s3_client.put_object(Body=csv_buffer.getvalue(),Bucket=output_bucket,Key=output_key)
    
    if row_count_check:
        return 'Finished combining data into one csv file with no issue'
        
    else:
        return 'Finished combining data into one csv file with differences in row count'
        