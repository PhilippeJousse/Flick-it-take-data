from fastapi import FastAPI, UploadFile, File
from google.cloud import storage,pubsub_v1
import os
import shutil
from pydantic import BaseModel
import uuid
from PIL import Image

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "google_key.json"
app = FastAPI()
storage_client = storage.Client()
bucket_name ="storage_image_api"
bucket = storage_client.get_bucket(bucket_name)

publisher = pubsub_v1.PublisherClient()
topic_path ="projects/third-essence-365119/topics/test-pubsub"

class MetaData(BaseModel):
    userId:str

@app.post('/upload/{userId}')
async def upload(userId,image: UploadFile = File(...)):
    with open(image.filename, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)
    img = Image.open(str(buffer.name))
    if(img.format == "JPEG" or img.format == "PNG"):
        img.close()
        id = uuid.uuid4()
        filename = str(id)+".jpg"
        os.rename(str(buffer.name),filename)
        word = "car/"
        blob = bucket.blob(word+filename)
        blob.upload_from_filename(filename)
        uri = 'gs://storage_image_api'+ word + filename
        message = {'uri':uri,'word':word,'userId':userId}
        message = str(message)
        message = message.encode('utf-8')
        publisher.publish(topic_path,message)
        os.remove(filename)
        return 200
    else:
        return 400