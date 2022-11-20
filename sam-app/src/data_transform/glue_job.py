import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.dynamicframe import DynamicFrameCollection
from awsglue.dynamicframe import DynamicFrame
from pyspark.sql import functions as F

args = getResolvedOptions(sys.argv, ["JOB_NAME"])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args["JOB_NAME"], args)

args = getResolvedOptions(sys.argv,
                            ['source_bucket',
                            'output_bucket',
                            'region'])
source_bucket=args["source_bucket"]
dl_bucket=args["output_bucket"]

# Script generated for node Custom Transform
def MyTransform(glueContext, dfc) -> DynamicFrameCollection:
    df=dfc.select(list(dfc.keys())[0]).toDF()
    df=df.withColumn("dates",F.split(df["date_range"],",").getItem(0))\
        .withColumn("date_range_frequency",F.split(df["date_range"],",").getItem(1))\
            .withColumn("date_range_type",F.split(df["date_range"],",").getItem(2))
    df=df.withColumn("date_range_start",F.split(df["dates"]," - ").getItem(0))\
        .withColumn("date_range_end",F.split(df["dates"]," - ").getItem(1))
    df=df.drop("dates","date_range")
    dyf=DynamicFrame.fromDF(df,glueContext,"split time")
    return (DynamicFrameCollection({"CustomTransform_node":dyf},glueContext))

# Script generated for node S3 bucket
S3bucket_node1 = glueContext.create_dynamic_frame.from_options(
    format_options={
        "quoteChar": '"',
        "withHeader": True,
        "separator": ",",
        "optimizePerformance": False,
    },
    connection_type="s3",
    format="csv",
    connection_options={"paths": [f"s3://{source_bucket}/uber/"], "recurse": True},
    transformation_ctx="S3bucket_node1",
)

# Script generated for node Custom Transform
CustomTransform_node = MyTransform(glueContext, DynamicFrameCollection({"S3bucket_node1": S3bucket_node1}, glueContext))

# Script generated for node Select From Collection
SelectFromCollection_node = SelectFromCollection.apply(dfc=CustomTransform_node, key=list(CustomTransform_node.keys())[0], transformation_ctx="CustomTransform_node")


# Script generated for node S3 bucket
S3bucket_node3 = glueContext.write_dynamic_frame.from_options(
    frame=SelectFromCollection_node,
    connection_type="s3",
    format="glueparquet",
    connection_options={
        "path": f"s3://{dl_bucket}/uber",
        "partitionKeys": ["city"],
    },
    format_options={"compression": "uncompressed"},
    transformation_ctx="S3bucket_node3",
)

job.commit()
