# -*- coding:utf-8 -*-
# project_xxx\venv\Scripts python

'''
Author: Felix
Email: xiashubai@gmail.com
WeiXin: AXiaShuBai
Blog: https://blog.csdn.net/u011318077
Date: 2020/1/30 18:26
Desc:
'''

import a_get_html

class WorldData():

    def __init__(self):
        self.ncovdata = a_get_html.nCovData()
        self.all_data = self.ncovdata.get_html_text()

    def world_total_data(self):
        '''获取世界各国累积数据'''
        # areaTree键对应的值就是各个国家的数据
        areaTree = self.all_data['areaTree']
        country_name = list()
        country_total_confirm = list()
        country_total_suspect = list()
        country_total_dead = list()
        country_total_heal = list()
        for country in areaTree:
            country_name.append(country['name'])
            country_total_confirm.append(country['total']['confirm'])
            country_total_suspect.append(country['total']['suspect'])
            country_total_dead.append(country['total']['dead'])
            country_total_heal.append(country['total']['heal'])
        print(country_name)
        print(country_total_confirm)

    def world_today_data(self):
        '''获取各国今日数据'''
        areaTree = self.all_data['areaTree']
        country_name = list()
        country_today_confirm = list()
        country_today_suspect = list()
        country_today_dead = list()
        country_today_heal = list()
        for country in areaTree:
            country_name.append(country['name'])
            country_today_confirm.append(country['today']['confirm'])
            country_today_suspect.append(country['today']['suspect'])
            country_today_dead.append(country['total']['dead'])
            country_today_heal.append(country['total']['heal'])
        print(country_today_confirm)

    def main(self):
        self.world_total_data()
        self.world_today_data()

if __name__ == '__main__':
    world_data= WorldData()
    world_data.main()


