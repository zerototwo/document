import os
import glob
from googletrans import Translator

translator = Translator()
target_lang = "en"

def translate_text(text):
    """ 使用 Google Translate 翻译 """
    try:
        return translator.translate(text, dest=target_lang).text
    except Exception as e:
        print(f"Translation error: {e}")
        return text

def translate_markdown(file_path):
    """ 读取 Markdown 文件并翻译 """
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    translated_content = translate_text(content)

    # 生成英文版文件
    new_file_path = file_path.replace("/zh/", "/en/")
    os.makedirs(os.path.dirname(new_file_path), exist_ok=True)

    with open(new_file_path, "w", encoding="utf-8") as f:
        f.write(translated_content)

    print(f"Translated {file_path} -> {new_file_path}")

# 遍历 `zh/` 目录下的所有 Markdown 文件，并翻译到 `en/`
for md_file in glob.glob("zh/**/*.md", recursive=True):
    translate_markdown(md_file)