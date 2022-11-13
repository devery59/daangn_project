import boto3
from botocore.exceptions import ClientError
import os
from dotenv import load_dotenv
import json
import logging


class S3Manager:
    def __init__(self):
        self.__aws_access_key_id__ = os.getenv("AWS_ACCESS_KEY_ID")
        self.__aws_secret_access_key__ = os.getenv("AWS_SECRET_ACCESS_KEY")
        self.AWS_ACCOUNT_NUMBER = os.getenv("AWS_ACCOUNT_NUMBER")

    def create_s3_bucket(self, bucket_name):
        print("Creating a bucket :  " + bucket_name)

        s3 = boto3.client(
            's3',
            aws_access_key_id=self.__aws_access_key_id__,
            aws_secret_access_key=self.__aws_secret_access_key__)

        try:
            response = s3.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={
                    'LocationConstraint': 'ap-northeast-2'
                }
            )
            return response
        except ClientError as e:
            if e.response['Error']['Code'] == 'BucketAlreadyOwnedByYou':
                print("Bucket already exists. Enter another buckey name")
            else:
                print("Unknown error, exit.")

    def create_iam_role(self):
        iam = boto3.client(
            'iam',
            aws_access_key_id=self.__aws_access_key_id__,
            aws_secret_access_key=self.__aws_secret_access_key__)

        assume_role_policy_document = json.dumps({
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": "sts:AssumeRole",
                    "Principal": {
                        "AWS": self.AWS_ACCOUNT_NUMBER
                    },
                    "Condition": {}
                }
            ]
        })

        response = iam.create_role(
            RoleName="awesome-winter",
            AssumeRolePolicyDocument=assume_role_policy_document
        )

        return response["Role"]["RoleName"]

    def attach_role_policy(self, policy_arn, role_name):
        iam = boto3.client(
            'iam',
            aws_access_key_id=self.__aws_access_key_id__,
            aws_secret_access_key=self.__aws_secret_access_key__)
        response = iam.attach_role_policy(
            RoleName=role_name,
            PolicyArn=policy_arn
        )

        return response

    def localstack_s3bucketList(self):
        s3 = boto3.client('s3', endpoint_url="http://localhost:4566")
        response = s3.list_buckets()
        print("Existing buckets : ")
        for bucket in response["Buckets"]:
            print(f'{bucket["Name"]}')

    def localstack_create_bucket(self, bucket_name, region='ap-northeast-2'):
        try:
            s3_client = boto3.client("s3", region_name=region, endpoint_url="http://localhost:4566")
            location = {'LocationConstraint': region}
            s3_client.create_bucket(Bucket=bucket_name,
                                    CreateBucketConfiguration=location)
        except ClientError as e:
            logging.error(e)
            return False
        return True


def main():
    load_dotenv()
    s3manager = S3Manager()

    # Using AWS IAM
    bucket_name = input("Enter new bucket name : ")
    response_bucket = s3manager.create_s3_bucket(bucket_name)
    print("Bucket : " + str(response_bucket))
    response_role = s3manager.create_iam_role()
    print("Role name : " + str(response_role))
    readOnlyPolicyArn = os.getenv("s3ReadOnlyPolicyArn")
    response_attachPolicy = s3manager.attach_role_policy(readOnlyPolicyArn, response_role)
    print(response_attachPolicy)

    # Using localStack ( docker compose )
    response_localstack = s3manager.localstack_create_bucket("test2-bucket")
    print(response_localstack)
    s3manager.localstack_s3bucketList()



main()
