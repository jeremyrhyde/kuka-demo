import asyncio
import time, threading
from datetime import datetime, timedelta

from resources.kuka_arm import KukaArm
from resources.intel_realsense_camera import IntelRealsenseCamera
from resources.plc_board import PLCBoard 
from resources.detector import VisionDetector
from viam.robot.client import RobotClient
from viam.components.board import Board

def check_no_move_region(angle_offset):
    check_no_move_region = (2,2)

    if abs(angle_offset[0]) <= check_no_move_region[0] and abs(angle_offset[1]) <= check_no_move_region[1]:
        return True

    return False

async def connect():
    opts = RobotClient.Options.with_api_key(
      api_key='c2xoz05zsntvj5yuofuyp2uez71jlca3',
      api_key_id='b6743fec-d6c4-4b3f-a5e8-5b6046779145'
    )
    return await RobotClient.at_address('kuka-demo-main.covge5vgpo.viam.cloud', opts)

async def connect_pi():
    opts = RobotClient.Options.with_api_key(
      api_key='9zqecgtkt0sogdhl4li45sc8j82lx24o',
      api_key_id='47395597-7759-4521-b33b-ecdab7b97ddd'
    )
    return await RobotClient.at_address('kuk-demo-2-main.covge5vgpo.viam.cloud', opts)

async def connect_plc():
    opts = RobotClient.Options.with_api_key(
      api_key='2n0whcheas7v57iy7f2oxoif2qahet1k',
      api_key_id='9bc9b494-b12a-4fae-9fd2-c9d5ad4f0735'
    )
    return await RobotClient.at_address('revpi104519-main.nen8isx27t.viam.cloud', opts)

class KukaDemo():

    def __init__(self,):
        return

    @classmethod
    async def init(self, robot, plc_robot):
        self.arm = KukaArm()        
        self.camera = IntelRealsenseCamera()
        self.detector = VisionDetector()

        await self.arm.init(robot)
        await self.camera.init(robot)
        await self.detector.init(robot)   
        
        self.board = Board.from_robot(plc_robot, name="PLCBoard") 
        print("PLC Board initialized")

        self.gpiopin0 = await self.board.gpio_pin_by_name("DO_01")
        self.gpiopin1 = await self.board.gpio_pin_by_name("DO_02")
        self.gpiopin2 = await self.board.gpio_pin_by_name("DO_03")
        self.gpiopin3 = await self.board.gpio_pin_by_name("DO_04")

    @classmethod
    def pixel_to_angle_offset(self, pixel_offset):
        angle_offset = (pixel_offset[0]/self.camera.width_px*self.camera.FOV[0], pixel_offset[1]/self.camera.height_px*self.camera.FOV[1])
        return angle_offset


    @classmethod
    async def start_loop(self):
        # Start loop
        i = 0
        reset_time = datetime.now()
        curious_timer = 0
        while True:
            if i > 10000:
                break

            #input("Press Enter")

            try:
                image = await self.camera.get_image()
                detection, ok = await self.detector.get_best_detection(image)
                if not ok:
                    if datetime.now() > reset_time + timedelta(seconds=10) and not self.arm.at_home:
                        await self.arm.move_to_home()
                    continue

                reset_time = datetime.now()

                print(detection)
                pixel_offset = await self.detector.calculate_bb_offset(detection, self.camera.width_px, self.camera.height_px)

                print("Pixel Offset:" + str(pixel_offset[0]) + ", " + str(pixel_offset[1]))

                angle_offset = self.pixel_to_angle_offset(pixel_offset)

                print("Angle Offset:" + str(angle_offset[0]) + ", " + str(angle_offset[1]))

                if check_no_move_region(angle_offset):
                    print("No move needed")
                    curious_timer += 1
                    if curious_timer > 10:
                        await self.arm.move_curious()
                        curious_timer = 0
                else:
                    curious_timer = 0

                    print("Moving arm")
                    await self.arm.move_to_delta(angle_offset)

                print("Setting PLC Pin to ", detection.class_name == "Hardhat")
                await self.gpiopin0.set(detection.class_name == "Hardhat")
                await self.gpiopin1.set(detection.class_name == "Hardhat")
                await self.gpiopin2.set(detection.class_name == "Hardhat")
                await self.gpiopin3.set(detection.class_name == "Hardhat")

                i = i + 1
            except Exception as e:
                print("Exception ", e)
        return

async def main():
    robot = await connect()
    print("Connected to main robot")
    plc_robot = await connect_plc()
    print("Connected to plc robot")

    demo = KukaDemo()
    await demo.init(robot, plc_robot)
    await demo.start_loop()

    await robot.close()

if __name__ == '__main__':
    asyncio.run(main())