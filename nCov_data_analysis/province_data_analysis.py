# -*- coding:utf-8 -*-
# project_xxx\venv\Scripts python

'''
Author: Felix
WeiXin: AXiaShuBai
Email: xiashubai@gmail.com
Blog: https://blog.csdn.net/u011318077
Date: 2020/1/30 21:15
Desc:
'''

from nCov_data_analysis import a_get_html
import json

class ProvinceData():

    def __init__(self):
        # 获取所有的疫情数据，字典格式
        self.ncovdata = a_get_html.nCovData()
        self.all_data = self.ncovdata.get_html_text()

    def province_total_data(self):
        '''获取各省的累积数据'''
        # areaTree对应的第一个数据就是中国，下面的children对应的就是每个省份的数据，是一个列表
        areaTree = self.all_data['areaTree'][0]['children']
        province_name = list()
        province_total_confirm = list()
        province_total_suspect = list()
        province_total_dead = list()
        province_total_heal = list()
        for province in areaTree:
            province_name.append(province['name'])
            province_total_confirm.append(province['total']['confirm'])
            province_total_suspect.append(province['total']['suspect'])
            province_total_dead.append(province['total']['dead'])
            province_total_heal.append(province['total']['heal'])
        # 将省份名称和确诊人数对应打包为字典，用于ECharts地图可视化
        province_total_confirm_dict = {'name': province_name, 'value': province_total_confirm}
        print(province_total_confirm_dict)
        with open('province_total.json', 'w', encoding='utf-8') as f:
            json.dump(province_total_confirm_dict, f, ensure_ascii=False)
        return province_name, province_total_confirm

    def province_today_data(self):
        '''获取各省今日数据'''
        areaTree = self.all_data['areaTree'][0]['children']
        province_name = list()
        province_today_confirm = list()
        province_today_suspect = list()
        province_today_dead = list()
        province_today_heal = list()
        for province in areaTree:
            province_name.append(province['name'])
            province_today_confirm.append(province['today']['confirm'])
            province_today_suspect.append(province['today']['suspect'])
            province_today_dead.append(province['total']['dead'])
            province_today_heal.append(province['total']['heal'])
        # print(province_today_confirm)

    def main(self):
        self.province_total_data()
        self.province_today_data()

if __name__ == '__main__':
    province_data= ProvinceData()
    province_data.main()


