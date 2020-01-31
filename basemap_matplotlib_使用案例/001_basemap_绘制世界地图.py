# -*- coding:utf-8 -*-
# project_xxx\venv\Scripts python

'''
Author: Felix
WeiXin: AXiaShuBai
Email: xiashubai@gmail.com
Blog: https://blog.csdn.net/u011318077
Date: 2020/1/31 14:17
Desc:
'''

# 首先导入绘图包和地图包
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap

# 第一步：设置图片大小及分辨率
plt.figure(figsize=(16, 8), dpi=128)

# 第二步：创建一个地图
m = Basemap()

# 第三步：绘制地图上的线条，比如海岸线，国界线
m.drawcoastlines(linewidth=1,linestyle='solid',color='black') # 绘制海岸线
m.drawcountries(linewidth=1,linestyle='solid',color='black')  # 绘制国界线

# 第四步：显示图形
plt.show()