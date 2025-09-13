from twelvelabs import TwelveLabs
import requests
import sys
import os

class TwelveLabsService:
    
    def __init__(self, api_key=None):
        if api_key is None:
            api_key = os.environ.get('TWELVELABS_API_KEY', '')
        self.api_key = api_key
        self.client = TwelveLabs(api_key=api_key)
    
    def check_connection(self):
        try:
            if not self.api_key:
                return {"status": "error", "message": "Missing TwelveLabs API key"}
            
            url = "https://api.twelvelabs.io/v1.3/health"
            headers = {
                "accept": "application/json",
                "x-api-key": self.api_key
            }
            
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                return {"status": "ok", "message": "Twelve Labs connection successful"}
            else:
                return {"status": "error", "message": f"Failed to connect to Twelve Labs: Status {response.status_code}"}
        except Exception as e:
            return {"status": "error", "message": f"Error connecting to Twelve Labs: {e}"}

    def get_indexes(self):
        try:
            print("Fetching indexes...")
            if not self.api_key:
                print("No API key available")
                return []
            
            url = "https://api.twelvelabs.io/v1.3/indexes"
            headers = {
                "accept": "application/json",
                "x-api-key": self.api_key
            }
            
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                result = []
                for index in data.get('data', []):
                    result.append({
                        "id": index['_id'],
                        "name": index['index_name']
                    })
                return result
            else:
                print(f"Failed to fetch indexes: Status {response.status_code}")
                return []
        except Exception as e:
            print(f"Error fetching indexes: {e}")
            return []
    
    def get_videos(self, index_id):
        try:
            if not self.api_key:
                print("No API key available")
                return []
            
            url = f"https://api.twelvelabs.io/v1.3/indexes/{index_id}/videos"
            headers = {
                "accept": "application/json",
                "x-api-key": self.api_key
            }
            
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                result = []
                for video in data.get('data', []):
                    system_metadata = video.get('system_metadata', {})
                    hls_data = video.get('hls', {})
                    thumbnail_urls = hls_data.get('thumbnail_urls', [])
                    thumbnail_url = thumbnail_urls[0] if thumbnail_urls else None
                    video_url = hls_data.get('video_url')
                    
                    result.append({
                        "id": video['_id'],
                        "name": system_metadata.get('filename', f'Video {video["_id"]}'),
                        "duration": system_metadata.get('duration', 0),
                        "thumbnail_url": thumbnail_url,
                        "video_url": video_url,
                        "width": system_metadata.get('width', 0),
                        "height": system_metadata.get('height', 0),
                        "fps": system_metadata.get('fps', 0),
                        "size": system_metadata.get('size', 0)
                    })
                return result
            else:
                print(f"Failed to fetch videos: Status {response.status_code}")
                return []
        except Exception as e:
            print(f"Error fetching videos for index {index_id}: {e}")
            return []
    
    def analyze_video(self, video_id):
        try:
            prompt = """Provide a clear and organized overview of the video, capturing its main theme, purpose, and progression of ideas.

Describe all significant topics, arguments, and perspectives in detail, ensuring that no relevant point is overlooked.

Incorporate observations of visual and auditory elements such as gestures, expressions, tone, and contextual visuals that enrich understanding."""
            analysis_response = self.client.analyze(
                video_id=video_id,
                prompt=prompt
            )
            return analysis_response.data
        except Exception as e:
            print(f"Error analyzing video {video_id}: {e}")
            raise e

    def get_video_details(self, index_id, video_id):
        if not hasattr(self, 'client') or not getattr(self, 'client', None):
            return None
        if not self.api_key:
            return None
        url = f"https://api.twelvelabs.io/v1.3/indexes/{index_id}/videos/{video_id}?embed=false"
        headers = {
            "accept": "application/json",
            "x-api-key": self.api_key,
            "Content-Type": "application/json"
        }
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Failed to get video details: Status {response.status_code}")
                return None
        except Exception as e:
            print(f"Exception getting video details: {str(e)}")
            return None

    def get_video_thumbnail(self, index_id, video_id):
        if not hasattr(self, 'client') or not getattr(self, 'client', None):
            print("[DEBUG] No client available", file=sys.stderr)
            return None
        if not self.api_key:
            print("[DEBUG] No API key available", file=sys.stderr)
            return None
        url = f"https://api.twelvelabs.io/v1.3/indexes/{index_id}/videos/{video_id}/thumbnail"
        headers = {
            "accept": "application/json",
            "x-api-key": self.api_key
        }
        try:
            response = requests.get(url, headers=headers)
            print(f"[DEBUG] Thumbnail endpoint content-type: {response.headers.get('Content-Type')}", file=sys.stderr)
            if response.status_code != 200:
                print(f"[DEBUG] Thumbnail endpoint returned status {response.status_code}: {response.text}", file=sys.stderr)
                return None
            data = response.json()
            if not isinstance(data, dict) or 'thumbnail' not in data:
                print(f"[DEBUG] Unexpected thumbnail response: {data}", file=sys.stderr)
                return None
            thumbnail_url = data.get('thumbnail')
            print(f"[DEBUG] Extracted thumbnail URL: {thumbnail_url}", file=sys.stderr)
            if thumbnail_url:
                img_resp = requests.get(thumbnail_url)
                print(f"[DEBUG] Image fetch status: {img_resp.status_code}", file=sys.stderr)
                if img_resp.status_code == 200:
                    print(f"[DEBUG] Image fetch successful, bytes: {len(img_resp.content)}", file=sys.stderr)
                    return img_resp.content
                else:
                    print(f"[DEBUG] Failed to fetch actual thumbnail image: {img_resp.status_code}", file=sys.stderr)
                    return None
            else:
                print("[DEBUG] No thumbnail URL in JSON response", file=sys.stderr)
                return None
        except Exception as e:
            print(f"[DEBUG] Exception getting thumbnail: {str(e)}", file=sys.stderr)
            return None

    def upload_video_file(self, index_id: str, file_path: str, timeout_seconds: int = 900):

        import sys
        try:
            if not self.api_key:
                return {"error": "Missing TwelveLabs API key"}
            if not index_id:
                return {"error": "Missing index_id"}
            if not os.path.exists(file_path):
                return {"error": f"File not found: {file_path}"}
            
            print(f"[DEBUG] Starting upload for file: {file_path}", file=sys.stderr)

            tasks_url = "https://api.twelvelabs.io/v1.3/tasks"
            headers = {
                "x-api-key": self.api_key
            }

            # Create upload task
            with open(file_path, "rb") as f:
                files = {
                    "video_file": (os.path.basename(file_path), f)
                }
                data = {
                    "index_id": index_id
                }
                resp = requests.post(tasks_url, headers=headers, files=files, data=data)

            if resp.status_code not in (200, 201):
                return {"error": f"Failed to create upload task: {resp.status_code} {resp.text}"}

            resp_json = resp.json() if resp.text else {}
            task_id = resp_json.get("id") or resp_json.get("task_.id") or resp_json.get("_id")
            if not task_id:
                return {"error": f"No task id returned: {resp_json}"}

            # Poll task until ready
            import time
            start_time = time.time()
            print(f"[DEBUG] Starting to poll task {task_id} for completion...", file=sys.stderr)
            
            while time.time() - start_time < timeout_seconds:
                r = requests.get(f"{tasks_url}/{task_id}", headers=headers)
                if r.status_code != 200:
                    time.sleep(2)
                    continue
                task = r.json() if r.text else {}
                status = task.get("status")
                print(f"[DEBUG] Task {task_id} status: {status}", file=sys.stderr)
                
                if status in ("ready", "completed"):
                    video_id = task.get("video_id") or (task.get("data") or {}).get("video_id")
                    print(f"[DEBUG] Indexing completed successfully! Video ID: {video_id}", file=sys.stderr)
                    return {"status": status, "video_id": video_id, "task": task}
                if status in ("failed", "error"):
                    print(f"[DEBUG] Indexing failed with status: {status}", file=sys.stderr)
                    return {"error": f"Indexing failed with status {status}", "task": task}
                time.sleep(2)

            print(f"[DEBUG] Upload timed out after {timeout_seconds} seconds", file=sys.stderr)
            return {"error": "Upload timed out"}
        except Exception as e:
            return {"error": str(e)}