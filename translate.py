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

    if not content:
        print(f"⚠️ Skipping empty file: {file_path}")
        return  # 跳过空文件

    translated_content = translate_text(content)

    # 生成 `en/` 目录路径
    relative_path = os.path.relpath(file_path, "zh")  # 获取相对路径，如 "README.md"
    new_file_path = os.path.join("en", relative_path)  # 生成 en 目录路径

    os.makedirs(os.path.dirname(new_file_path), exist_ok=True)

    # 确保翻译内容被正确写入
    with open(new_file_path, "w", encoding="utf-8") as f:
        f.write(translated_content)

    print(f"✅ Translated {file_path} -> {new_file_path}")

# 遍历 `zh/` 目录下的所有 Markdown 文件，并翻译到 `en/`
for md_file in glob.glob("zh/**/*.md", recursive=True):
    translate_markdown(md_file)

print("🚀 Translation completed! Check the 'en/' directory for translated files.")