import pandas as pd
import numpy as np
import sys

def clean_cadence_data(input_csv, output_csv):
    print(f"开始解析 Cadence 原始数据: {input_csv} ...")
    
    # 1. 读取原始 CSV
    df = pd.read_csv(input_csv)
    
    # 2. 定义环境映射字典
    # 根据你导出的表头，提取对应的温度和 Corner 组合
    temps = [-40, 27, 50, 75, 100, 125]
    corners = ['ff', 'ss', 'tt']
    
    col_names = []
    for c in corners:
        for i in range(len(temps)):
            col_names.append(f"{c}_{i}") # 生成如 'ff_0', 'ff_1' 等列名匹配原始数据

    # 3. 定位电压块与对应的数据行
    # 注意：这里的行号 (25, 32, 39) 是基于你上传的 CSV 中 'retentiontime' 所在的索引。
    # 如果以后导出的表格结构有变，只需修改这个字典即可。
    wwl_values = {
        25: 1.8,  # 第一组：WWL = 1.8V
        32: 2.0,  # 第二组：WWL = 2.0V
        39: 2.2   # 第三组：WWL = 2.2V
    }

    data_rows = []

    # 4. 遍历提取数据
    for idx, wwl in wwl_values.items():
        row = df.loc[idx]
        for col_name in col_names:
            val_str = str(row[col_name])
            try:
                val = float(val_str)
            except ValueError:
                val = np.nan
            
            # 从列名中解析出具体的 Corner 和 Temp
            corner = col_name.split('_')[0].upper()
            temp_idx = int(col_name.split('_')[1])
            temp = temps[temp_idx]
            
            data_rows.append({
                'Corner': corner,
                'Voltage': wwl,
                'Temp': temp,
                'RetentionTime': val
            })

    # 5. 生成结构化 DataFrame 并保存
    tidy_df = pd.DataFrame(data_rows)
    tidy_df.dropna(inplace=True) # 清除可能的空数据
    
    tidy_df.to_csv(output_csv, index=False)
    print(f"数据清洗完成！已保存至干净格式: {output_csv}")
    print(tidy_df.head()) # 打印前几行预览

if __name__ == "__main__":
    # 检查你运行脚本时有没有附带文件名
    if len(sys.argv) > 1:
        input_file = sys.argv[1]  # 获取你输入的第一个文件名
        output_file = "processed_" + input_file # 自动生成输出文件名
    else:
        # 如果你没输入，就用默认的
        input_file = '2T0C_PVT.csv'
        output_file = 'processed_2T0C_data.csv'
        
    clean_cadence_data(input_file, output_file)