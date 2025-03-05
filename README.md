# AniMatch is a AWS based server-less party game demo
This demo using predefined anime labels and mediapipe model for game score calculation.

# Files/Datasets

Datasets source: “Tagged Anime Illustrations” (Kaggle) and Google Custom Search




# Deployment
In total, two AWS lambda function, one docker image (pushed to Amazon ECR), 2 S3 buckets(one for anime image store, one for webpage public access)

NOTE!
Add your own api in index.html:const RANDOM_ANIME_API = "————your_lambda_link————";
const MEDIAPIPE_API    = "————your_lambda_link————";

