import asyncio

from viam.robot.client import RobotClient
from viam.components.board import Board

class PLCBoard():

    def __init__(self,):
        return

    @classmethod
    async def init(self, robot):
        self.board = Board.from_robot(robot, name="plc-board") 
        print("PLC Board initialized")

        return

async def connect():
    opts = RobotClient.Options.with_api_key(
      api_key='c2xoz05zsntvj5yuofuyp2uez71jlca3',
      api_key_id='b6743fec-d6c4-4b3f-a5e8-5b6046779145'
    )
    return await RobotClient.at_address('kuka-demo-main.covge5vgpo.viam.cloud', opts)

async def main():
    robot = await connect()

    plc = PLCBoard()
    await plc.init(robot)

    await robot.close()

if __name__ == '__main__':
    asyncio.run(main())