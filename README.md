 # IC 仿真数据清洗与可视化工具

这个项目专门用于处理 **Cadence** 仿真导出的 **2T0C 存储阵列** PVT 仿真数据。

### 脚本说明
* **clean_data.py**: 核心数据清洗脚本，负责去除原始数据中的噪声、异常值及无效数据点。
* **data_plot.py**: 自动绘图工具，支持一键生成以下图表：
    * **Shmoo Plot**: 用于分析工艺角与电压/频率的关系。
    * **Trend Analysis**: PVT 变化趋势分析图。

### 环境要求
* Python 3.x
* Pandas, NumPy, Matplotlib
