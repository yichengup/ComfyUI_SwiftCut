import torch
from torch import Tensor
import re
from typing import Union, List, Tuple

# 定义常量
BIGMIN = -(2**53-1)
BIGMAX = 2**53-1

def convert_str_to_indexes(text: str, total_frames: int) -> List[int]:
    """将字符串转换为索引列表
    
    支持格式:
    - 单个索引: "5"
    - 多个索引: "1,3,5"
    - 范围: "3-10"
    - 混合: "1,3-5,8,10-15"
    - 负索引: "-1" (最后一帧)
    - 步长: "0-10:2" (0到10每隔2帧)
    """
    if not text.strip():
        return []
    
    indexes = []
    parts = text.split(',')
    
    for part in parts:
        part = part.strip()
        if not part:
            continue
            
        # 处理范围格式 "start-end" 或 "start-end:step"
        if '-' in part and not part.startswith('-'):
            # 检查是否有步长
            if ':' in part:
                range_part, step_str = part.split(':', 1)
                try:
                    step = int(step_str)
                except ValueError:
                    step = 1
            else:
                range_part = part
                step = 1
                
            # 解析范围
            try:
                start_str, end_str = range_part.split('-', 1)
                start = int(start_str)
                end = int(end_str)
                
                # 处理负索引
                if start < 0:
                    start = total_frames + start
                if end < 0:
                    end = total_frames + end
                    
                # 确保范围有效
                start = max(0, min(start, total_frames - 1))
                end = max(0, min(end, total_frames - 1))
                
                # 生成范围内的索引
                if start <= end:
                    indexes.extend(range(start, end + 1, step))
                else:
                    indexes.extend(range(start, end - 1, -step))
                    
            except ValueError:
                # 如果解析失败，尝试作为单个索引处理
                try:
                    idx = int(part)
                    if idx < 0:
                        idx = total_frames + idx
                    if 0 <= idx < total_frames:
                        indexes.append(idx)
                except ValueError:
                    pass
        else:
            # 处理单个索引
            try:
                idx = int(part)
                if idx < 0:
                    idx = total_frames + idx
                if 0 <= idx < total_frames:
                    indexes.append(idx)
            except ValueError:
                pass
    
    # 去重并排序
    indexes = sorted(list(set(indexes)))
    return indexes

def select_indexes(input_obj: Tensor, indexes: List[int]) -> Tensor:
    """根据索引列表选择tensor中的数据"""
    if not indexes:
        return input_obj[:0]  # 返回空tensor，保持维度结构
    
    # 确保索引在有效范围内
    valid_indexes = [idx for idx in indexes if 0 <= idx < input_obj.shape[0]]
    
    if not valid_indexes:
        return input_obj[:0]  # 返回空tensor
    
    return input_obj[valid_indexes]

def select_indexes_from_str(input_obj: Tensor, indexes: str, 
                            err_if_missing: bool = True, 
                            err_if_empty: bool = True) -> Tensor:
    """从字符串索引选择tensor数据"""
    total_frames = input_obj.shape[0]
    
    # 转换字符串为索引列表
    index_list = convert_str_to_indexes(indexes, total_frames)
    
    # 检查错误条件
    if err_if_empty and not index_list:
        raise ValueError(f"没有有效的索引被选择。输入: '{indexes}', 总帧数: {total_frames}")
    
    if err_if_missing:
        # 检查是否有索引超出范围
        invalid_indexes = [idx for idx in index_list if idx >= total_frames or idx < 0]
        if invalid_indexes:
            raise ValueError(f"索引超出范围: {invalid_indexes}, 总帧数: {total_frames}")
    
    # 选择数据
    return select_indexes(input_obj, index_list)

# 描述文本
select_description = """
Image Index Selection Node

Supported Index Formats:
- Single Index: "5" (Selects the 6th image, counting from 0)
- Multiple Indexes: "1,3,5" (Selects the 2nd, 4th, and 6th images)
- Range Selection: "3-10" (Selects the 4th to 11th images)
- Range with Step: "0-10:2" (Selects the 1st, 3rd, 5th, 7th, 9th, and 11th images)
- Mixed Format: "1,3-5,8,10-15" (Selects the 1st, 3rd, 4th, 5th, 8th, 10th, 11th, 12th, 13th, 14th, and 15th images)
- Negative Index: "-1" (Selects the last image), "-3--1" (Selects the last 3 images)

Parameter Description:
- err_if_missing: Whether to report an error if the index is out of range
- err_if_empty: Whether to report an error if no images are selected
""" 