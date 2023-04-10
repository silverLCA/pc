import cv2 
from PIL import Image 
from pytesseract import pytesseract 
camera=cv2.VideoCapture(0)

while True:
    _,image=camera.read()
    cv2.imshow('Text detection',image)
    if cv2.waitKey(1)& 0xFF==ord('s'):
        cv2.imwrite('test1.png',image)
        break 
       
camera.release()
cv2.destroyALLWindow()


def tesseract():
    
    Imagepath='test1.ong'
    
    

    text=pytesseract.image_to_string(Image.open(Imagepath))
    tts=gtts.gTTS(text,lang='en',slow='false')
    print(text[:-1])
tesseract()
    
       

