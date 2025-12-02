import re
import requests
from io import BytesIO
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import fitz  # PyMuPDF
from docx import Document
from docx.shared import RGBColor
from docx.oxml.ns import qn
from docx.oxml.text.run import CT_R

# 复用原代码的全局配置
ALLOWED_FONTS = {"宋体", "微软雅黑", "黑体", "Arial", "Times New Roman", "SimSun", "Microsoft YaHei"}
ALLOWED_EXTENSIONS = {'docx', 'pdf', 'txt', 'json'}
MIN_TITLE_LENGTH = 2
MAX_TITLE_LEVEL = 6
FONT_SIZE_THRESHOLD = 1.5

# 复用原代码的工具函数（保持样式提取逻辑一致）
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def rgb_to_rgb_str(rgb):
    if not rgb:
        return "rgb(0,0,0)"
    if isinstance(rgb, (tuple, list)):
        r, g, b = [int(x) for x in rgb[:3]]
    elif isinstance(rgb, RGBColor):
        r, g, b = rgb.r, rgb.g, rgb.b
    else:
        return "rgb(0,0,0)"
    return f"rgb({max(0, min(255, r))},{max(0, min(255, g))},{max(0, min(255, b))})"

def filter_font(font_name):
    if not font_name:
        return "宋体"
    cleaned = font_name.strip()
    font_alias = {
        "SimSun": "宋体",
        "Microsoft YaHei": "微软雅黑",
        "SimHei": "黑体"
    }
    if cleaned in ALLOWED_FONTS:
        return cleaned
    for alias, std_name in font_alias.items():
        if cleaned.lower() == alias.lower():
            return std_name
    for std_font in ALLOWED_FONTS:
        if std_font.lower() in cleaned.lower():
            return std_font
    return "宋体"

# 复用原文件解析函数（直接从原文件提取带样式的标题）
def extract_word_titles(file_content):
    doc = Document(BytesIO(file_content))
    titles = []
    style_level_map = {
        'Heading 1': 1, '标题 1': 1, 'Heading 2': 2, '标题 2': 2,
        'Heading 3': 3, '标题 3': 3, 'Heading 4': 4, '标题 4': 4,
        'Heading 5': 5, '标题 5': 5, 'Heading 6': 6, '标题 6': 6
    }
    for para in doc.paragraphs:
        text = para.text.strip()
        if not text or len(text) < MIN_TITLE_LENGTH:
            continue
        style_name = para.style.name
        level = style_level_map.get(style_name)
        if level is None:
            continue  # 只保留明确的标题样式
        run = para.runs[0] if para.runs else None
        raw_font = "未知"
        if run:
            if run.font.name:
                raw_font = run.font.name
            elif hasattr(run, '_element') and isinstance(run._element, CT_R):
                r_pr = run._element.rPr
                if r_pr and hasattr(r_pr, 'rFonts'):
                    raw_font = r_pr.rFonts.get(qn('w:eastAsia')) or r_pr.rFonts.get(qn('w:ascii')) or "未知"
        font = filter_font(raw_font)
        size = run.font.size.pt if (run and run.font.size) else 12
        color = rgb_to_rgb_str(run.font.color.rgb) if (run and run.font.color.rgb) else "rgb(0,0,0)"
        bold = run.font.bold if (run and run.font.bold is not None) else False
        italic = run.font.italic if (run and run.font.italic is not None) else False
        titles.append({
            "title": text,
            "font": font,
            "size": size,
            "color": color,
            "bold": bold,
            "italic": italic,
            "raw_title": text  # 保留原始文本用于匹配
        })
    return titles

def extract_pdf_titles(file_content):
    doc = fitz.open(stream=BytesIO(file_content), filetype="pdf")
    titles = []
    for page in doc:
        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            if "lines" not in block:
                continue
            block_text = []
            block_size = []
            block_bold = False
            block_font = []
            block_color = []
            for line in block["lines"]:
                for span in line["spans"]:
                    block_text.append(span["text"])
                    block_size.append(span["size"])
                    block_font.append(span["font"])
                    block_color.append(span["color"])
                    if "bold" in span["font"].lower() or "heavy" in span["font"].lower():
                        block_bold = True
            if not block_text:
                continue
            full_text = "".join(block_text).strip()
            if len(full_text) < MIN_TITLE_LENGTH:
                continue
            avg_size = sum(block_size) / len(block_size)
            if avg_size < 10 and not block_bold:
                continue
            main_font = block_font[0] if block_font else "未知"
            font = filter_font(main_font)
            color = rgb_to_rgb_str((
                (block_color[0] >> 16) & 0xFF,
                (block_color[0] >> 8) & 0xFF,
                block_color[0] & 0xFF
            ))
            italic = any("italic" in f.lower() or "oblique" in f.lower() for f in block_font)
            titles.append({
                "title": full_text,
                "font": font,
                "size": round(avg_size, 1),
                "color": color,
                "bold": block_bold,
                "italic": italic,
                "raw_title": full_text  # 保留原始文本用于匹配
            })
    return titles

# 从Markdown提取标题结构（仅层级和文本）
def extract_markdown_structure(markdown_content):
    pattern = r'^(#{1,6})\s+(.*?)\s*$'
    structure = []
    for line in markdown_content.split('\n'):
        match = re.match(pattern, line.strip())
        if match:
            level = len(match.group(1))
            level = min(level, MAX_TITLE_LEVEL)
            title_text = match.group(2).strip()
            structure.append({
                "title": title_text,
                "id_level": level,
                "children": []
            })
    return structure

# 核心：关联Markdown结构与原文件样式（通过标题文本模糊匹配）
def merge_structure_with_styles(markdown_structure, original_titles):
    # 预处理原文件标题：简化文本（去标点、空格）用于匹配
    original_clean_map = {}
    for orig in original_titles:
        clean_text = re.sub(r'[^\w\s]', '', orig["raw_title"]).lower().strip()
        original_clean_map[clean_text] = orig  # 用清洗后的文本作为键
    
    # 遍历Markdown结构，匹配样式
    for md_title in markdown_structure:
        md_clean = re.sub(r'[^\w\s]', '', md_title["title"]).lower().strip()
        # 模糊匹配（优先完全匹配，再部分匹配）
        matched = original_clean_map.get(md_clean)
        if not matched:
            for clean_orig, orig in original_clean_map.items():
                if md_clean in clean_orig or clean_orig in md_clean:
                    matched = orig
                    break
        # 补充样式信息
        if matched:
            md_title["font"] = matched["font"]
            md_title["size"] = matched["size"]
            md_title["color"] = matched["color"]
            md_title["bold"] = matched["bold"]
            md_title["italic"] = matched["italic"]
        else:
            # 匹配失败时用默认样式
            md_title["font"] = "宋体"
            md_title["size"] = 12 + (6 - md_title["id_level"]) * 2
            md_title["color"] = "rgb(0,0,0)"
            md_title["bold"] = True if md_title["id_level"] <= 3 else False
            md_title["italic"] = False
    return markdown_structure

# 复用层级构建函数
def build_title_hierarchy(titles):
    if not titles:
        return []
    root = []
    stack = []
    for title in titles:
        level = title["id_level"]
        while stack and stack[-1]["id_level"] >= level:
            stack.pop()
        if stack:
            stack[-1]["children"].append(title)
        else:
            root.append(title)
        stack.append(title)
    return root

# 主处理函数：先转发获取Markdown结构，再读原文件补样式
def upload_file_from_frontend(frontend_file):
    target_url = "http://192.168.0.97:7333/v2/parse/file"
    try:
        # 1. 读取原文件内容（用于后续提取样式）
        file_content = frontend_file.read()
        frontend_file.seek(0)  # 重置文件指针，避免后续读取失败
        
        # 2. 转发文件获取Markdown内容，提取标题结构
        files = {
            'file': (frontend_file.name, frontend_file.read(), frontend_file.content_type)
        }
        headers = {'accept': 'application/json'}
        response = requests.post(url=target_url, headers=headers, files=files)
        
        if response.status_code != 200:
            return {"success": False, "error": f"服务响应错误: {response.status_code}"}
        
        result = response.json()
        markdown_content = result.get('markdown', '')
        md_structure = extract_markdown_structure(markdown_content)
        if not md_structure:
            return {"success": False, "error": "未从Markdown中提取到标题"}
        
        # 3. 从原文件提取带样式的标题
        ext = frontend_file.name.rsplit('.', 1)[1].lower()
        if ext == 'docx':
            original_titles = extract_word_titles(file_content)
        elif ext == 'pdf':
            original_titles = extract_pdf_titles(file_content)
        else:
            return {"success": False, "error": f"暂不支持{ext}文件的样式提取"}
        
        if not original_titles:
            return {"success": False, "error": "未从原文件中提取到标题"}
        
        # 4. 关联结构与样式，构建最终层级
        merged_titles = merge_structure_with_styles(md_structure, original_titles)
        hierarchy = build_title_hierarchy(merged_titles)
        
        return hierarchy;
    
    except Exception as e:
        return {"success": False, "error": f"处理失败：{str(e)}"}

