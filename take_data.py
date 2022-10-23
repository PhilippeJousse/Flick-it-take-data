from re import S
from fastapi import FastAPI, UploadFile, File
from google.cloud import storage
import os
import shutil
from pydantic import BaseModel

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "google_key.json"
app = FastAPI()
storage_client = storage.Client()
bucket_name ="storage_image_api"
bucket = storage_client.get_bucket(bucket_name)

class MetaData(BaseModel):
    userId:str
    


@app.post('/upload')
async def upload(metadata:MetaData,image: UploadFile = File(...)):
    with open(image.filename, "wb") as buffer:
        #shutil.copyfileobj(image.file, buffer)
        blob = bucket.blob('test/')
        blob.upload_from_string("car.jpg")
    #blob.upload_from_file(file)
    return {"file_name":image.filename}