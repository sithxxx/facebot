import logging
from face_analysis.models import FullAnalysisResult, MetricResult
from report.pdf.builder import build_report

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

def run_demo():
    # Mock some data
    metrics = [
        MetricResult(name="face_symmetry", name_ru="Симметрия лица", raw_value=0.58, norm_value=0.55, sigma_deviation=1.5, score=9.0, description="Сравнение билатеральных точек"),
        MetricResult(name="face_proportions", name_ru="Пропорции лица", raw_value=1.6, norm_value=1.618, sigma_deviation=0.2, score=8.5, description="Отношение ширины к высоте"),
        MetricResult(name="vertical_balance", name_ru="Вертикальный баланс", raw_value=0.33, norm_value=0.33, sigma_deviation=0.0, score=9.5, description="Правило третей"),
        MetricResult(name="jaw_cheek_balance", name_ru="Баланс челюсти и скул", raw_value=0.85, norm_value=0.88, sigma_deviation=-0.5, score=7.0, description="Отношение ширины челюсти к скулам"),
        MetricResult(name="eye_size", name_ru="Размер глаз", raw_value=0.05, norm_value=0.06, sigma_deviation=-1.0, score=5.0, description="Площадь глаз к лицу"),
        MetricResult(name="eye_spacing", name_ru="Межзрачковое расстояние", raw_value=0.46, norm_value=0.46, sigma_deviation=0.0, score=9.0, description="Дистанция между зрачками"),
        MetricResult(name="eye_tilt", name_ru="Наклон глаз", raw_value=5.0, norm_value=3.0, sigma_deviation=0.8, score=8.0, description="Угол наклона кантуса"),
        MetricResult(name="nose_width", name_ru="Ширина носа", raw_value=0.25, norm_value=0.25, sigma_deviation=0.0, score=9.0, description="Ширина носа к лицу"),
        MetricResult(name="mouth_width", name_ru="Ширина рта", raw_value=0.32, norm_value=0.31, sigma_deviation=0.2, score=8.5, description="Ширина рта к скулам"),
        MetricResult(name="nose_length", name_ru="Длина носа", raw_value=0.34, norm_value=0.33, sigma_deviation=0.3, score=8.0, description="Длина носа к лицу"),
        MetricResult(name="chin_length", name_ru="Длина подбородка", raw_value=0.18, norm_value=0.17, sigma_deviation=0.4, score=8.0, description="Длина подбородка"),
        MetricResult(name="chin_contour", name_ru="Контур подбородка", raw_value=120, norm_value=125, sigma_deviation=-0.8, score=6.0, description="Угол челюсти"),
        MetricResult(name="nose_to_mouth_ratio", name_ru="Отношение носа ко рту", raw_value=0.78, norm_value=0.8, sigma_deviation=-0.2, score=8.0, description="Ширина носа ко рту"),
        MetricResult(name="biocular_width", name_ru="Биокулярная ширина", raw_value=0.6, norm_value=0.6, sigma_deviation=0.0, score=9.0, description="Расстояние между внешними кантусами"),
        MetricResult(name="forehead_width", name_ru="Ширина лба", raw_value=0.5, norm_value=0.5, sigma_deviation=0.0, score=8.5, description="Ширина лба к лицу"),
        MetricResult(name="lip_fullness", name_ru="Полнота губ", raw_value=0.03, norm_value=0.04, sigma_deviation=-1.5, score=4.0, description="Толщина губ"),
        MetricResult(name="lip_proportions", name_ru="Пропорции губ", raw_value=1.0, norm_value=1.6, sigma_deviation=-2.0, score=3.0, description="Верхняя губа к нижней"),
        MetricResult(name="jaw_to_mouth", name_ru="От челюсти до рта", raw_value=1.5, norm_value=1.5, sigma_deviation=0.0, score=9.0, description="Ширина челюсти ко рту"),
        MetricResult(name="eye_shape", name_ru="Форма глаз", raw_value=0.4, norm_value=0.4, sigma_deviation=0.0, score=8.5, description="Ширина к высоте глаза"),
        MetricResult(name="brow_height", name_ru="Высота бровей", raw_value=0.05, norm_value=0.05, sigma_deviation=0.0, score=8.5, description="Расстояние от глаза до брови"),
    ]
    
    result = FullAnalysisResult(
        metrics=metrics,
        overall_score=7.8,
        top_strengths=["face_symmetry", "vertical_balance", "eye_spacing"],
        top_weaknesses=["lip_proportions", "lip_fullness", "eye_size"],
        gender="male"
    )

    # Need a dummy photo
    with open("dummy_photo.jpg", "wb") as f:
        # Just write an empty file or a minimal valid JPEG. 
        # But an empty file won't render properly. Let's create a solid color image using matplotlib.
        pass
        
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(3, 4))
    ax.set_facecolor('#111111')
    ax.text(0.5, 0.5, 'Face Image Placeholder', color='white', ha='center', va='center')
    ax.axis('off')
    fig.savefig('dummy_photo.jpg', format='jpg', bbox_inches='tight')
    plt.close(fig)

    build_report(result, "dummy_photo.jpg", "report_output.pdf")
    logging.info("Demo complete. Check report_output.pdf")

if __name__ == "__main__":
    run_demo()
