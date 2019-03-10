import cv2
import numpy as np

class FrameFileObject:   
    def __init__(self, data):
        self.data = cv2.imencode('.jpg', data)[1].tostring()
    
    def read(self):
        return self.data
        
    def getBuff(self):
        return np.asarray(bytearray(self.data))

    def getImage(self):
        return cv2.imdecode(self.getBuff(), -1)