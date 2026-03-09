import pandas as pd
from pyecharts import options as opts
from pyecharts.charts import Line
from pyecharts.globals import ThemeType
from datetime import datetime
import matplotlib.pyplot as plt
from pyecharts.charts import Bar
from pyecharts.charts import Pie
import numpy as np
import folium
from pyecharts.charts import BMap
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error

# 19年数据预处理
# 读取数据
df = pd.read_csv('201903-citibike-tripdata.csv')

# 删除start station id或end station id为空的行
df_cleaned = df.dropna(subset=['start station id', 'end station id'])

# 单独提取站点信息，存储为两个文件：19_start_stations.csv 和 19_end_stations.csv
start_stations = df_cleaned[['start station id']].drop_duplicates()
start_stations.to_csv('19_start_stations.csv', index=False)

end_stations = df_cleaned[['end station id']].drop_duplicates()
end_stations.to_csv('19_end_stations.csv', index=False)

# 转换'starttime'和'stoptime'列为datetime类型
df['starttime'] = pd.to_datetime(df['starttime'])
df['stoptime'] = pd.to_datetime(df['stoptime'])

# 计算借车小时数（将timedelta转换为小时，并四舍五入到最近的小时）
df['borrow_hours'] = (df['stoptime'] - df['starttime']).dt.total_seconds() / 3600
df['borrow_hours_rounded'] = df['borrow_hours'].round().astype(int)  # 四舍五入到最近整数小时

# 提取日期信息
df['date'] = df['starttime'].dt.date

# 基于借车时长（小时数，四舍五入到最近小时）进行流量汇总
# 定义小时段的边界
bins = list(range(25))  # 0到24的小时数，包括24作为上界
labels = [f'{i}-{i + 1}小时' for i in range(24)]  # 小时段标签

# 使用pd.cut()对borrow_hours_rounded进行分箱
df['borrow_hours_bin'] = pd.cut(df['borrow_hours_rounded'], bins=bins, labels=labels, right=False)

# 按日汇总流量信息（记录数）
daily_flow = df.groupby('date').size().reset_index(name='daily_flow')

# 基于借车时长（小时数）的流量汇总
hourly_duration_flow = df.groupby('borrow_hours_bin').size().reset_index(name='hourly_duration_flow')

# 将结果保存到CSV文件
daily_flow.to_csv('19_daily_flow.csv', index=False)
hourly_duration_flow.to_csv('19_hourly_duration_flow.csv', index=False)

# 20年数据预处理
# 读取数据
df = pd.read_csv('202003-citibike-tripdata.csv')

# 删除start station id或end station id为空的行
df_cleaned = df.dropna(subset=['start station id', 'end station id'])

# 转换'starttime'和'stoptime'列为datetime类型
df['starttime'] = pd.to_datetime(df['starttime'])
df['stoptime'] = pd.to_datetime(df['stoptime'])

# 计算借车小时数（将timedelta转换为小时，并四舍五入到最近的小时）
df['borrow_hours'] = (df['stoptime'] - df['starttime']).dt.total_seconds() / 3600
df['borrow_hours_rounded'] = df['borrow_hours'].round().astype(int)  # 四舍五入到最近整数小时

# 提取日期信息
df['date'] = df['starttime'].dt.date

# 基于借车时长（小时数，四舍五入到最近小时）进行流量汇总
# 定义小时段的边界
bins = list(range(25))  # 0到24的小时数，包括24作为上界
labels = [f'{i}-{i + 1}小时' for i in range(24)]  # 小时段标签

# 使用pd.cut()对borrow_hours_rounded进行分箱
df['borrow_hours_bin'] = pd.cut(df['borrow_hours_rounded'], bins=bins, labels=labels, right=False)

# 按日汇总流量信息（记录数）
daily_flow = df.groupby('date').size().reset_index(name='daily_flow')

# 基于借车时长（小时数）的流量汇总
hourly_duration_flow = df.groupby('borrow_hours_bin').size().reset_index(name='hourly_duration_flow')

# 将结果保存到CSV文件
daily_flow.to_csv('20_daily_flow.csv', index=False)
hourly_duration_flow.to_csv('20_hourly_duration_flow.csv', index=False)

print("数据预处理完成！")

# pyecharts绘制
# 读取数据
df_19 = pd.read_csv('19_daily_flow.csv', index_col='date', parse_dates=True)
df_20 = pd.read_csv('20_daily_flow.csv', index_col='date', parse_dates=True)

# 确保数据按日期排序
df_19.sort_index(inplace=True)
df_20.sort_index(inplace=True)

# 提取日期和流量数据
formatted_dates = [datetime.strftime(date, "%m-%d") for date in df_19.index]
flow_19 = df_19['daily_flow'].tolist()
flow_20 = df_20['daily_flow'].tolist()

# 创建折线图
line = (
    Line(init_opts=opts.InitOpts(theme=ThemeType.LIGHT))
    .add_xaxis(formatted_dates)  # 使用新的仅包含月和日的列表作为x轴数据
    .add_yaxis("2019年每日借车量", flow_19, label_opts=opts.LabelOpts(is_show=False), linestyle_opts=opts.LineStyleOpts(color="blue"))
    .add_yaxis("2020年每日借车量", flow_20, label_opts=opts.LabelOpts(is_show=False), linestyle_opts=opts.LineStyleOpts(color="green"))
    .set_global_opts(
        title_opts=opts.TitleOpts(title="19年与20年3月每日借车量变化对比"),
        xaxis_opts=opts.AxisOpts(
            type_="category",
            boundary_gap=False
            # 移除 formatter 设置
        ),
        yaxis_opts=opts.AxisOpts(
            type_="value",
            min_=0,
            max_=max(flow_19 + flow_20) * 1.1  # 设置一个稍微大于最大值的范围以确保所有数据都可见
        ),
        tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
        legend_opts=opts.LegendOpts(pos_left="right")  # 将图例放在左侧以避免遮挡数据
    )
)

# 渲染图表到HTML文件
line.render("daily_flow_comparison.html")
print ("绘制完成")

#绘制用户性别的借车量对比
# 读取数据
df = pd.read_csv('201903-citibike-tripdata.csv')

# 数据汇总：计算每个性别的总借车量
gender_summary = df['gender'].value_counts().reset_index()
gender_summary.columns = ['gender', 'total_trips']

gender_mapping = {1: 'Male', 2: 'Female'}  # 根据你的数据实际情况调整
gender_summary['gender'] = gender_summary['gender'].map(gender_mapping)

# 绘制柱状图
bar = (
    Bar()
    .add_xaxis(gender_summary['gender'].tolist())
    .add_yaxis("Total Trips", gender_summary['total_trips'].tolist())
    .set_global_opts(
        title_opts=opts.TitleOpts(title="19_不同用户性别的借车量统计"),
        xaxis_opts=opts.AxisOpts(name="性别"),
        yaxis_opts=opts.AxisOpts(name="总借车量"),
    )
)

# 渲染图表到本地 HTML 文件
bar.render("2019_gender_bike_trips.html")

# 读取数据
df = pd.read_csv('202003-citibike-tripdata.csv')

# 数据汇总：计算每个性别的总借车量
gender_summary = df['gender'].value_counts().reset_index()
gender_summary.columns = ['gender', 'total_trips']

gender_mapping = {1: 'Male', 2: 'Female'}  # 根据你的数据实际情况调整
gender_summary['gender'] = gender_summary['gender'].map(gender_mapping)

# 绘制柱状图
bar = (
    Bar()
    .add_xaxis(gender_summary['gender'].tolist())
    .add_yaxis("Total Trips", gender_summary['total_trips'].tolist())
    .set_global_opts(
        title_opts=opts.TitleOpts(title="20_不同用户性别的借车量统计"),
        xaxis_opts=opts.AxisOpts(name="性别"),
        yaxis_opts=opts.AxisOpts(name="总借车量"),
    )
)

# 渲染图表到本地 HTML 文件
bar.render("2020_gender_bike_trips.html")
print("绘制完成")

#绘制用户年龄饼状图
# 读取数据
df = pd.read_csv('201903-citibike-tripdata.csv')

# 计算年龄，并添加到新列
current_year = datetime.now().year  # 获取当前年份
df['age'] = current_year - df['birth year']

# 划分年龄段，并添加到新列
def age_group(age):
    if age >= 100:
        return "100+"
    else:
        return f"{(age // 10) * 10}-{((age // 10) + 1) * 10 - 1}"

df['age_group'] = df['age'].apply(age_group)

# 数据汇总：计算每个年龄段的总借车量
age_summary = df.groupby('age_group')['tripduration'].sum().reset_index()
age_summary.columns = ['age_group', 'total_trips']

# 计算所有用户的总借车量
total_trips = age_summary['total_trips'].sum()

# 计算每个年龄段占总借车量的比例
age_summary['percentage'] = age_summary['total_trips'] / total_trips

# 准备数据给饼图
data_for_pie = [
    list(z) for z in zip(age_summary['age_group'], age_summary['total_trips'])
]

# 绘制饼状图
pie = (
    Pie()
    .add("", data_for_pie, radius=["30%", "75%"], center=["50%", "50%"], rosetype="radius")
    .set_global_opts(
        title_opts=opts.TitleOpts(title="2019_不同用户年龄的借车量统计"),
        legend_opts=opts.LegendOpts(is_show=True, pos_left='center', pos_top='bottom', orient='horizontal')
    )
    .set_series_opts(
        label_opts=opts.LabelOpts(formatter="{b}: {c} trips ({d}%)")
    )
)

# 渲染图表到本地 HTML 文件
pie.render("2019_age_group_bike_trips.html")

# 读取数据
df = pd.read_csv('202003-citibike-tripdata.csv')

# 计算年龄，并添加到新列
current_year = datetime.now().year
df['age'] = current_year - df['birth year']

# 划分年龄段，并添加到新列
def age_group(age):
    if age >= 100:
        return "100+"
    else:
        return f"{(age // 10) * 10}-{((age // 10) + 1) * 10 - 1}"

df['age_group'] = df['age'].apply(age_group)

# 数据汇总
age_summary = df.groupby('age_group')['tripduration'].sum().reset_index()
age_summary.columns = ['age_group', 'total_trips']
age_summary['percentage'] = age_summary['total_trips'] / age_summary['total_trips'].sum()

# 绘制饼状图
pie = (
    Pie()
    .add(
        "",
        [(age_group, total_trips) for age_group, total_trips in zip(age_summary['age_group'], age_summary['total_trips'])],
        radius=["30%", "75%"],
        center=["50%", "50%"],
        rosetype="radius",
        label_opts=opts.LabelOpts(formatter="{b}: {c} trips ({d}%)")
    )
    .set_global_opts(
        title_opts=opts.TitleOpts(title="2020_不同用户年龄的借车量统计"),
        legend_opts=opts.LegendOpts(is_show=True, pos_left='center', pos_top='bottom', orient='horizontal')
    )
)

# 渲染图表到本地 HTML 文件
pie.render("2020_age_group_bike_trips.html")
print("绘制完成")

#绘制用户类型柱状图
# 读取数据
df = pd.read_csv('201903-citibike-tripdata.csv')

# 确保usertype和tripduration列没有缺失值
df.dropna(subset=['usertype', 'tripduration'], inplace=True)

# 数据汇总：计算每种用户类型的总借车量
user_type_summary = df.groupby('usertype')['tripduration'].sum().reset_index()
user_type_summary.columns = ['usertype', 'total_trips']

# 绘制柱状图
bar = (
    Bar()
    .add_xaxis(user_type_summary['usertype'].tolist())
    .add_yaxis("Total Trips", user_type_summary['total_trips'].tolist())
    .set_global_opts(
        title_opts=opts.TitleOpts(title="2019_不同用户类型的借车量统计"),
        xaxis_opts=opts.AxisOpts(name="User Type"),
        yaxis_opts=opts.AxisOpts(name="Total Trips"),
    )
)

# 渲染图表到本地HTML文件
bar.render("2019_user_type_bike_trips.html")

# 读取数据
df = pd.read_csv('202003-citibike-tripdata.csv')

# 确保usertype和tripduration列没有缺失值
df.dropna(subset=['usertype', 'tripduration'], inplace=True)

# 数据汇总：计算每种用户类型的总借车量
user_type_summary = df.groupby('usertype')['tripduration'].sum().reset_index()
user_type_summary.columns = ['usertype', 'total_trips']

# 绘制柱状图
bar = (
    Bar()
    .add_xaxis(user_type_summary['usertype'].tolist())
    .add_yaxis("Total Trips", user_type_summary['total_trips'].tolist())
    .set_global_opts(
        title_opts=opts.TitleOpts(title="2020_不同用户类型的借车量统计"),
        xaxis_opts=opts.AxisOpts(name="User Type"),
        yaxis_opts=opts.AxisOpts(name="Total Trips"),
    )
)

# 渲染图表到本地HTML文件
bar.render("2020_user_type_bike_trips.html")
print("绘制完成")

#空间可视化
data = pd.read_csv('stations.csv')

longitudes = data['station longitude'].tolist()
latitudes = data['station latitude'].tolist()

m = folium.Map(location=[latitudes[0], longitudes[0]], zoom_start=10)

for lon, lat in zip(longitudes, latitudes):
    folium.CircleMarker(
        location=[lat, lon],
        radius=3,
        color='blue',
        fill=True,
        fill_color='blue',
        fill_opacity=0.6
    ).add_to(m)

m.save('map_from_csv.html')
# 读取 CSV 文件
df = pd.read_csv(r'stations.csv')

# 提取站点信息
stations = list(zip(df['station name'], df['station longitude'], df['station latitude']))

# 百度地图API密钥
BMAP_AK = 'aflG76UebFtMaI2v53li6DUd3SdLaEkd'

# 创建BMap实例并设置地图大小
bmap = BMap(init_opts=opts.InitOpts(width="1200px", height="700px"))

# 设置百度地图的中心点和缩放等级
bmap.add_schema(
    baidu_ak=BMAP_AK,
    center=[-74.0060, 40.7128],  # 设置纽约的经纬度为中心
    zoom=12,  # 设置缩放比例，适合显示纽约地区
)


# 添加站点到地图上
for station in stations:
    bmap.add_coordinate(station[0], station[1], station[2])
    bmap.add(
        "",
        [(station[0], 1)],
        type_="scatter",
        symbol_size=6,
        itemstyle_opts=opts.ItemStyleOpts(color="blue"),  # 设置散点的颜色为蓝色
        label_opts = opts.LabelOpts(is_show=False),  # 隐藏散点标签
        tooltip_opts = opts.TooltipOpts(formatter=f"{station[0]}<br>经度：{station[1]}<br> 纬度：{station[2]}")  # 设置提示信息
    )

# 设置地图全局配置
bmap.set_global_opts(
    title_opts=opts.TitleOpts(title="纽约站点分布图"),
)

# 渲染到HTML文件
bmap.render("stations_map.html")
print("绘制完成")

#k-means聚类
# 读取CSV文件
csv_file_path = 'stations.csv'  # 请确保CSV文件的路径正确
df = pd.read_csv(csv_file_path)

df.columns = ['station_id', 'station_name', 'latitude', 'longitude']

# 用户输入K值
k = int(input("请输入聚类个数K: "))

# 从DataFrame中提取经纬度坐标
coords = df[['latitude', 'longitude']].values

# 标准化经纬度数据
scaler = StandardScaler()
coords_scaled = scaler.fit_transform(coords)

# 使用KMeans进行聚类
kmeans = KMeans(n_clusters=k, random_state=0).fit(coords_scaled)
labels = kmeans.labels_

# 将聚类标签添加回DataFrame中
df['cluster'] = labels

# 绘制聚类结果
plt.figure(figsize=(10, 8))
colors = plt.cm.Spectral(np.linspace(0, 1, k))
for i in range(k):
    class_member_mask = (df['cluster'] == i)
    plt.scatter(df.loc[class_member_mask, 'longitude'], df.loc[class_member_mask, 'latitude'],
                c=colors[i], label=f'Cluster {i+1}', s=100, alpha=0.6, edgecolor='k')

plt.title(f'K-means Clustering of Stations (K={k})')
plt.xlabel('Longitude')
plt.ylabel('Latitude')
plt.legend()
plt.grid(True)
plt.show()
print("绘制完成")

#聚类空间可视化
# 读取CSV文件
csv_file_path = 'stations.csv'
df = pd.read_csv(csv_file_path)


df.columns = ['station_id', 'station_name', 'latitude', 'longitude']

# 用户输入K值
k = int(input("请输入聚类个数K: "))

# 从DataFrame中提取经纬度坐标
coords = df[['latitude', 'longitude']].values

# 标准化经纬度数据
scaler = StandardScaler()
coords_scaled = scaler.fit_transform(coords)

# 使用KMeans进行聚类
kmeans = KMeans(n_clusters=k, random_state=0).fit(coords_scaled)
labels = kmeans.labels_

# 将聚类标签添加回DataFrame中
df['cluster'] = labels

# 百度地图API密钥
BMAP_AK = 'aflG76UebFtMaI2v53li6DUd3SdLaEkd'

# 创建BMap实例并设置地图大小
bmap = BMap(init_opts=opts.InitOpts(width="1200px", height="700px"))

# 设置百度地图的中心点和缩放等级
bmap.add_schema(
    baidu_ak=BMAP_AK,
    center=[-74.0060, 40.7128],  # 设置纽约的经纬度为中心
    zoom=12,  # 设置缩放比例，适合显示纽约地区
)

# 提取站点信息
stations = list(zip(df['station_name'], df['longitude'], df['latitude'], df['cluster']))

# 添加站点到地图上，同时体现聚类结果
for station in stations:
    bmap.add_coordinate(station[0], station[1], station[2])
    # 根据聚类标签选择不同颜色，这里简单示例用固定几种颜色区分不同聚类类别，可根据喜好调整配色方案
    color_mapping = ['red', 'green', 'blue', 'yellow', 'purple', 'orange', 'black', 'gray']  # 示例颜色列表，根据k值合理设置长度
    color_index = station[3] % len(color_mapping)  # 获取对应颜色索引
    bmap.add(
        "",
        [(station[0], 1)],
        type_="scatter",
        symbol_size=6,
        itemstyle_opts=opts.ItemStyleOpts(color=color_mapping[color_index]),  # 根据聚类设置散点的颜色
        label_opts=opts.LabelOpts(is_show=False),  # 隐藏散点标签
        tooltip_opts=opts.TooltipOpts(formatter=f"{station[0]}<br>经度：{station[1]}<br> 纬度：{station[2]}<br>聚类类别: {station[3]}")  # 设置提示信息包含聚类类别
    )

# 设置地图全局配置
bmap.set_global_opts(
    title_opts=opts.TitleOpts(title="纽约站点聚类分布图"),
)

# 渲染到HTML文件
bmap.render("stations_cluster_map.html")
print("绘制完成")

#流量预测
# 读取流量数据文件
file_path = '19_daily_flow.csv'
df = pd.read_csv(file_path, parse_dates=['date'], index_col='date')
df.columns = ['daily_flow']  # 确保列名正确

#线性回归
# 使用滞后1天的流量作为特征
df['lag_1'] = df['daily_flow'].shift(1)
df.dropna(inplace=True)  # 删除缺失值

X = df[['lag_1']]
y = df['daily_flow']

# 拆分数据为训练集和测试集
from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)

# 拟合线性回归模型
from sklearn.linear_model import LinearRegression
model = LinearRegression()
model.fit(X_train, y_train)

# 进行预测
y_pred = model.predict(X_test)

# 计算误差
mse = mean_squared_error(y_test, y_pred)
print(f'Linear Regression MSE: {mse}')

# 创建与y_test索引对齐的预测值Series
y_pred_series = pd.Series(y_pred, index=df.iloc[len(X_train):].index)

# 可视化结果
plt.figure(figsize=(10, 6))
plt.plot(y_test.index, y_test, label='Actual Daily Flow', color='blue')
plt.plot(y_pred_series.index, y_pred_series, label='Predicted Daily Flow', color='red', linestyle='--')
plt.xlabel('Date')
plt.ylabel('Daily Flow')
plt.title('Actual vs Predicted Daily Flow')
plt.legend()
plt.grid(True)
plt.show()

#XGBoost
# 使用滞后项作为特征
for i in range(1, 7):  # 创建6个滞后项特征
    df[f'lag_{i}'] = df['daily_flow'].shift(i)
df.dropna(inplace=True)  # 删除缺失值

X = df.drop('daily_flow', axis=1)
y = df['daily_flow']

# 拆分数据为训练集和测试集
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)

# 使用XGBoost进行训练
import xgboost as xgb
dtrain = xgb.DMatrix(X_train, label=y_train)
dtest = xgb.DMatrix(X_test, label=y_test)

params = {
    'objective': 'reg:squarederror',
    'max_depth': 3,
    'eta': 0.1,
    'subsample': 0.8,
    'colsample_bytree': 0.8,
    'seed': 42
}

num_rounds = 100
model = xgb.train(params, dtrain, num_rounds)

# 进行预测
y_pred = model.predict(dtest)

# 计算误差
mse = mean_squared_error(y_test, y_pred)
print(f'XGBoost MSE: {mse}')

# 可视化结果
plt.figure(figsize=(10, 6))
plt.plot(y_test.index, y_test, label='Actual Daily Flow', color='blue')
plt.plot(y_test.index, y_pred, label='Predicted Daily Flow', color='red', linestyle='--')
plt.xlabel('Date')
plt.ylabel('Daily Flow')
plt.title('Actual vs Predicted Daily Flow using XGBoost')
plt.legend()
plt.grid(True)
plt.show()