from fastapi import FastAPI, UploadFile, File
from google.cloud import storage,pubsub_v1
import os,datetime, shutil, uuid, pyrebase,json
from pydantic import BaseModel
from PIL import Image

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "google_key.json"

firebaseConfig = {
  "apiKey": "AIzaSyBnz6wws3EjTRnFOG7NvefKSr9CsaOlcxY",
  "authDomain": "flick-it-users-storage.firebaseapp.com",
  "databaseURL": "https://flick-it-users-storage-default-rtdb.europe-west1.firebasedatabase.app",
  "projectId": "flick-it-users-storage",
  "storageBucket": "flick-it-users-storage.appspot.com",
  "messagingSenderId": "1046722019798",
  "appId": "1:1046722019798:web:905b021820e1922f95a477",
  "measurementId": "G-J3T9K8WPV2",
  "serviceAccount": "serviceAccountCredentials.json"
}
firebase = pyrebase.initialize_app(firebaseConfig)

db = firebase.database()

app = FastAPI()

storage_client = storage.Client()
bucket_name ="storage_image_api"
bucket = storage_client.get_bucket(bucket_name)

publisher = pubsub_v1.PublisherClient()
topic_path_Vision = "projects/third-essence-365119/topics/launch-vision"
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

        blob = bucket.blob(filename)
        blob.upload_from_filename(filename)

        uri = 'gs://storage_image_api/' + filename

        timeUTC = datetime.datetime.utcnow()
        timeUTC = timeUTC.strftime("%H%M%S")

        word = db.child("word").get()
        word = json.loads(json.dumps(word.val()))
        db.child("metadata").child(id).set({"uri":uri, "timeUTC":timeUTC,"word":word["word"],"point":word["point"],"userId":userId,"status":"False"})

        id = id.encode('utf-8')
        publisher.publish(topic_path_Vision,id)
        os.remove(filename)
        return 200
    else:
        return 400