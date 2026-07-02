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

def generate_metric_text(metric: MetricResult, gender: str) -> str:
    """
    Generates 3-paragraph personalized analysis for a single metric.
    """
    system_prompt = METRIC_PROMPTS.get(metric.name, DEFAULT_METRIC_PROMPT)
    
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
        return (
            f"Анализ метрики '{metric.name_ru}' не удалось сгенерировать из-за ошибки сети. "
            f"Твой показатель равен {metric.raw_value:.4f}, тогда как средняя норма составляет {metric.norm_value:.4f}. "
            f"Твой итоговый балл по этому параметру — {metric.score:.1f}/10.\n\n"
            "Это важный параметр лицевой симметрии и пропорций, который играет значимую роль в формировании общего восприятия.\n\n"
            "**ВЛИЯНИЕ:** Гармоничные значения этого показателя помогают создать сбалансированный, эстетичный образ."
        )

def generate_overall_summary(result: FullAnalysisResult) -> str:
    """
    Generates the "ОБЩЕЕ ВПЕЧАТЛЕНИЕ" block (first page summary).
    """
    top_strengths = ", ".join(result.top_strengths)
    top_weaknesses = ", ".join(result.top_weaknesses)
    
    user_prompt = (
        f"Пол: {result.gender}\n"
        f"Общий балл: {result.overall_score:.1f} из 10\n"
        f"Сильные стороны: {top_strengths}\n"
        f"Зоны для улучшения: {top_weaknesses}\n"
    )
    
    messages = [
        {"role": "system", "content": SUMMARY_PROMPT},
        {"role": "user", "content": user_prompt}
    ]
    
    try:
        return _call_openai_with_retry(messages)
    except Exception:
        return (
            f"Твой общий балл составляет {result.overall_score:.1f} из 10. "
            f"Среди сильных сторон ярко выделяются: {top_strengths}. "
            f"Основными зонами для визуального улучшения являются: {top_weaknesses}. "
            "В целом, твое лицо обладает уникальным набором черт, над которыми можно конструктивно работать."
        )

def generate_improvement_advice(result: FullAnalysisResult) -> list[dict]:
    """
    Generates improvement advice for bottom 5 metrics.
    """
    # Find the bottom 5 metrics
    sorted_metrics = sorted(result.metrics, key=lambda m: m.score)
    bottom_5 = sorted_metrics[:5]
    
    metrics_info = []
    for m in bottom_5:
        metrics_info.append(f"- {m.name_ru} (Балл: {m.score:.1f})")
    
    user_prompt = "Сгенерируй советы для следующих 5 метрик с наименьшими баллами:\n" + "\n".join(metrics_info)
    
    messages = [
        {"role": "system", "content": ADVICE_PROMPT},
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
            fallback_advice.append({
                "metric_name_ru": m.name_ru,
                "category": "Общие рекомендации",
                "advice_text": "Попробуй поэкспериментировать с ракурсами и освещением, чтобы найти наиболее выгодный угол для этой черты лица."
            })
        return fallback_advice

def generate_all_texts(result: FullAnalysisResult) -> dict:
    """
    Orchestrator — calls all generation functions in parallel.
    """
    metric_texts = {}
    advice = []
    overall_summary = ""
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        # Submit summary job
        future_summary = executor.submit(generate_overall_summary, result)
        
        # Submit advice job
        future_advice = executor.submit(generate_improvement_advice, result)
        
        # Submit metric jobs
        future_to_metric = {
            executor.submit(generate_metric_text, metric, result.gender): metric.name 
            for metric in result.metrics
        }
        
        for future in as_completed(future_to_metric):
            metric_name = future_to_metric[future]
            try:
                metric_texts[metric_name] = future.result()
            except Exception as e:
                logging.error(f"Error gathering result for {metric_name}: {e}")
                metric_texts[metric_name] = "Ошибка генерации текста."
                
        overall_summary = future_summary.result()
        advice = future_advice.result()
        
    return {
        "overall_summary": overall_summary,
        "metric_texts": metric_texts,
        "advice": advice
    }
