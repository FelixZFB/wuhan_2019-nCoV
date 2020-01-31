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
from province_data_analysis import ProvinceData
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap

def distribution_map():

    # 显示中文和显示负号
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False

    # 获取省份名称列表及确认病例列表原始数据，按照人数多到少排列
    province_name, province_total_confirm = ProvinceData().province_total_data()
    province_confirm_dict = dict(zip(province_name, province_total_confirm))

    # 设置图形大小
    plt.figure(figsize=(10, 8), dpi=300)

    # 设置中国的经纬度范围
    lon_min, lon_max = 77, 142
    lat_min, lat_max = 14, 51

    # 绘制中国地图，设置经度纬度范围，使用兰伯特投影
    map = Basemap(llcrnrlon=lon_min, llcrnrlat=lat_min, urcrnrlon=lon_max, urcrnrlat=lat_max, projection='lcc',
                  lat_1=33, lat_2=45, lon_0=100)
    map.readshapefile('../china_shapfiles/china-shapefiles-simple-version/china', 'china', drawbounds=True)
    map.readshapefile('../china_shapfiles/china-shapefiles-simple-version/china_nine_dotted_line', 'china_nine',
                    drawbounds=True)

    # 读取各省份省委城市的经纬度数据
    posi = pd.read_excel('中国省会城市经度纬度表.xlsx')
    province_list = list(posi['province'])
    lat_list = np.array(posi["lat"][0:34])
    lon_list = np.array(posi["lon"][0:34])
    confirm_origin = list(posi["confirm"][0:34])
    province_dict = dict(zip(province_list,confirm_origin))

    # 进行重新排序后的省份疫情表，省份排序与本地的经纬度表一致
    new_province_confirm= data_merge(province_dict, province_confirm_dict)
    confirm_list = np.array(list(new_province_confirm.values()))
    size = (confirm_list/np.max(confirm_list))*3000
    print(confirm_list)

    parallels = np.arange(0., 90, 10.)
    map.drawparallels(parallels, labels=[1, 0, 0, 0], fontsize=10)  # 绘制纬线
    meridians = np.arange(80., 140., 10.)
    map.drawmeridians(meridians, labels=[0, 0, 0, 1], fontsize=10)  # 绘制经线

    x, y = map(lon_list, lat_list)
    map.scatter(x, y, s=size, c='red')
    # 设置数字标记
    for i in range(0, 34):
        plt.text(x[i] + 5000, y[i] + 5000, str(confirm_list[i]))

    plt.title('2019-nCoV疫情分布地图', fontsize=16)
    plt.savefig('2019-nCoV疫情分布地图.png')
    plt.show()

# 由于原始疫情数据是按确诊人数排列的，与本地经纬度表排序不一致
# 我们将省份相同的名称对应的confirm(初始confirm都是0)值相加，得到重新排序后的确诊人数列表
def data_merge(A, B):
    C = dict()
    for key in A:
        if B.get(key):
            C[key] = A[key] + B[key]
        else:
            C[key] = A[key]
    for key in B:
        if not A.get(key):
            C[key] = B[key]
    return C

if __name__ == '__main__':
    distribution_map()
