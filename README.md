# AniMatch is a AWS based server-less party game demo
This demo using predefined anime labels and mediapipe model for game score calculation.
## High-Level Architecture
🎯 Step 1: Website select a random anime image from S3;  
📤 Step 2: User uploads his/her own photo;  
🖥️ Step 3: Docker container (Mediapipe) started and return landmark;  
🔢 Step 4: Similarity score computed.  

# Files/Datasets

Datasets source: “Tagged Anime Illustrations” (Kaggle) and Google Custom Search

## Anime image selection
<img src="./ReadmeRelatedImages/HumanLandmark.png" width="900" />  
The first one handles anime image selection. When a user clicks 'Get Random Anime Image,' an API call triggers an AWS Lambda function.  
The function selects an image from an S3 bucket, where images are organized into labeled folders.  
With the anime image selected, the next step is analyzing human face:  
## Mediapipe docker integration
<img src="./ReadmeRelatedImages/RandomAnimeSelection.png" width="900" /> 
When a user uploads a photo, another AWS Lambda function is triggered.   
It pulls a Docker container— one that we built from scratch, packaged with a Mediapipe model, and then pushed to Amazon ECR.  
Inside this container, the Mediapipe model  identifying key expressions of eye and mouth,  returning these features back.  
At this point, we have both the anime expression and user's landmarks ready, so we can now compute the similarity score.  

## Scoreing Formulation

The logic behind calculation is pretty neat, only by comparing eye and mouth openness.  T
he closer the values, the higher the score.  
Given the cross-domain comparison between human faces and anime characters, we map openness values as follows:  
If the value is less than or equal to 0.2, we consider it closed (zero).If the value is greater then or equal to 0.8, we consider it open (one).Everything in between remains unchanged. 
In this case, the user closely matches the anime expression, resulting in a 100% score.
<img src="./ReadmeRelatedImages/SimilarityFormulation.png" width="900" /> 




# Deployment
In total, two AWS lambda functions, one docker image (pushed to Amazon ECR), 2 S3 buckets(one for anime image store, one for webpage public access)

## Frontend page 
### HTTP API 
As Albert E..

NOTE!  
Add your own api in index.html:const RANDOM_ANIME_API = "————your_lambda_link————";  
const MEDIAPIPE_API    = "————your_lambda_link————";  

## Docker package
### Push to AWS ECR
