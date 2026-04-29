import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import sys
import os

def plot_reliability_trends(df, base_name):
    """绘制全 PVT 矩阵的半对数趋势图"""
    print("⏳ 正在生成全温区趋势分析图 (Semi-log)...")
    
    plt.figure(figsize=(10, 6))
    sns.set_style("whitegrid")
    plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial']
    
    sns.lineplot(data=df, x='Temp', y='RetentionTime', 
                 hue='Corner', style='Voltage', 
                 markers=True, markersize=8, linewidth=2)

    plt.yscale('log')
    plt.axvline(x=125, color='red', linestyle='--', alpha=0.7, label='Spec Limit (125°C)')

    plt.title('2T0C e-DRAM Retention Time vs. Temperature', fontsize=14, fontweight='bold')
    plt.xlabel('Ambient Temperature (°C)', fontsize=12)
    plt.ylabel('Retention Time ($\mu$s) - Log Scale', fontsize=12)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', title="PVT Conditions")
    plt.grid(True, which="both", ls="-", alpha=0.3)
    plt.tight_layout()

    output_img = f'{base_name}_Trend_Analysis.png'
    plt.savefig(output_img, dpi=300)
    plt.close() # 释放内存，防止两张图重叠
    print(f"✅ 趋势图已保存: {output_img}")

    # 打印 Worst-Case
    worst_case = df.loc[df['RetentionTime'].idxmin()]
    print("\n🚨 [系统预警] 最差边界 (Worst-Case):")
    print(f"   -> {worst_case['Corner']} Corner | {worst_case['Voltage']}V | {worst_case['Temp']}°C | {worst_case['RetentionTime']} μs\n")

def plot_shmoo_matrix(df, base_name, target_corner='FF', pass_threshold=1.0):
    """绘制指定 Corner 的 Shmoo Pass/Fail 边界图"""
    print(f"⏳ 正在生成 {target_corner} 角的 Shmoo Plot (阈值: {pass_threshold}μs)...")
    
    df_corner = df[df['Corner'] == target_corner.upper()]
    if df_corner.empty:
        print(f"❌ 警告：未找到 {target_corner} 的数据，跳过 Shmoo 绘制。")
        return

    # 数据透视与排序
    shmoo_data = df_corner.pivot(index="Voltage", columns="Temp", values="RetentionTime")
    shmoo_data = shmoo_data.sort_index(ascending=False)
    is_pass = shmoo_data >= pass_threshold

    plt.figure(figsize=(8, 5))
    plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial']
    cmap = sns.color_palette(["#ff4c4c", "#4caf50"]) 

    sns.heatmap(is_pass, cmap=cmap, annot=shmoo_data, fmt=".2f", 
                linewidths=.5, cbar=False, 
                annot_kws={"size": 11, "weight": "bold"})

    plt.title(f'Shmoo Plot: 2T0C Retention Time ({target_corner.upper()})\nPass Threshold: >= {pass_threshold} $\mu$s', 
              fontsize=14, fontweight='bold', pad=15)
    plt.xlabel('Temperature (°C)', fontsize=12, fontweight='bold')
    plt.ylabel('VDD Voltage (V)', fontsize=12, fontweight='bold')
    
    from matplotlib.patches import Patch
    legend_elements = [Patch(facecolor='#4caf50', label='PASS (Safe)'),
                       Patch(facecolor='#ff4c4c', label='FAIL (Violation)')]
    plt.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(1.3, 1))
    plt.tight_layout()
    
    output_img = f'{base_name}_Shmoo_{target_corner}.png'
    plt.savefig(output_img, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✅ Shmoo图已保存: {output_img}")

def plot_reliability_trends_split(df, base_name):
    """绘制全 PVT 矩阵的分面趋势图 (按 Corner 拆分，独立 Y 轴)"""
    print("⏳ 正在生成分面趋势图 (按 Corner 拆分)...")
    
    sns.set_style("whitegrid")
    plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial']
    
    # 核心修改：使用 FacetGrid 按 Corner 拆分成 3 个并排的子图
    # sharey=False 允许每个子图的 Y 轴独立缩放，这是拉开电压曲线间距的关键
    g = sns.FacetGrid(df, col="Corner", hue="Voltage", col_order=['SS', 'TT', 'FF'], 
                      sharey=False, height=5, aspect=1.1)
    
    # 在每个子图里画折线图
    g.map(sns.lineplot, "Temp", "RetentionTime", marker="o", markersize=8, linewidth=2)
    
    # 遍历每个子图进行精修
    for ax in g.axes.flat:
        ax.set_yscale('log') # 依然保持对数轴
        ax.axvline(x=125, color='red', linestyle='--', alpha=0.5)
        ax.grid(True, which="both", ls="-", alpha=0.3)
        ax.set_xlabel('Temperature (°C)', fontsize=12)
        
    # 设置左侧第一个子图的 Y 轴标签
    g.axes[0,0].set_ylabel('Retention Time ($\mu$s) - Log Scale', fontsize=12)
    
    # 添加全局图例和标题
    g.add_legend(title="VDD (V)", bbox_to_anchor=(1.02, 0.5), loc='center left')
    g.figure.subplots_adjust(top=0.85, right=0.9) # 腾出空间给标题和图例
    g.figure.suptitle('2T0C Retention Time vs. Temp (Separated by Corner)', fontsize=16, fontweight='bold')
    
    # 保存图片
    output_img = f'{base_name}_Split_Trend.png'
    plt.savefig(output_img, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"✅ 分面趋势图已保存: {output_img}")
# ==========================================
# 主控制流 (Main Pipeline)
# ==========================================
if __name__ == "__main__":
    print("="*50)
    print("🚀 芯片可靠性自动化出图系统启动")
    print("="*50)

    # 1. 解析命令行参数
    input_file = 'processed_2T0C_data.csv' # 默认文件
    target_corner = 'FF'                   # 默认画 FF 的 Shmoo
    threshold = 1.0                        # 默认及格线 1.0 us

    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    if len(sys.argv) > 2:
        target_corner = sys.argv[2]
    if len(sys.argv) > 3:
        threshold = float(sys.argv[3])

    # 2. 读取数据 (只读一次，提升效率)
    try:
        df = pd.read_csv(input_file)
        # 获取不带后缀的文件名，用于生成图片前缀
        base_name = os.path.splitext(input_file)[0] 
    except FileNotFoundError:
        print(f"❌ 致命错误：找不到数据文件 '{input_file}'！请先运行数据清洗脚本。")
        sys.exit(1)

   
   # 3. 依次调用三大绘图模块
    plot_reliability_trends(df, base_name)             # 第一张：全局趋势图
    plot_reliability_trends_split(df, base_name)       # 第二张：分面趋势图 
    plot_shmoo_matrix(df, base_name, target_corner, threshold) # 第三张：Shmoo 边界图

    print("="*50)
    print("🎉 所有报告生成完毕！请查看当前文件夹。")
    print("="*50)