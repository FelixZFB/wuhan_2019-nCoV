# -*- coding:utf-8 -*-
# project_xxx\venv\Scripts python

'''
Author: Felix
WeiXin: AXiaShuBai
Email: xiashubai@gmail.com
Blog: https://blog.csdn.net/u011318077
Date: 2020/1/30 22:11
Desc:
'''
# 获取每个省份下各地级市详细数据，以湖北举例说明
# 其它省份获取一样，若要全部获取，可以使用使用循环取出每一个省份，然后再取出每个省份下地级市的数据

from nCov_data_analysis import a_get_html

class CityData():

    def __init__(self):
        self.ncovdata = a_get_html.nCovData()
        self.all_data = self.ncovdata.get_html_text()

    def hubei_total_data(self):
        '''获取湖北省各地级市累积数据'''
        # areaTree对应的第一个数据就是中国，下面的children对应的就是每个省份的数据，
        # 第一个省份就是湖北省，湖北省下面的children就是每个地级市的数据，也是一个列表，列表里面是字典
        areaTree = self.all_data['areaTree'][0]['children'][0]['children']
        # print(areaTree)
        city_name = list()
        city_total_confirm = list()
        city_total_suspect = list()
        city_total_dead = list()
        city_total_heal = list()
        for city in areaTree:
            city_name.append(city['name'])
            city_total_confirm.append(city['total']['confirm'])
            city_total_suspect.append(city['total']['suspect'])
            city_total_dead.append(city['total']['dead'])
            city_total_heal.append(city['total']['heal'])
        print(city_name)
        print(city_total_confirm)

    def hubei_today_data(self):
        '''获取湖北省各地级市今日数据'''
        areaTree = self.all_data['areaTree'][0]['children']
        city_name = list()
        city_today_confirm = list()
        city_today_suspect = list()
        city_today_dead = list()
        city_today_heal = list()
        for city in areaTree:
            city_name.append(city['name'])
            city_today_confirm.append(city['today']['confirm'])
            city_today_suspect.append(city['today']['suspect'])
            city_today_dead.append(city['total']['dead'])
            city_today_heal.append(city['total']['heal'])
        print(city_today_confirm)

    def main(self):
        self.hubei_total_data()
        self.hubei_today_data()

if __name__ == '__main__':
    city_data= CityData()
    city_data.main()
