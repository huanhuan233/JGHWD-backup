import re
from io import BytesIO
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import fitz  # PyMuPDF
from docx import Document
from docx.shared import RGBColor
from docx.oxml.ns import qn
from docx.oxml.text.run import CT_R

# 允许的字体列表
ALLOWED_FONTS = {"宋体", "微软雅黑", "黑体", "Arial", "Times New Roman"}
# 允许的文件类型
ALLOWED_EXTENSIONS = {'docx', 'pdf','txt', 'json'}


def allowed_file(filename):
    """检查文件类型是否允许"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def rgb_to_rgb_str(rgb):
    """转换颜色为rgb(r,g,b)格式"""
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
    """过滤字体，仅保留允许的类型"""
    if not font_name:
        return "宋体"
    cleaned = font_name.strip()
    if cleaned in ALLOWED_FONTS:
        return cleaned
    if cleaned.lower() == "arial":
        return "Arial"
    if cleaned.lower() == "times new roman":
        return "Times New Roman"
    return "宋体"

def get_word_list_number(para):
    """提取Word内置标题编号"""
    try:
        p_pr = para._p.get_or_add_pPr()
        if not hasattr(p_pr, 'numPr') or p_pr.numPr is None:
            return ""
        num_pr = p_pr.numPr
        num_id = num_pr.numId.val if (hasattr(num_pr, 'numId') and num_pr.numId) else None
        ilvl = num_pr.ilvl.val if (hasattr(num_pr, 'ilvl') and num_pr.ilvl) else 0
        if num_id is None:
            return ""
        if not hasattr(para.part, 'numbering_part') or not para.part.numbering_part:
            return ""
        num_def = para.part.numbering_part.numbering_definitions._numbering
        num = num_def.get_num(num_id)
        if not num:
            return ""
        lvl = num.get_lvl(ilvl)
        if not lvl:
            return ""
        fmt = lvl.numFmt.val
        start = lvl.start.val if (hasattr(lvl, 'start') and lvl.start) else 1
        current = start + ilvl
        if fmt == 'chinese':
            chars = '一二三四五六七八九十'
            return f"{chars[current-1]}、" if current <= len(chars) else f"{current}、"
        elif fmt == 'decimal':
            return f"{current}."
        elif fmt == 'decimalEnclosedParen':
            return f"({current})"
        elif fmt == 'lowerLetter':
            return f"{chr(96 + current)}."
        elif fmt == 'upperLetter':
            return f"{chr(64 + current)}."
    except:
        return ""
    return ""

def get_word_font_name(run):
    """安全获取Word字体名称"""
    try:
        if run.font.name:
            return run.font.name
        if hasattr(run, '_element') and isinstance(run._element, CT_R):
            if hasattr(run._element, 'rPr') and run._element.rPr:
                r_pr = run._element.rPr
                if hasattr(r_pr, 'rFonts') and r_pr.rFonts:
                    east_asia = r_pr.rFonts.get(qn('w:eastAsia'))
                    if east_asia:
                        return east_asia
                    ascii_font = r_pr.rFonts.get(qn('w:ascii'))
                    if ascii_font:
                        return ascii_font
    except:
        pass
    return "未知"

def extract_word_titles(file_content):
    """从内存中的Word内容提取标题"""
    doc = Document(BytesIO(file_content))
    titles = []
    style_map = {
        'Heading 1': 1, '标题 1': 1,
        'Heading 2': 2, '标题 2': 2,
        'Heading 3': 3, '标题 3': 3,
        'Heading 4': 4, '标题 4': 4,
        'Heading 5': 5, '标题 5': 5,
        'Heading 6': 6, '标题 6': 6
    }
    
    for para in doc.paragraphs:
        text = para.text.strip()
        style = para.style.name
        if style not in style_map or not text:
            continue
        
        level = style_map[style]
        number = get_word_list_number(para)
        full_title = (number + text).strip()
        
        raw_font = "未知"
        if para.runs:
            raw_font = get_word_font_name(para.runs[0])
        font = filter_font(raw_font)
        
        size = 12
        if para.runs and para.runs[0].font.size:
            size = para.runs[0].font.size.pt
        
        color = "rgb(0,0,0)"
        if para.runs and para.runs[0].font.color.rgb:
            color = rgb_to_rgb_str(para.runs[0].font.color.rgb)
        
        bold = para.runs[0].font.bold if (para.runs and para.runs[0].font.bold is not None) else False
        italic = para.runs[0].font.italic if (para.runs and para.runs[0].font.italic is not None) else False
        
        titles.append({
            "title": full_title,
            "font": font,
            "size": size,
            "color": color,
            "bold": bold,
            "italic": italic,
            "id_level": level,
            "children": []
        })
    return titles

def extract_pdf_titles(file_content):
    """从内存中的PDF内容提取标题"""
    doc = fitz.open(stream=BytesIO(file_content), filetype="pdf")
    titles = []
    prev_size, prev_level = 0, 1
    
    for page in doc:
        for block in page.get_text("dict")["blocks"]:
            if "lines" not in block:
                continue
            for line in block["lines"]:
                spans = line["spans"]
                if not spans:
                    continue
                text = "".join([s["text"] for s in spans]).strip()
                if not text:
                    continue
                
                main_span = spans[0]
                size = main_span["size"]
                raw_font = main_span["font"]
                font = filter_font(raw_font)
                
                color_int = main_span["color"]
                color = rgb_to_rgb_str((
                    (color_int >> 16) & 0xFF,
                    (color_int >> 8) & 0xFF,
                    color_int & 0xFF
                ))
                
                bold = "bold" in raw_font.lower() or "heavy" in raw_font.lower()
                italic = "italic" in raw_font.lower() or "oblique" in raw_font.lower()
                
                level = prev_level
                if re.match(r'^[一二三四五六七八九十]+、', text):
                    level = 1
                elif re.match(r'^\（[一二三四五六七八九十]+\）', text):
                    level = 2
                elif re.match(r'^[0-9]+、', text):
                    level = 3
                elif re.match(r'^[0-9]+\.[0-9]+', text):
                    level = 4
                elif re.match(r'^[0-9]+\.[0-9]+\.[0-9]+', text):
                    level = 5
                elif re.match(r'^\([0-9]+\)', text):
                    level = 3
                
                if size > prev_size + 1:
                    level = max(1, prev_level - 1)
                elif size < prev_size - 1:
                    level = min(6, prev_level + 1)
                
                titles.append({
                    "title": text,
                    "font": font,
                    "size": round(size, 1),
                    "color": color,
                    "bold": bold,
                    "italic": italic,
                    "id_level": level,
                    "children": []
                })
                
                prev_size, prev_level = size, level
    return titles

def build_title_hierarchy(titles):
    """构建标题层级结构"""
    root, stack = [], []
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
