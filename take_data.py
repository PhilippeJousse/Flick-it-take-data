from fastapi import FastAPI, UploadFile, File
from google.cloud import storage,pubsub_v1
import os
import shutil
from pydantic import BaseModel
import uuid
from PIL import Image
import firebase_admin
from firebase_admin import credentials,firestore

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "google_key.json"

firebase_admin.initialize_app(credentials.Certificate('serviceAccountCredentials.json'))
db = firestore.client()

app = FastAPI()

storage_client = storage.Client()
bucket_name ="storage_image_api"
bucket = storage_client.get_bucket(bucket_name)

publisher = pubsub_v1.PublisherClient()
topic_path ="projects/third-essence-365119/topics/test-pubsub"

class MetaData(BaseModel):
    userId:str

@app.post('/v1/upload/{userId}')
async def upload(userId,image: UploadFile = File(...)):
    with open(image.filename, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)
    img = Image.open(str(buffer.name))
    if(img.format == "JPEG" or img.format == "PNG"):
        img.close()
        id = str(uuid.uuid4())
        filename = id +".jpg"
        os.rename(str(buffer.name),filename)
        word = "car"
        blob = bucket.blob(word+'/'+filename)
        blob.upload_from_filename(filename)
        uri = 'gs://storage_image_api/'+ word + '/' + filename
        dest = db.collection('metadata').document(id)
        dest.set({"uri":uri,"word":word,"userId":userId,"status":"False"})
        id = id.encode('utf-8')
        publisher.publish(topic_path,id)
        os.remove(filename)
        return 200
    else:
        return 400