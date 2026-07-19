import os
import time
import logging
import requests
from azure.identity import DefaultAzureCredential

logger = logging.getLogger("video-indexer")

class VideoIndexerService:
    def __init__(self):
        self.account_id = os.getenv("AZURE_VI_ACCOUNT_ID")
        self.location = os.getenv("AZURE_VI_LOCATION")
        self.subscription_id = os.getenv("AZURE_SUBSCRIPTION_ID")
        self.resource_group = os.getenv("AZURE_RESOURCE_GROUP")
        self.vi_name = os.getenv("AZURE_VI_NAME", "vedioindexeryt")
        self.credential = DefaultAzureCredential()

    def get_access_token(self):
        """Generates an ARM Access Token."""
        try:
            token_object = self.credential.get_token("https://management.azure.com/.default")
            return token_object.token
        except Exception as e:
            logger.error(f"Failed to get Azure Token: {e}")
            raise

    def get_account_token(self, arm_access_token):
        """Exchanges ARM token for Video Indexer Account Token."""
        url = (
            f"https://management.azure.com/subscriptions/{self.subscription_id}"
            f"/resourceGroups/{self.resource_group}"
            f"/providers/Microsoft.VideoIndexer/accounts/{self.vi_name}"
            f"/generateAccessToken?api-version=2024-01-01"
        )
        headers = {"Authorization": f"Bearer {arm_access_token}"}
        payload = {"permissionType": "Contributor", "scope": "Account"}
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code != 200:
            raise Exception(f"Failed to get VI Account Token: {response.text}")
        return response.json().get("accessToken")

    def download_youtube_video(self, url, output_path="temp_video.mp4"):
        """Downloads a YouTube video using a RapidAPI proxy to bypass bot detection."""
        logger.info(f"Downloading YouTube video via RapidAPI proxy: {url}")
        
        try:
            # Extract video ID from URL
            if "youtu.be/" in url:
                video_id = url.split("youtu.be/")[1].split("?")[0]
            elif "v=" in url:
                video_id = url.split("v=")[1].split("&")[0]
            else:
                raise Exception("Invalid YouTube URL format. Could not extract video ID.")
                
            api_url = "https://ytstream-download-youtube-videos.p.rapidapi.com/dl"
            querystring = {"id": video_id}
            
            headers = {
                'x-rapidapi-key': os.getenv("RAPIDAPI_KEY"),
                'x-rapidapi-host': "ytstream-download-youtube-videos.p.rapidapi.com",
                'Content-Type': "application/json"
            }
            
            logger.info(f"Requesting download links from RapidAPI for video ID: {video_id}")
            response = requests.get(api_url, headers=headers, params=querystring)
            
            if response.status_code != 200:
                raise Exception(f"RapidAPI failed: {response.text}")
                
            data = response.json()
            
            # Find the best pre-merged MP4 format (usually format 18)
            download_url = None
            if "formats" in data:
                for fmt in data["formats"]:
                    if "mp4" in fmt.get("mimeType", "").lower():
                        download_url = fmt.get("url")
                        break
            
            if not download_url:
                raise Exception("No standard MP4 stream found in RapidAPI response.")
                
            # Download the actual MP4 file to disk
            logger.info("Downloading raw MP4 stream to disk...")
            video_response = requests.get(download_url, stream=True)
            if video_response.status_code != 200:
                raise Exception(f"Failed to download MP4 stream: HTTP {video_response.status_code}")
                
            with open(output_path, 'wb') as f:
                for chunk in video_response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        
            logger.info("Download complete.")
            return output_path
            
        except Exception as e:
            raise Exception(f"YouTube Download Failed (RapidAPI): {str(e)}")


    def upload_video(self, video_path, video_name):
        """Uploads a LOCAL FILE to Azure Video Indexer."""
        arm_token = self.get_access_token()
        vi_token = self.get_account_token(arm_token)

        api_url = f"https://api.videoindexer.ai/{self.location}/Accounts/{self.account_id}/Videos"
        
        params = {
            "accessToken": vi_token,
            "name": video_name,
            "privacy": "Private",
            "indexingPreset": "Default",
        }
        
        logger.info(f"Uploading file {video_path} to Azure...")
        
        with open(video_path, 'rb') as video_file:
            files = {'file': video_file}
            response = requests.post(api_url, params=params, files=files)
        
        if response.status_code != 200:
            raise Exception(f"Azure Upload Failed: {response.text}")
            
        return response.json().get("id")

    def wait_for_processing(self, video_id):
        """Polls status until complete."""
        logger.info(f"Waiting for video {video_id} to process...")
        while True:
            arm_token = self.get_access_token()
            vi_token = self.get_account_token(arm_token)
            
            url = f"https://api.videoindexer.ai/{self.location}/Accounts/{self.account_id}/Videos/{video_id}/Index"
            params = {"accessToken": vi_token}
            response = requests.get(url, params=params)
            data = response.json()
            
            state = data.get("state")
            if state == "Processed":
                return data
            elif state == "Failed":
                raise Exception("Video Indexing Failed in Azure.")
            elif state == "Quarantined":
                raise Exception("Video Quarantined (Copyright/Content Policy Violation).")
            
            logger.info(f"Status: {state}... waiting 30s")
            time.sleep(30)

    def extract_data(self, vi_json):
        """Parses the JSON into our State format."""
        transcript_lines = []
        for v in vi_json.get("videos", []):
            for insight in v.get("insights", {}).get("transcript", []):
                transcript_lines.append(insight.get("text"))
        
        ocr_lines = []
        for v in vi_json.get("videos", []):
            for insight in v.get("insights", {}).get("ocr", []):
                ocr_lines.append(insight.get("text"))
                
        return {
            "transcript": " ".join(transcript_lines),
            "ocr_text": ocr_lines,
            "video_metadata": {
                "duration": vi_json.get("summarizedInsights", {}).get("duration", {}).get("seconds"),
                "platform": "youtube"
            }
        }