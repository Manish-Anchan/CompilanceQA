import os
import time
import logging
import requests
from pytubefix import YouTube
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
        """Downloads a YouTube video to a local file using pytubefix."""
        logger.info(f"Downloading YouTube video via pytubefix: {url}")
        
        try:
            yt = YouTube(url, use_po_token=True)
            # Grab the highest resolution pre-merged MP4 (usually 720p)
            stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
            
            if not stream:
                raise Exception("No standard MP4 stream available for this video.")
                
            stream.download(filename=output_path)
            logger.info("Download complete.")
            return output_path
            
        except Exception as e:
            raise Exception(f"YouTube Download Failed (pytubefix): {str(e)}")


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