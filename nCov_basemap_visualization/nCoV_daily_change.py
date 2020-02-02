# -*- coding:utf-8 -*-
# project_xxx\venv\Scripts python

'''
Author: Felix
WeiXin: AXiaShuBai
Email: xiashubai@gmail.com
Blog: https://blog.csdn.net/u011318077
Date: 2020/1/31 17:18
Desc:
'''

from china_data_analysis import ChinaData
import matplotlib.pyplot as plt

def daily_change():

    # 获取每日疫情数据，日期，确诊，疑似，死亡，治愈
    date_list, everyday_confirm, everyday_suspect, everyday_dead, everyday_heal = ChinaData().china_everyday_data()

    # 显示中文和显示负号
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False

    # 绘制画布和子图对象
    fig, ax1 = plt.subplots(figsize=(10, 6))

    # 左Y轴绘制确诊和疑似病例曲线
    ax1.plot(date_list, everyday_confirm, lw=2, ls='--', marker='o', color='red', label='确诊')
    ax1.plot(date_list, everyday_suspect, lw=2, ls='--', marker='o', color='orange', label='疑似')
    # 设置标题，XY轴标题，刻度
    ax1.set_title("2019-nCoV疫情变化时间图", fontsize=16)
    ax1.set_xlabel("2020年1-2月", fontsize=16)
    ax1.set_xticklabels(date_list, rotation=30)
    ax1.set_ylabel(r"确诊及疑似人数", fontsize=16)
    ax1.set_ylim(0, 20000)
    # 显示网格线和显示图例
    plt.grid(which='major', axis='both', color='grey', linestyle='--', alpha=0.2)
    plt.legend(loc='upper left', bbox_to_anchor=(0.3,1))

    # 右Y轴绘制死亡和治愈病例曲线,共用ax1的X轴
    ax2 = ax1.twinx()
    ax2.plot(date_list, everyday_dead, lw=1, ls='--', marker='.', color='cyan', label='死亡')
    ax2.plot(date_list, everyday_heal, lw=1, ls='--', marker='.', color='green', label='治愈')
    # 设置标题刻度
    ax2.set_ylabel(r"死亡及治愈人数", fontsize=16)
    ax2.set_ylim(0, 400)
    # 显示网格线和显示图例
    plt.grid(which='major', axis='both', color='grey', linestyle='--', alpha=0.2)
    plt.legend(loc='upper center')

    # 展示图形
    # plt.show()
    # 保存图形为图片,第一个参数保存路径，第二个参数裁掉多余的空白部分
    plt.savefig('2019-nCoV疫情变化时间图.png', bbox_inches='tight')

if __name__ == '__main__':
    daily_change()

