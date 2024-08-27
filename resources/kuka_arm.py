import asyncio
import time 

from viam.robot.client import RobotClient
from viam.components.arm import Arm

class KukaArm():

    def __init__(self,):
        return

    @classmethod
    async def init(self, robot):
        self.arm = Arm.from_robot(robot, name="kuka-arm") 
        print("Kuka Arm initialized")


        self.joint_lengths = [9.,24.,10.,10.,5.,0.]
        self.joint_start_angles = [0.,-60.,112.5,0.,-50.,0.]
        #self.joint_start_angles = [45.,-60.,112.5,0.,-50.,0.]

        self.joint_neg_limits = [-60.0, -90.0, 90.0, -30.0, -100.0, -30.0]
        self.joint_pos_limits = [60.0, -45.0, 130.0, 30.0, 0.0, 30.0]

        await self.move_to_home()
        self.at_home = True

        return

    @classmethod
    async def move_to_home(self):
        print("Re-homing...")
        await self.move_to(self.joint_start_angles)
        print("Re-homing complete!")
        self.at_home = True
        return
    
    @classmethod
    async def move_curious(self):
        current_joints = await self.arm.get_joint_positions()
        new_joints = current_joints

        new_joints.values[5] = -20.
        await self.arm.move_to_joint_positions(new_joints)
        new_joints.values[5] = 20.
        await self.arm.move_to_joint_positions(new_joints)
        new_joints.values[5] = 0.
        await self.arm.move_to_joint_positions(new_joints)

        return
    
    @classmethod
    async def move_to(self, joint_angles):

        current_joints = await self.arm.get_joint_positions()
        new_joints = current_joints

        for i in range(len(joint_angles)):

            if joint_angles[i] < self.joint_neg_limits[i] or joint_angles[i] > self.joint_pos_limits[i]:
                print("Move is outside of limits for joint {} (Value: {} [{} < {}]".format(i, 
                                                                                           str(joint_angles[i]), 
                                                                                           str(self.joint_neg_limits[i]), 
                                                                                           str(self.joint_pos_limits[i])))
                return
            new_joints.values[i] = joint_angles[i]
            #print("Joint {} set to {}".format(i, joint_angles[i]))
            
        await self.arm.stop()
    
        await self.arm.move_to_joint_positions(new_joints)
        self.at_home = False

        return
    
    @classmethod
    async def move_to_delta(self, angle_offset):
        current_joints = await self.arm.get_joint_positions()

        new_joints = current_joints

        # X axis
        dtheta0 = angle_offset[0]

        # Y axis
        L1 = self.joint_lengths[1]
        L2 = self.joint_lengths[2] + self.joint_lengths[3]
        L3 = self.joint_lengths[4]
        LT = 10*(L1 + L2 + L3)

        dtheta1 = angle_offset[1]*(LT/(2*L1*L2-L3*L2-L1*L3))
        dtheta2 = angle_offset[1]*(LT/(2*L1*L2-L3*L2-L1*L3))*L2/L1
        dtheta3 = -(dtheta1 + dtheta2)

        print("Delta - [0]: " + str(dtheta1
                                    ) + " [1]: " + str(dtheta2) + " [2]: " + str(dtheta3))
        
        new_joints.values[0] -= dtheta0
        new_joints.values[1] -= dtheta1
        new_joints.values[2] -= dtheta2
        new_joints.values[4] -= dtheta3

        for i in range(len(new_joints.values)):
            # if new_joints.values[i] < self.joint_neg_limits[i] or new_joints.values[i] > self.joint_pos_limits[i]:
            #     print("Move is outside of limits for joint {} (Value: {} [{} < {}]".format(i, 
            #                                                                                str(new_joints.values[i]), 
            #                                                                                str(self.joint_neg_limits[i]), 
            #                                                                                str(self.joint_pos_limits[i])))
            #     return
            if new_joints.values[i] < self.joint_neg_limits[i]:
                new_joints.values[i] = self.joint_neg_limits[i]
            if new_joints.values[i] > self.joint_pos_limits[i]:
                new_joints.values[i] = self.joint_pos_limits[i]

        await self.arm.stop()

        await self.arm.move_to_joint_positions(new_joints)
        self.at_home = False

        return

async def connect():
    opts = RobotClient.Options.with_api_key(
      api_key='c2xoz05zsntvj5yuofuyp2uez71jlca3',
      api_key_id='b6743fec-d6c4-4b3f-a5e8-5b6046779145'
    )
    return await RobotClient.at_address('kuka-demo-main.covge5vgpo.viam.cloud', opts)

async def main():
    robot = await connect()

    arm = KukaArm()
    await arm.init(robot)

    await robot.close()

if __name__ == '__main__':
    asyncio.run(main())