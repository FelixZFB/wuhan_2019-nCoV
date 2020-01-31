# -*- coding:utf-8 -*-
# project_xxx\venv\Scripts python

'''
Author: Felix
WeiXin: AXiaShuBai
Email: xiashubai@gmail.com
Blog: https://blog.csdn.net/u011318077
Date: 2020/1/31 15:31
Desc:
'''
# 首先导入绘图包和地图包
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap

# 第一步：设置图片大小及分辨率
plt.figure(figsize=(16, 8), dpi=300)

# 第二步：创建一个地图，设置经度纬度范围，只显示中国区域范围，projection选择投影模式,兰勃特投影
m = Basemap(llcrnrlon=77, llcrnrlat=14, urcrnrlon=140, urcrnrlat=51, projection='lcc', lat_1=33, lat_2=45, lon_0=100)
# 读取中国行政区文件,使用GitHub上已经整理好的地图文件，drawbounds参数显示图形
# 藏南区域和岛屿都有明显的标注，可以对比002结果，信息更加丰富，藏南更准确
m.readshapefile('../china_shapfiles/china-shapefiles-simple-version/china', 'china', drawbounds=True)
# 九段线地图数据
m.readshapefile('../china_shapfiles/china-shapefiles-simple-version/china_nine_dotted_line', 'china', drawbounds=True)


# 上面使用读取了本地地图文件，就不需要使用basemap绘制海岸线和国界线了，避免混乱
# 第三步：绘制地图上的线条，比如海岸线，国界线
# m.drawcoastlines(linewidth=1,linestyle='solid',color='black') # 绘制海岸线
# m.drawcountries(linewidth=1,linestyle='solid',color='black')  # 绘制国界线

# 第四步：显示图形
plt.show()