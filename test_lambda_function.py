import pytest
import boto3
import pandas as pd
from moto import mock_s3
from io import BytesIO

from lambda_function import lambda_handler

@pytest.fixture(scope='module')
def s3_client():
    with mock_s3():
        s3 = boto3.client('s3', region_name='us-east-1')
        s3.create_bucket(Bucket='tri-test-bucket')
        yield s3

@pytest.fixture(scope='module')
def csv_data():
    return b'a,b,c\n1,2,3\n4,5,6\n'

def test_lambda_handler(s3_client, csv_data):
    # Define input event and context
    event = {}
    context = {}

    # Set up mock S3 bucket and objects
    s3_client.put_object(Body=csv_data, Bucket='tri-test-bucket', Key='file1.csv')
    s3_client.put_object(Body=csv_data, Bucket='tri-test-bucket', Key='file2.csv')

    # Call the lambda handler
    result = lambda_handler(event, context)

    # Check the result
    assert result == 'Finished combining data into one csv file with no issue'

    # Check that the S3 objects were combined and written correctly
    obj = s3_client.get_object(Bucket='tri-test-bucket', Key='output-folder/combined-data.csv')
    df = pd.read_csv(BytesIO(obj['Body'].read()))
    assert len(df) == 2 * len(pd.read_csv(BytesIO(csv_data)))
