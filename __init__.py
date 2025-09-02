import importlib.util
import os
import sys
import json

NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}

python = sys.executable

def get_ext_dir(subpath=None, mkdir=False):
    dir = os.path.dirname(__file__)
    if subpath is not None:
        dir = os.path.join(dir, subpath)

    dir = os.path.abspath(dir)

    if mkdir and not os.path.exists(dir):
        os.makedirs(dir)
    return dir

def serialize(obj):
    if isinstance(obj, (str, int, float, bool, list, dict, type(None))):
        return obj
    return str(obj)

# 获取py目录路径
py = get_ext_dir("py")

# 遍历py目录中的所有.py文件
files = os.listdir(py)
all_nodes = {}

for file in files:
    if not file.endswith(".py"):
        continue
    name = os.path.splitext(file)[0]
    
    try:
        # 将模块导入也放入try块中
        imported_module = importlib.import_module(".py.{}".format(name), __name__)
        
        # 检查模块是否有必要的映射
        if hasattr(imported_module, 'NODE_CLASS_MAPPINGS') and hasattr(imported_module, 'NODE_DISPLAY_NAME_MAPPINGS'):
            NODE_CLASS_MAPPINGS = {**NODE_CLASS_MAPPINGS, **imported_module.NODE_CLASS_MAPPINGS}
            NODE_DISPLAY_NAME_MAPPINGS = {**NODE_DISPLAY_NAME_MAPPINGS, **imported_module.NODE_DISPLAY_NAME_MAPPINGS}
            
            serialized_CLASS_MAPPINGS = {k: serialize(v) for k, v in imported_module.NODE_CLASS_MAPPINGS.items()}
            serialized_DISPLAY_NAME_MAPPINGS = {k: serialize(v) for k, v in imported_module.NODE_DISPLAY_NAME_MAPPINGS.items()}
            all_nodes[file] = {
                "NODE_CLASS_MAPPINGS": serialized_CLASS_MAPPINGS, 
                "NODE_DISPLAY_NAME_MAPPINGS": serialized_DISPLAY_NAME_MAPPINGS
            }
            print(f"✅ 成功加载节点文件: {file} (节点数: {len(imported_module.NODE_CLASS_MAPPINGS)})")
        else:
            print(f"⚠️  跳过文件 {file}: 没有节点映射定义")
            
    except ImportError as e:
        print(f"❌ 导入失败 {file}: {str(e)}")
        print(f"   -> 这可能是由于语法错误或缺少依赖导致的")
    except AttributeError as e:
        print(f"⚠️  属性错误 {file}: {str(e)}")
        print(f"   -> 模块缺少必要的NODE_CLASS_MAPPINGS或NODE_DISPLAY_NAME_MAPPINGS")
    except Exception as e:
        print(f"❌ 加载错误 {file}: {str(e)}")
        print(f"   -> 其他未知错误")

print(f"\n📊 节点加载总结:")
print(f"   - 总共扫描文件: {len([f for f in files if f.endswith('.py')])}")
print(f"   - 成功加载文件: {len(all_nodes)}")
print(f"   - 可用节点总数: {len(NODE_CLASS_MAPPINGS)}")
if NODE_CLASS_MAPPINGS:
    print(f"   - 节点列表: {list(NODE_CLASS_MAPPINGS.keys())}")

# 定义web目录（如果需要前端资源）
WEB_DIRECTORY = "./js"

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"] 