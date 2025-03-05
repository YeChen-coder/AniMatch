import json
import boto3
import random

s3 = boto3.client("s3")
BUCKET_NAME = "——yourAnimeImageBucketName——"

def lambda_handler(event, context):
    # Step 1: Randomly choose a folder/category
    folder_names = ["CECM", "CEOM", "OECM", "OEOM"]
    chosen_folder = random.choice(folder_names)
    prefix = chosen_folder + "/"

    # Step 2: List objects within that folder
    response = s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix=prefix)
    if "Contents" not in response or not response["Contents"]:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": f"No images found in folder {chosen_folder}"}),
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            }
        }

    # Filter out any keys that are just the "folder/" itself (subfolders, etc.)
    all_keys = [
        obj["Key"]
        for obj in response["Contents"]
        if not obj["Key"].endswith("/")
    ]
    
    if not all_keys:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": f"No valid images found in folder {chosen_folder}"}),
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            }
        }

    # Step 3: Randomly pick an image key from that folder
    random_key = random.choice(all_keys)

    # Step 4: Generate a presigned URL
    presigned_url = s3.generate_presigned_url(
        "get_object",
        Params={"Bucket": BUCKET_NAME, "Key": random_key},
        ExpiresIn=3600  # 1 hour expiration
    )

    # Step 5: Return the category(folder name) and the image URL
    return {
        "statusCode": 200,
        "body": json.dumps({
            "anime_label": chosen_folder,
            "anime_key": random_key,
            "image_url": presigned_url
        }),
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*"
        }
    }
