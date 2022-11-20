import json
import datadotworld as dw
import pandas as pd
import os
import boto3
from io import StringIO

s3_resource = boto3.resource('s3')

def df_upload(df,output_bucket,output_key):
    csv_buffer = StringIO()
    df.to_csv(csv_buffer,index=False)
    s3_resource.Object(output_bucket, output_key).put(Body=csv_buffer.getvalue())


def lambda_handler(event, context):

    output_bucket=os.environ.get("Raw_Bucket")
    print(output_bucket)
    output_prefix="uber"

    dataset=dw.DataDotWorld(config=dw.EnvConfig()).load_dataset('rmiller107/travel-time-uber-movement')

    for table,df in dataset.dataframes.items():
        df["city"]=table.split("travel_times_")[1]
        df_upload(df,output_bucket,output_key=f"{output_prefix}/{table}.csv")
    return {
        "statusCode": 200,
        "body": json.dumps(
            {
                "message": "hello world",
            }
        ),
    }
