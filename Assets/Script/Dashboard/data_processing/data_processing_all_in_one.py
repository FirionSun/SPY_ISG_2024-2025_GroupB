from step1_download_users_statements import process_user_statements
from step2_statements_raw_data_processing import process_statements_from_file
from step3_level_data_proceissing import process_level_data
from step4_level_data_general_processing import process_level_data_general_with_competencies  # 新增导入

# 定义用户列表
user_ids = ["3D37C851", "59B6B585", "4C6ED003", "6DFE62E7"]

# Step 1: 下载用户 Statements
step1_output_file = "Assets/Script/Dashboard/data/step1_user_statements.json"
process_user_statements(user_ids, step1_output_file)

# Step 2: 处理 Raw Statements 数据
step2_input_file = step1_output_file
step2_output_file = "Assets/Script/Dashboard/data/step2_processed_statements.json"
process_statements_from_file(step2_input_file, step2_output_file)

# Step 3: 进一步清理和处理 Level Data
step3_input_file = step2_output_file
step3_output_file = "Assets/Script/Dashboard/data/step3_level_data_cleaned.json"
process_level_data(step3_input_file, step3_output_file)

# Step 4: 生成关卡的通用信息并匹配 Competencies
step4_input_file = step3_output_file
competency_file = "Assets/Script/Dashboard/data/competenciesReferential.json"
step4_output_file = "Assets/Script/Dashboard/data/step4_level_data_general.json"
process_level_data_general_with_competencies(step4_input_file, competency_file, step4_output_file)

print(f"All processing steps completed. Final data saved to {step4_output_file}.")
