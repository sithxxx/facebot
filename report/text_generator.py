import json
import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import openai

from report.config import OPENAI_API_KEY, OPENAI_BASE_URL, OPENAI_MODEL, OPENAI_MAX_TOKENS, OPENAI_TEMPERATURE
from face_analysis.models import MetricResult, FullAnalysisResult
from report.prompts.metric_prompts import METRIC_PROMPTS, DEFAULT_METRIC_PROMPT
from report.prompts.summary_prompt import SUMMARY_PROMPT
from report.prompts.advice_prompt import ADVICE_PROMPT

client = openai.OpenAI(
    api_key=OPENAI_API_KEY,
    base_url=OPENAI_BASE_URL,
)

# Appended to every system prompt when the user language is English. The
# prompts themselves are written in English and instruct Russian output — a
# final override wins without rewriting 450 lines of prompt text.
EN_OVERRIDE = (
    "\n\nIMPORTANT LANGUAGE OVERRIDE: Ignore all earlier instructions about "
    "writing in Russian. Write the ENTIRE text in natural ENGLISH, second "
    "person. Where a bold lead word \'ВЛИЯНИЕ\' was requested, use \'IMPACT\' "
    "instead. Field names in any JSON output stay exactly as specified."
)


def _sys(prompt: str, lang: str) -> str:
    return prompt + EN_OVERRIDE if (lang or "").startswith("en") else prompt

def _call_openai_with_retry(messages: list, max_retries: int = 3, response_format=None, max_tokens: int | None = None) -> str:
    """Helper to call OpenAI API with exponential backoff on RateLimitError."""
    delays = [2, 4, 8]

    for attempt in range(max_retries + 1):
        try:
            kwargs = {
                "model": OPENAI_MODEL,
                "messages": messages,
                "max_tokens": max_tokens or OPENAI_MAX_TOKENS,
                "temperature": OPENAI_TEMPERATURE,
            }
            if response_format:
                kwargs["response_format"] = response_format

            response = client.chat.completions.create(**kwargs)
            content = response.choices[0].message.content
            # Some providers (e.g. DeepSeek) can return content=None when the
            # token budget is exhausted mid-generation. Retry, don't crash.
            if not content or not content.strip():
                if attempt < max_retries:
                    logging.warning("Empty completion content. Retrying...")
                    time.sleep(delays[attempt])
                    continue
                raise ValueError("Empty completion content after retries")
            return content.strip()

        except openai.RateLimitError as e:
            if attempt < max_retries:
                logging.warning(f"RateLimitError encountered. Retrying in {delays[attempt]}s...")
                time.sleep(delays[attempt])
            else:
                logging.error(f"Rate limit exceeded after {max_retries} retries.")
                raise e
        except openai.APIError as e:
            logging.error(f"OpenAI APIError: {e}")
            raise e
        except Exception as e:
            logging.error(f"Unexpected error calling OpenAI: {e}")
            raise e

def generate_metric_text(metric: MetricResult, gender: str, lang: str = "ru") -> str:
    """
    Generates 3-paragraph personalized analysis for a single metric.
    """
    system_prompt = _sys(METRIC_PROMPTS.get(metric.name, DEFAULT_METRIC_PROMPT), lang)

    is_en = (lang or "").startswith("en")
    metric_name = metric.name_en if is_en and metric.name_en else metric.name_ru
    if is_en:
        user_prompt = (
            f"Gender: {gender}\n"
            f"Metric: {metric_name}\n"
            f"Result: {metric.raw_value:.4f}\n"
            f"Norm: {metric.norm_value:.4f}\n"
            f"Deviation from the norm (in sigmas): {metric.sigma_deviation:.2f}\n"
            f"Score (1 to 10): {metric.score:.2f}\n"
        )
    else:
        user_prompt = (
            f"Пол: {gender}\n"
            f"Метрика: {metric.name_ru}\n"
            f"Результат: {metric.raw_value:.4f}\n"
            f"Норма: {metric.norm_value:.4f}\n"
            f"Отклонение от нормы (в сигмах): {metric.sigma_deviation:.2f}\n"
            f"Балл (от 1 до 10): {metric.score:.2f}\n"
        )
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    
    try:
        return _call_openai_with_retry(messages)
    except Exception:
        # Fallback template if API fails
        if is_en:
            return (
                f"The analysis for '{metric_name}' could not be generated due to a network error. "
                f"Your value is {metric.raw_value:.4f}, while the population norm is {metric.norm_value:.4f}. "
                f"Your final score for this parameter is {metric.score:.1f}/10.\n\n"
                "This is an important parameter of facial symmetry and proportion that plays a significant role in overall perception.\n\n"
                "**IMPACT:** Harmonious values of this parameter help create a balanced, aesthetic look."
            )
        return (
            f"Анализ метрики '{metric.name_ru}' не удалось сгенерировать из-за ошибки сети. "
            f"Твой показатель равен {metric.raw_value:.4f}, тогда как средняя норма составляет {metric.norm_value:.4f}. "
            f"Твой итоговый балл по этому параметру — {metric.score:.1f}/10.\n\n"
            "Это важный параметр лицевой симметрии и пропорций, который играет значимую роль в формировании общего восприятия.\n\n"
            "**ВЛИЯНИЕ:** Гармоничные значения этого показателя помогают создать сбалансированный, эстетичный образ."
        )

def generate_overall_summary(result: FullAnalysisResult, lang: str = "ru") -> str:
    """
    Generates the "ОБЩЕЕ ВПЕЧАТЛЕНИЕ" block (first page summary).
    """
    top_strengths = ", ".join(result.top_strengths)
    top_weaknesses = ", ".join(result.top_weaknesses)

    if (lang or "").startswith("en"):
        user_prompt = (
            f"Gender: {result.gender}\n"
            f"Overall score: {result.overall_score:.1f} out of 10\n"
            f"Strengths: {top_strengths}\n"
            f"Growth areas: {top_weaknesses}\n"
        )
    else:
        user_prompt = (
            f"Пол: {result.gender}\n"
            f"Общий балл: {result.overall_score:.1f} из 10\n"
            f"Сильные стороны: {top_strengths}\n"
            f"Зоны для улучшения: {top_weaknesses}\n"
        )

    messages = [
        {"role": "system", "content": _sys(SUMMARY_PROMPT, lang)},
        {"role": "user", "content": user_prompt}
    ]
    
    try:
        return _call_openai_with_retry(messages)
    except Exception:
        if (lang or "").startswith("en"):
            return (
                f"Your overall score is {result.overall_score:.1f} out of 10. "
                f"Your standout strengths: {top_strengths}. "
                f"The main areas for visual improvement: {top_weaknesses}. "
                "Overall, your face has a unique set of features that can be worked on constructively."
            )
        return (
            f"Твой общий балл составляет {result.overall_score:.1f} из 10. "
            f"Среди сильных сторон ярко выделяются: {top_strengths}. "
            f"Основными зонами для визуального улучшения являются: {top_weaknesses}. "
            "В целом, твое лицо обладает уникальным набором черт, над которыми можно конструктивно работать."
        )

def generate_improvement_advice(result: FullAnalysisResult, lang: str = "ru") -> list[dict]:
    """
    Generates improvement advice for bottom 5 metrics.
    """
    # Find the bottom 5 metrics
    sorted_metrics = sorted(result.metrics, key=lambda m: m.score)
    bottom_5 = sorted_metrics[:5]
    
    is_en = (lang or "").startswith("en")
    metrics_info = []
    for m in bottom_5:
        label = m.name_en if is_en and m.name_en else m.name_ru
        metrics_info.append(f"- {label} ({'Score' if is_en else 'Балл'}: {m.score:.1f})")

    if is_en:
        user_prompt = (
            "Generate advice for the following 5 lowest-scoring metrics. "
            "Write metric_name_ru with the ENGLISH metric name and use English category names:\n"
            + "\n".join(metrics_info)
        )
    else:
        user_prompt = "Сгенерируй советы для следующих 5 метрик с наименьшими баллами:\n" + "\n".join(metrics_info)

    messages = [
        {"role": "system", "content": _sys(ADVICE_PROMPT, lang)},
        {"role": "user", "content": user_prompt}
    ]
    
    try:
        # Since ADVICE_PROMPT requests JSON output, we can attempt to parse it.
        # JSON for 5 metrics does not fit into the default 400-token budget —
        # a truncated response breaks json.loads ("Unterminated string").
        response_text = _call_openai_with_retry(messages, max_tokens=1200)
        # Strip potential markdown code blocks
        if response_text.startswith("```json"):
            response_text = response_text[7:-3].strip()
        elif response_text.startswith("```"):
            response_text = response_text[3:-3].strip()
            
        return json.loads(response_text)
    except Exception as e:
        logging.error(f"Failed to generate or parse advice JSON: {e}")
        # Fallback advice
        fallback_advice = []
        for m in bottom_5:
            if is_en:
                fallback_advice.append({
                    "metric_name_ru": m.name_en or m.name_ru,
                    "category": "General advice",
                    "advice_text": "Experiment with camera angles and lighting to find the most flattering presentation for this facial feature."
                })
            else:
                fallback_advice.append({
                    "metric_name_ru": m.name_ru,
                    "category": "Общие рекомендации",
                    "advice_text": "Попробуй поэкспериментировать с ракурсами и освещением, чтобы найти наиболее выгодный угол для этой черты лица."
                })
        return fallback_advice

def generate_all_texts(result: FullAnalysisResult, lang: str = "ru") -> dict:
    """
    Orchestrator — calls all generation functions in parallel.
    """
    metric_texts = {}
    advice = []
    overall_summary = ""
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        # Submit summary job
        future_summary = executor.submit(generate_overall_summary, result, lang)
        
        # Submit advice job
        future_advice = executor.submit(generate_improvement_advice, result, lang)
        
        # Submit metric jobs
        future_to_metric = {
            executor.submit(generate_metric_text, metric, result.gender, lang): metric.name 
            for metric in result.metrics
        }
        
        for future in as_completed(future_to_metric):
            metric_name = future_to_metric[future]
            try:
                metric_texts[metric_name] = future.result()
            except Exception as e:
                logging.error(f"Error gathering result for {metric_name}: {e}")
                metric_texts[metric_name] = "Text generation error." if (lang or "").startswith("en") else "Ошибка генерации текста."
                
        overall_summary = future_summary.result()
        advice = future_advice.result()
        
    return {
        "overall_summary": overall_summary,
        "metric_texts": metric_texts,
        "advice": advice
    }
