import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

class StorageManager:
    def __init__(self):
        self.supabase_url = os.environ.get("SUPABASE_URL")
        self.supabase_key = os.environ.get("SUPABASE_KEY")
        self.bucket_name = os.environ.get("SUPABASE_BUCKET", "dropshare")
        
        if self.supabase_url and self.supabase_key:
            self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
            self.is_cloud = True
        else:
            self.is_cloud = False
            self.local_upload_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads")
            if not os.path.exists(self.local_upload_dir):
                os.makedirs(self.local_upload_dir)

    def upload(self, filename, data, content_type):
        if self.is_cloud:
            try:
                # data should be bytes
                response = self.supabase.storage.from_(self.bucket_name).upload(
                    path=filename,
                    file=data,
                    file_options={"content-type": content_type}
                )
                return filename
            except Exception as e:
                print(f"Supabase Upload Error: {e}")
                raise e
        else:
            file_path = os.path.join(self.local_upload_dir, filename)
            with open(file_path, 'wb') as f:
                f.write(data)
            return filename

    def download(self, filename):
        if self.is_cloud:
            try:
                data = self.supabase.storage.from_(self.bucket_name).download(filename)
                return data
            except Exception as e:
                print(f"Supabase Download Error: {e}")
                raise e
        else:
            file_path = os.path.join(self.local_upload_dir, filename)
            if os.path.exists(file_path):
                with open(file_path, 'rb') as f:
                    return f.read()
            return None

storage_manager = StorageManager()
