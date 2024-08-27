import asyncio

from viam.robot.client import RobotClient
from viam.services.vision import VisionClient

def calculate_bb_center(detection):
    center = ((detection.x_max + detection.x_min)/2, (detection.y_max + detection.y_min)/2)
    print("Center: " + str(center[0]) + ", " + str(center[1]))
    return center

def calculate_bb_area(detection):
    return float((detection.y_max - detection.y_min) * (detection.x_max - detection.x_min))

class VisionDetector():

    def __init__(self,):
        return

    @classmethod
    async def init(self, robot):
        self.detector = VisionClient.from_robot(robot, name="detector") 
        print("Detector initialized")
        self.confidence_threshold = 0.5

        return
    
    @classmethod
    async def get_best_detection(self, image):
        detections = await self.detector.get_detections(image)
    
        max_area_i = 0
        max_area = 0.0
        print("Detection:")
        for i in range(len(detections)):
            if detections[i].confidence < self.confidence_threshold:
                continue
            print("Valid detection: {}".format(detections[max_area_i].class_name))
            area = calculate_bb_area(detections[i])
            if area > max_area:
                max_area = area
                max_area_i = i


        if max_area == 0:
            print("No valid detections")
            return {}, False
        
        return detections[max_area_i], True
    
    @classmethod
    async def calculate_bb_offset(self, detection, width, height):
        x,y = calculate_bb_center(detection)

        return width/2 - x, height/2 - y

async def connect():
    opts = RobotClient.Options.with_api_key(
      api_key='c2xoz05zsntvj5yuofuyp2uez71jlca3',
      api_key_id='b6743fec-d6c4-4b3f-a5e8-5b6046779145'
    )
    return await RobotClient.at_address('kuka-demo-main.covge5vgpo.viam.cloud', opts)

async def main():
    robot = await connect()

    detector = VisionDetector()
    await detector.init(robot)

    await robot.close()

if __name__ == '__main__':
    asyncio.run(main())
