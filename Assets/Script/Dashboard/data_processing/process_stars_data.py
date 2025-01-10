import json

input_file = "spy_analysis/data/scores_file.txt"  # 原始文件
output_file = "spy_analysis/data/scores_per_level.json"  # 输出文件

# 定义需要去掉的前缀
prefix_to_remove = "/users/tian/documents/all_m2/isg/project/spy_isg_2024-2025_groupb/assets/streamingassets/"

# 创建一个字典存储数据
data = {}

# 读取输入文件并解析内容
with open(input_file, "r") as infile:
    for line in infile:
        if ": {" in line:  # 确保是有效的内容行
            path, scores = line.strip().split(" : ", 1)  # 分割路径和分数部分
            if path.startswith(prefix_to_remove):
                path = path[len(prefix_to_remove):]  # 去掉指定的前缀
            scores_dict = json.loads(scores.replace("'", '"'))  # 将字符串格式的分数转换为字典
            data[path] = scores_dict  # 添加到字典中

# 将字典写入 JSON 文件
with open(output_file, "w") as outfile:
    json.dump(data, outfile, indent=4)

print(f"JSON file saved as {output_file}")