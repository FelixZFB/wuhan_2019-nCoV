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

from nCov_data_analysis import a_get_html

class ChinaData():

    def __init__(self):
        self.ncovdata = a_get_html.nCovData()
        self.all_data = self.ncovdata.get_html_text()

    def china_total_data(self):
        # 累积数据汇总(实际该累积数据包含其它国家的数据),chinaTotal键对应的值就是累积数据
        chinaTotal = self.all_data['chinaTotal']
        # print(chinaTotal)
        return chinaTotal

    def china_everyday_data(self):
        '''获取中国每日累积数据'''
        chinaDayList = self.all_data['chinaDayList']
        date_list = list()
        everyday_confirm = list()
        everyday_suspect = list()
        everyday_dead = list()
        everyday_heal = list()
        for everyday in chinaDayList:
            date_list.append(everyday['date'])
            everyday_confirm.append(int(everyday['confirm']))
            everyday_suspect.append(int(everyday['suspect']))
            everyday_dead.append(int(everyday['dead']))
            everyday_heal.append(int(everyday['heal']))
        # print(date_list)
        # print(everyday_confirm) # 中国累积确诊数据少于上面chinaTotal累积数据
        return date_list, everyday_confirm, everyday_suspect, everyday_dead, everyday_heal

    def main(self):
        self.china_total_data()
        self.china_everyday_data()

if __name__ == '__main__':
    world_data= ChinaData()
    world_data.main()


