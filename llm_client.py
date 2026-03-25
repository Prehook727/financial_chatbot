# llm_client.py
import os
import requests
import logging
from dotenv import load_dotenv


# ===================== basic_config ====================
load_dotenv()
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("llm_client")

# 从环境变量读取核心配置（与之前的.env文件对应）
LLM_API_KEY = os.getenv("LLM_API_KEY")
LLM_API_URL = os.getenv("LLM_API_URL")
HKBUAPI_URL = os.getenv("API_KEY")
HKBU_URL = os.getenv("BASE_URL")
HKBU_MODEL = os.getenv("MODEL")
HKBU_API_VER = os.getenv("API_VER")
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "30"))
if not LLM_API_KEY or not LLM_API_URL:
    logger.info("LLM API config lost")



# ===================== 核心调用函数（适配不同LLM API） =====================
def call_llm_api(
    prompt: str,
    temperature: float = 0.1,  
    max_tokens: int = 500,     
    model: str = "chatgpt_hkbu"     
) -> str:
    """
    Call LLM API to get response text
    :param prompt: Enter prompt word (core command of financial agent)
    :param temperature: generation temperature, the lower the more accurate (0-1)
    :param max_tokens: maximum number of generated tokens
    :param model: model version to use
    :return: The plain text response returned by LLM (returns a friendly prompt on failure)
    """
    logger.info(f"Model parameters when calling API: '{model}' (type: {type(model)}, length: {len(model)})")
    
    
    # 根据模型类型选择API配置
    if model.strip() == "chatgpt_hkbu":  # 使用strip()去除可能的空白字符
        # ===== 适配【HKBU校内LLM API】 =====
        logger.info("使用HKBU API进行请求")
        headers = {
            "accept": "application/json",
            "Content-Type": "application/json",
            "api-key": HKBUAPI_URL  # HKBU API使用api-key头部
        }
        # HKBU API的URL格式不同
        api_url = f"{HKBU_URL}/deployments/{HKBU_MODEL}/chat/completions?api-version={HKBU_API_VER}"
        payload = {
            "messages": [
                {
                    "role": "system", 
                    "content": "You are a helper! Your users are university students. Your replies should be conversational, informative, use simple words, and be straightforward."
                },
                {
                    "role": "user",
                    "content": prompt  # 用户提示词
                }
            ],
            "temperature": 1,     # HKBU API固定参数
            "max_tokens": 150,    # HKBU API固定参数
            "top_p": 1,           # HKBU API固定参数
            "stream": False       # HKBU API固定参数
        }
    else:
        # ===== 适配其他API（如豆包等）=====
        logger.info(f"使用第三方API进行请求，模型: {model}")
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {LLM_API_KEY}"  # 通用鉴权格式，部分API需调整（如直接传key）
        }

        payload = {
            "model": model,  # 使用传入的模型名
            "messages": [
                {
                    "role": "user",
                    "content": prompt  # 用户提示词
                }
            ],
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        api_url = LLM_API_URL

    # 3. 发送请求并处理响应（核心逻辑，无需修改）
    try:
        logger.info(f"调用LLM API，请求参数：prompt={prompt[:50]}...")  # 日志仅输出前50字符，避免过长
        # 发送POST请求，设置超时（避免卡死）
        response = requests.post(
            url=api_url,
            headers=headers,
            json=payload,
            timeout=REQUEST_TIMEOUT  # 使用可配置的超时时间
        )
        # 校验响应状态码（200=成功）
        response.raise_for_status()
        # 解析JSON响应
        response_data = response.json()
        logger.info(f"LLM API响应成功，状态码：{response.status_code}")

        # 4. 提取响应文本（根据不同API调整）
        if model.strip() == "chatgpt_hkbu":
            # ===== 适配HKBU校内API的响应格式 =====
            if "choices" in response_data and len(response_data["choices"]) > 0:
                llm_response = response_data["choices"][0]["message"]["content"].strip()
            elif "response" in response_data:
                llm_response = response_data["response"].strip()
            elif "text" in response_data:
                llm_response = response_data["text"].strip()
            else:
                # 兜底：若响应格式未知，返回原始文本（便于调试）
                llm_response = str(response_data)
                logger.warning(f"HKBU API响应格式未适配，原始响应：{llm_response[:200]}...")
        else:
            # ===== 适配其他API的响应格式 =====
            if "choices" in response_data:
                # 其他API响应示例：{"choices": [{"message": {"content": "回答内容"}}]}
                llm_response = response_data["choices"][0]["message"]["content"].strip()
            else:
                # 兜底：若响应格式未知，返回原始文本（便于调试）
                llm_response = str(response_data)
                logger.warning(f"第三方API响应格式未适配，原始响应：{llm_response[:200]}...")

        return llm_response

    # 5. 异常处理（覆盖所有常见错误，避免机器人崩溃）
    except requests.exceptions.Timeout:
        logger.error(f"LLM API调用超时（超过{REQUEST_TIMEOUT}秒）")
        return "抱歉，金融智能体请求超时，请稍后再试～"
    except requests.exceptions.ConnectionError as e:
        logger.error(f"LLM API连接失败（网络问题/URL错误）: {str(e)}")
        if model.strip() == "chatgpt_hkbu":
            return "抱歉，HKBU API连接失败，请检查网络或联系管理员～"
        else:
            return "抱歉，金融智能体网络连接失败，请检查网络或稍后再试～"
    except requests.exceptions.HTTPError as e:
        # 捕获HTTP错误（如401=密钥错误，404=URL错误）
        logger.error(f"LLM API HTTP错误：{e}，响应内容：{response.text if 'response' in locals() else '无'}")
        if "401" in str(e):
            return "抱歉，金融智能体API密钥无效，请联系管理员～"
        elif "404" in str(e):
            return "抱歉，金融智能体API地址错误，请联系管理员～"
        else:
            return f"抱歉，金融智能体请求失败（错误码：{e.response.status_code}），请稍后再试～"
    except Exception as e:
        # 兜底异常（捕获所有未预期错误）
        logger.error(f"LLM API调用未知错误：{str(e)}", exc_info=True)
        return "抱歉，金融智能体运行出错，请稍后再试～"




if __name__ == "__main__":
    test_prompt = "As a financial AI agent, analyze the current A-share market risk level (high/medium/low) and give 3 simple reasons"
    result = call_llm_api(prompt=test_prompt)
    print("="*50)
    print("LLM API test response:")
    print(result)
    print("="*50)