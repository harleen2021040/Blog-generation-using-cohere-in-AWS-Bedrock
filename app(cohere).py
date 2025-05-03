import boto3  
import botocore.config
import json
from datetime import datetime

def blog_generate_using_bedrock(blogtopic: str) -> str:
    # Building prompt for a chat model (Cohere)
    chat_history = [
        {
            "role": "USER",
            "message": f"Write a 200-word blog on the topic: {blogtopic}"
        }
    ]

    # Latest message to continue the conversation
    user_message = "Sure, please generate the blog."

    body = {
        "chat_history": chat_history,
        "message": user_message,
        "temperature": 0.7,
        "max_tokens": 512
    }

    try:
        # ✅ Corrected client name
        bedrock = boto3.client("bedrock-runtime", region_name="us-east-1",
                               config=botocore.config.Config(read_timeout=300, retries={'max_attempts': 3}))

        # ✅ Updated model to Cohere and correct input structure
        response = bedrock.invoke_model(
            body=json.dumps(body),
            modelId="cohere.command-r-plus-v1:0",
            contentType="application/json",
            accept="application/json"
        )

        response_content = response.get('body').read().decode("utf-8")
        response_data = json.loads(response_content)

        print(response_data)  # 🔍 For debugging

        blog_details = response_data["text"]  # ✅ This is where Cohere returns its reply
        return blog_details

    except Exception as e:
        print(f"Error generating the blog: {e}")
        return ""


def save_blog_details_s3(s3_key, s3_bucket, generate_blog):
    s3 = boto3.client('s3')

    try:
        s3.put_object(Bucket=s3_bucket, Key=s3_key, Body=generate_blog)
        print("Blog saved to S3")

    except Exception as e:
        print(f"Error when saving blog to S3: {e}")    


def lambda_handler(event, context):
    event = json.loads(event['body'])
    blogtopic = event['blog_topic']

    generate_blog = blog_generate_using_bedrock(blogtopic=blogtopic)

    if generate_blog:
        current_time = datetime.now().strftime('%H%M%S')
        s3_key = f"blog-output/{current_time}.txt"
        s3_bucket = 'awsbedrocapplication'
        save_blog_details_s3(s3_key, s3_bucket, generate_blog)
    else:
        print("No blog was generated")

    return {
        'statusCode': 200,
        'body': json.dumps('Blog generation is completed')
    }
