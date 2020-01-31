# -*- coding:utf-8 -*-
# project_xxx\venv\Scripts python

'''
Author: Felix
WeiXin: AXiaShuBai
Email: xiashubai@gmail.com
Blog: https://blog.csdn.net/u011318077
Date: 2020/1/31 16:38
Desc:
'''
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from matplotlib.patches import Polygon

# 第一步：设置图片大小及分辨率
plt.figure(figsize=(16, 8), dpi=300)

# 第二步：创建一个地图，设置经度纬度范围，只显示中国区域范围，projection选择投影模式,兰勃特投影
m = Basemap(llcrnrlon=77, llcrnrlat=14, urcrnrlon=140, urcrnrlat=51, projection='lcc', lat_1=33, lat_2=45, lon_0=100)
# 读取中国行政区文件,使用GitHub上已经整理好的地图文件，drawbounds参数显示图形
# 藏南区域和岛屿都有明显的标注，可以对比002结果，信息更加丰富，藏南更准确
m.readshapefile('../china_shapfiles/china-shapefiles-simple-version/china', 'china', drawbounds=True)
# 九段线地图数据
m.readshapefile('../china_shapfiles/china-shapefiles-simple-version/china_nine_dotted_line', 'china_nine', drawbounds=True)

# 第三步：上色

ax = plt.gca()

for nshape, seg in enumerate(m.china):
    poly = Polygon(seg, facecolor='red', edgecolor='black')
    ax.add_patch(poly)




# 第四步：显示图形
plt.show()

