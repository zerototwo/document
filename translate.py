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

def translate_markdown(file_path):
    """ 读取 Markdown 文件并翻译，并保存到 `en/` 目录 """
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read().strip()

    # 生成 `en/` 目录路径
    relative_path = os.path.relpath(file_path, "zh")  # 获取相对路径，如 "README.md"
    new_file_path = os.path.join("en", relative_path)  # 生成 en 目录路径

    os.makedirs(os.path.dirname(new_file_path), exist_ok=True)

    # 如果文件为空，仍然创建空文件
    if not content:
        print(f"⚠️ Empty file detected, creating empty file in en/: {file_path}")
        open(new_file_path, 'w').close()  # 创建一个空文件
        return

    translated_content = translate_text(content)

    # 确保翻译内容被正确写入
    with open(new_file_path, "w", encoding="utf-8") as f:
        f.write(translated_content)

    print(f"✅ Translated {file_path} -> {new_file_path}")

def sync_en_directory():
    """ 确保 `en/` 目录与 `zh/` 目录结构同步（包括空目录和空文件） """
    zh_dirs = {os.path.relpath(root, "zh") for root, _, _ in os.walk("zh")}
    en_dirs = {os.path.relpath(root, "en") for root, _, _ in os.walk("en")}

    # 确保 `en/` 目录中的所有 `zh/` 目录都存在
    for zh_dir in zh_dirs:
        en_dir_path = os.path.join("en", zh_dir)
        os.makedirs(en_dir_path, exist_ok=True)

    # 同步 `.md` 文件，确保 `en/` 目录没有多余的文件
    zh_files = {os.path.relpath(f, "zh") for f in glob.glob("zh/**/*.md", recursive=True)}
    en_files = {os.path.relpath(f, "en") for f in glob.glob("en/**/*.md", recursive=True)}
    extra_files = en_files - zh_files

    for extra_file in extra_files:
        en_file_path = os.path.join("en", extra_file)
        os.remove(en_file_path)
        print(f"🗑️ Removed {en_file_path}")

# 先同步 `en/` 目录结构（包括空目录）
sync_en_directory()

# 遍历 `zh/` 目录下的所有 Markdown 文件，并翻译到 `en/`
for md_file in glob.glob("zh/**/*.md", recursive=True):
    translate_markdown(md_file)

print("🚀 Translation completed! Check the 'en/' directory for translated files.")