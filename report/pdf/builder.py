import os
import base64
import time
import logging
from jinja2 import Environment, FileSystemLoader

from face_analysis.models import FullAnalysisResult
from report.text_generator import generate_all_texts
from report.pdf.charts import generate_radar_chart, generate_bell_curve, score_to_color, generate_score_bar
from report.pdf.renderer import render_pdf

METRIC_ORDER = [
    "face_symmetry", "face_proportions", "vertical_balance", "jaw_cheek_balance",
    "eye_size", "eye_spacing", "eye_tilt", "nose_width", "mouth_width", "nose_length",
    "chin_length", "chin_contour", "nose_to_mouth_ratio", "biocular_width",
    "forehead_width", "lip_fullness", "lip_proportions", "jaw_to_mouth",
    "eye_shape", "brow_height"
]

def _image_to_base64(filepath: str) -> str:
    """Helper to convert local image to base64 string."""
    if not os.path.exists(filepath):
        return ""
    with open(filepath, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("utf-8")
    ext = os.path.splitext(filepath)[1][1:].lower()
    if ext == "jpg":
        ext = "jpeg"
    return f"data:image/{ext};base64,{encoded}"


def _face_crop_base64(photo_path: str) -> str:
    """
    Aligned square face crop for the report (compact, no portrait stretching,
    keeps the cover circle an actual circle). Falls back to the raw photo.
    """
    try:
        import cv2
        from face_analysis.detector import detect_face
        from face_analysis.alignment import align_and_crop

        image = cv2.imread(photo_path)
        landmarks = detect_face(photo_path)
        if image is not None and landmarks is not None:
            crop = align_and_crop(image, landmarks.points)
            if crop is not None:
                ok, buf = cv2.imencode(".jpg", crop, [cv2.IMWRITE_JPEG_QUALITY, 88])
                if ok:
                    encoded = base64.b64encode(buf.tobytes()).decode("utf-8")
                    return f"data:image/jpeg;base64,{encoded}"
    except Exception as e:
        logging.warning(f"Face crop for report failed ({e}); using raw photo")
    return _image_to_base64(photo_path)

def parse_ai_text(raw_text: str, influence_word: str = "ВЛИЯНИЕ"):
    """
    Parses the 3-paragraph text from AI to extract body and influence.
    Assumes the last paragraph starts with something like **ВЛИЯНИЕ** or ВЛИЯНИЕ.
    """
    lines = raw_text.split('\n')
    body_lines = []
    influence_lines = []
    in_influence = False
    
    for line in lines:
        if influence_word in line.upper() or "ВЛИЯНИЕ" in line.upper() or "IMPACT" in line.upper():
            in_influence = True
            cleaned_line = line.replace("**", "")
            for w in (influence_word, "ВЛИЯНИЕ", "IMPACT"):
                cleaned_line = cleaned_line.replace(f"{w}:", "").replace(w, "")
            cleaned_line = cleaned_line.strip()
            if cleaned_line:
                influence_lines.append(cleaned_line)
        elif in_influence:
            influence_lines.append(line.strip())
        else:
            if line.strip():
                body_lines.append(f"<p>{line.strip()}</p>")
                
    ai_body = "\n".join(body_lines)
    ai_influence = " ".join(influence_lines).strip()
    if not ai_influence:
        ai_influence = ("Affects the overall perception of facial harmony."
                        if influence_word == "IMPACT"
                        else "Влияет на общее восприятие гармонии лица.")
        
    return ai_body, ai_influence

def build_report(result: FullAnalysisResult, photo_path: str, output_path: str, lang: str = "ru") -> str:
    """
    Full pipeline to generate the PDF report.
    """
    start_time = time.time()
    is_en = (lang or "").startswith("en")
    from bot.locales import get_locale
    t = get_locale(lang).PDF_T
    influence_word = "IMPACT" if is_en else "ВЛИЯНИЕ"
    logging.info(f"Starting report generation (lang={lang})...")

    # 1. Generate texts
    logging.info("Generating AI texts...")
    texts = generate_all_texts(result, lang)
    
    # 2. Setup Jinja2 environment
    templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
    env = Environment(loader=FileSystemLoader(templates_dir))
    
    # Load templates
    cover_tpl = env.get_template("cover.html")
    summary_tpl = env.get_template("summary.html")
    metric_card_tpl = env.get_template("metric_card.html")
    advice_tpl = env.get_template("advice.html")
    
    photo_b64 = _face_crop_base64(photo_path)
    
    # Render parts
    html_parts = []
    
    # --- Cover Page ---
    logging.info("Generating cover page...")
    cover_bell = generate_bell_curve((result.overall_score - 5) / 2) # rough estimate of overall sigma
    
    # Map metric names to display names for strengths. top_strengths stores
    # RUSSIAN names (calculator legacy), so key the map by BOTH the internal
    # name and name_ru — otherwise EN covers show Russian badges.
    metric_name_map = {}
    for m in result.metrics:
        display = m.name_en if is_en and m.name_en else m.name_ru
        metric_name_map[m.name] = display
        metric_name_map[m.name_ru] = display
    top_strengths_ru = [metric_name_map.get(name, name) for name in result.top_strengths]
    
    html_parts.append(cover_tpl.render(
        photo_b64=photo_b64,
        result=result,
        bell_curve_b64=cover_bell,
        top_strengths_ru=top_strengths_ru,
        t=t,
    ))
    
    # --- Summary Page ---
    logging.info("Generating summary page...")
    radar_chart_b64 = generate_radar_chart(result.metrics, lang)
    html_parts.append(summary_tpl.render(
        radar_chart_b64=radar_chart_b64,
        overall_summary=texts["overall_summary"],
        t=t,
    ))
    
    # --- Metric Pages ---
    logging.info("Generating metric pages...")
    # Sort metrics based on METRIC_ORDER
    sorted_metrics = sorted(result.metrics, key=lambda m: METRIC_ORDER.index(m.name) if m.name in METRIC_ORDER else 999)
    
    for i, metric in enumerate(sorted_metrics, start=1):
        score_color = score_to_color(metric.score)
        score_bar_b64 = generate_score_bar(metric.score, score_color)
        bell_curve_b64 = generate_bell_curve(metric.sigma_deviation)
        
        raw_text = texts["metric_texts"].get(metric.name, "")
        ai_body, ai_influence = parse_ai_text(raw_text, influence_word)

        metric_display_name = metric.name_en if is_en and metric.name_en else metric.name_ru
        metric_display_desc = metric.description_en if is_en and metric.description_en else metric.description
        html_parts.append(metric_card_tpl.render(
            metric=metric,
            metric_display_name=metric_display_name,
            metric_display_desc=metric_display_desc,
            metric_num=i,
            total_metrics=len(sorted_metrics),
            photo_b64=photo_b64,
            t=t,
            score_color=score_color,
            score_bar_b64=score_bar_b64,
            bell_curve_b64=bell_curve_b64,
            ai_body=ai_body,
            ai_influence=ai_influence
        ))
        
    # --- Advice Page ---
    logging.info("Generating advice page...")
    html_parts.append(advice_tpl.render(
        advice_items=texts["advice"],
        t=t,
    ))
    
    # Combine HTML
    full_html = "\n".join(html_parts)
    
    # 5. Render PDF
    logging.info("Rendering PDF via WeasyPrint...")
    final_path = render_pdf(full_html, output_path)
    
    duration = time.time() - start_time
    logging.info(f"Report successfully built in {duration:.1f}s at {final_path}")
    
    return final_path
