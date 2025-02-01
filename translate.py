import os
import glob
from deep_translator import GoogleTranslator

translator = GoogleTranslator(source='zh-CN', target='en')

def translate_text(text):
    """ 使用 Google Translate 进行翻译 """
    try:
        translated = translator.translate(text)
        return translated if translated else text  # 避免空返回
    except Exception as e:
        print(f"Translation error: {e}")
        return text

def translate_folder_name(folder_name):
    """ 翻译文件夹名称 """
    return translate_text(folder_name)

def translate_markdown(file_path, zh_root="zh", en_root="en"):
    """ 读取 Markdown 文件并翻译，并保存到 `en/` 目录 """
    relative_path = os.path.relpath(file_path, zh_root)  # 获取相对路径
    translated_parts = [translate_folder_name(part) for part in relative_path.split(os.sep)]  # 翻译路径中的文件夹
    new_file_path = os.path.join(en_root, *translated_parts)  # 生成 `en/` 目录路径

    os.makedirs(os.path.dirname(new_file_path), exist_ok=True)

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read().strip()

    # 如果文件为空，仍然创建空文件
    if not content:
        print(f"⚠️ Empty file detected, creating empty file in en/: {file_path}")
        open(new_file_path, 'w').close()
        return

    translated_content = translate_text(content)

    with open(new_file_path, "w", encoding="utf-8") as f:
        f.write(translated_content)

    print(f"✅ Translated {file_path} -> {new_file_path}")

def sync_en_directory(zh_root="zh", en_root="en"):
    """ 确保 `en/` 目录与 `zh/` 目录结构同步（包括翻译文件夹名称） """
    zh_dirs = {os.path.relpath(root, zh_root) for root, _, _ in os.walk(zh_root)}

    for zh_dir in zh_dirs:
        translated_parts = [translate_folder_name(part) for part in zh_dir.split(os.sep)]  # 翻译文件夹名
        en_dir_path = os.path.join(en_root, *translated_parts)
        os.makedirs(en_dir_path, exist_ok=True)

    print("✅ `en/` 目录同步完成，文件夹名称已翻译！")

# 先同步 `en/` 目录结构（包括空目录和翻译文件夹名）
sync_en_directory()

# 遍历 `zh/` 目录下的所有 Markdown 文件，并翻译到 `en/`
for md_file in glob.glob("zh/**/*.md", recursive=True):
    translate_markdown(md_file)

print("🚀 Translation completed! Check the 'en/' directory for translated files.")