
import json
import math
import time

import matplotlib as mpl
import pickle

import numpy as np
from matplotlib import pyplot as plt

plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False
from sklearn.cluster import DBSCAN

from robowaiter.scene.scene import Scene


class SceneAEM(Scene):
    def __init__(self, robot):
        super().__init__(robot)

    def _reset(self):
        pass

    def _run(self):
        print(len(self.status.objects))
        objs = self.status.objects
        cur_objs = []
        cur_obstacle_world_points = []
        visited_obstacle = set()
        obj_json_data = []
        obj_count = 0
        added_info = 0

        map_ratio = self.map_ratio
        db = DBSCAN(eps=map_ratio, min_samples=int(map_ratio / 2))

        file_name = '../../robowaiter/proto/map_1.pkl'
        if os.path.exists(file_name):
            with open(file_name, 'rb') as file:
                map = pickle.load(file)


        self.add_walker(31, 30, 520, )
        self.add_walker(15, 30, 420)
        while True:
            walker_count = 0
            fig = plt.figure()
            goal = self.explore(map, 120)
            if goal is None:
                break
            cur_obstacle_world_points, cur_objs_id = self.navigation_move(plt, cur_objs, cur_obstacle_world_points,
                                                                          [[goal[0], goal[1]]], map_ratio, db, 0, 11)

            for point in cur_obstacle_world_points:
                if point[0] < -350 or point[0] > 600 or point[1] < -400 or point[1] > 1450:
                    continue
                self.map_map[math.floor((point[0] + 350) / map_ratio), math.floor((point[1] + 400) / map_ratio)] = 1
                visited_obstacle.add(
                    (math.floor((point[0] + 350) / map_ratio), math.floor((point[1] + 400) / map_ratio)))
            # plt.imshow(map_map, cmap='binary', alpha=0.5, origin='lower',
            #            extent=(-400 / map_ratio, 1450 / map_ratio,
            #                    -350 / map_ratio, 600 / map_ratio))

            for i in range(len(cur_objs_id)):
                if cur_objs_id[i] == "walker":
                    walker_count += 1
                for obj in objs:
                    if obj.name == cur_objs_id[i] and obj not in cur_objs:
                        cur_objs.append(obj)
                        break

            plt.subplot(2, 1, 2)
            plt.imshow(self.map_map, cmap='binary', alpha=0.5, origin='lower',
                       extent=(-400 / map_ratio, 1450 / map_ratio,
                               -350 / map_ratio, 600 / map_ratio))
            # plt.imshow(map_map, cmap='binary', alpha=0.5, origin='lower')
            # plt.axis('off')
            plt.title("Mapping process")

            plt.subplot(2, 7, 14)


            new_add_info = len(cur_objs) - added_info + walker_count
            plt.text(0, 0.5, f'Added semantic information：{new_add_info}', fontsize=10)
            added_info += new_add_info
            plt.text(0, 0.3, f'Stored semantic information：{added_info}', fontsize=10)
            self.infoCount = added_info
            plt.axis("off")
            plt.show()
            print(cur_objs)
            time.sleep(1)

        for i in range(len(cur_objs)):
            if cur_objs[i].name == "Desk" or cur_objs[i].name == "Chair":
                obj_json_data.append(
                    {"id": f"{i}", "name": f"{cur_objs[i].name}", "location": f"{cur_objs[i].location}",
                     "height": f"{cur_objs[i].location.Z * 2}"})

            else:
                obj_json_data.append(
                    {"id": f"{i}", "name": f"{cur_objs[i].name}", "location": f"{cur_objs[i].location}",
                     "height": f"{cur_objs[i].location.Z}"})

        with open('../../robowaiter/proto/objs.json', 'w') as file:
            json.dump(obj_json_data, file)


        print(obj_json_data)
        # self.add_walker(0, 30, 520, )
        # self.add_walker(10, 30, 420)
        # Scene.get_obstacle_point(db, Scene.status, map_ratio)


if __name__ == '__main__':
    import os
    from robowaiter.robot.robot import Robot

    robot = Robot()

    # create task
    task = SceneAEM(robot)
    task.reset()
    task.run()
