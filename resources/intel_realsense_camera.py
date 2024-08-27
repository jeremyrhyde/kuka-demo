import asyncio

from viam.robot.client import RobotClient
from viam.components.camera import Camera

class IntelRealsenseCamera():

    def __init__(self,):
        self.width_px = 640
        self.height_px = 480
        self.FOV = [40, 86]
        return

    @classmethod
    async def init(self, robot):
        self.camera = Camera.from_robot(robot, name="intel-realsense-cam") 
        print("Intel Realsense Camera initialized")

        return

    @classmethod
    async def get_image(self):
        image = await self.camera.get_image()

        return image

async def connect():
    opts = RobotClient.Options.with_api_key(
      api_key='c2xoz05zsntvj5yuofuyp2uez71jlca3',
      api_key_id='b6743fec-d6c4-4b3f-a5e8-5b6046779145'
    )
    return await RobotClient.at_address('kuka-demo-main.covge5vgpo.viam.cloud', opts)

async def main():
    robot = await connect()

    cam = IntelRealsenseCamera()
    await cam.init(robot)

    await robot.close()

if __name__ == '__main__':
    asyncio.run(main())