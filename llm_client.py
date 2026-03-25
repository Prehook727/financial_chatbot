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

# Read core configuration from environment variables (corresponding to the previous .env file)
LLM_API_KEY = os.getenv("LLM_API_KEY")
LLM_API_URL = os.getenv("LLM_API_URL")
HKBUAPI_URL = os.getenv("API_KEY")
HKBU_URL = os.getenv("BASE_URL")
HKBU_MODEL = os.getenv("MODEL")
HKBU_API_VER = os.getenv("API_VER")
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "30"))
if not LLM_API_KEY or not LLM_API_URL:
    logger.info("LLM API config lost")



# ===================== Core calling function (adapted to different LLM APIs) =====================
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
    
    if model.strip() == "chatgpt_hkbu":  
        logger.info("使用HKBU API进行请求")
        headers = {
            "accept": "application/json",
            "Content-Type": "application/json",
            "api-key": HKBUAPI_URL  
        }
        api_url = f"{HKBU_URL}/deployments/{HKBU_MODEL}/chat/completions?api-version={HKBU_API_VER}"
        payload = {
            "messages": [
                {
                    "role": "system", 
                    "content": "You are a professional financial AI. Only reply in English, concise and clear."
                },
                {
                    "role": "user",
                    "content": prompt  
                }
            ],
            "temperature": 1,     
            "max_tokens": 150,    
            "top_p": 1,           
            "stream": False       
        }
    else:
        # ===== Adapt to other APIs (such as Doubao, etc.)=====
        logger.info(f"Use: {model}")
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {LLM_API_KEY}"  
        }

        payload = {
            "model": model,  
            "messages": [
                {
                    "role": "user",
                    "content": prompt  
                }
            ],
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        api_url = LLM_API_URL

    try:
        logger.info(f"调用LLM API，请求参数：prompt={prompt[:50]}...")  
        response = requests.post(
            url=api_url,
            headers=headers,
            json=payload,
            timeout=REQUEST_TIMEOUT  
        )
        
        response.raise_for_status()

        response_data = response.json()
        logger.info(f"LLM API响应成功，状态码：{response.status_code}")

        
        if model.strip() == "chatgpt_hkbu":
            if "choices" in response_data and len(response_data["choices"]) > 0:
                llm_response = response_data["choices"][0]["message"]["content"].strip()
            elif "response" in response_data:
                llm_response = response_data["response"].strip()
            elif "text" in response_data:
                llm_response = response_data["text"].strip()
            else:
                llm_response = str(response_data)
                logger.warning(f"response do not contain expected fields, original response:{llm_response[:200]}...")
        else:
            if "choices" in response_data:
                llm_response = response_data["choices"][0]["message"]["content"].strip()
            else:
                llm_response = str(response_data)
                logger.warning(f"response do not contain expected fields, original response:{llm_response[:200]}...")

        return llm_response

    # 5. Exception handling (covers all common errors to avoid robot crashes)
    except requests.exceptions.Timeout:
        logger.error(f"LLM API call timeout (more than {REQUEST_TIMEOUT} seconds)")
        return "Sorry, the financial agent request timed out, please try again later~"
    except requests.exceptions.ConnectionError as e:
        logger.error(f"LLM API connection failed (network problem/URL error): {str(e)}")
        if model.strip() == "chatgpt_hkbu":
            return "Sorry, HKBU API connection failed, please check the network or contact the administrator~"
        else:
            return "Sorry, the financial agent network connection failed, please check the network or try again later~"
    except requests.exceptions.HTTPError as e:
        # Capture HTTP errors (such as 401=wrong key, 404=wrong URL)
        logger.error(f"LLM API HTTP error: {e}, response content: {response.text if 'response' in locals() else 'none'}")
        if "401" in str(e):
            return "Sorry, the financial intelligence API key is invalid, please contact the administrator~"
        elif "404" in str(e):
            return "Sorry, the API address of the financial intelligence agent is wrong, please contact the administrator~"
        else:
            return f"Sorry, the financial agent request failed (error code: {e.response.status_code}), please try again later~"
    except Exception as e:
        # Catch exceptions (catch all unexpected errors)
        logger.error(f"Unknown error in LLM API call: {str(e)}", exc_info=True)
        return "Sorry, there was an error in the operation of the financial intelligence agent, please try again later~"




if __name__ == "__main__":
    test_prompt = "As a financial AI agent, analyze the current A-share market risk level (high/medium/low) and give 3 simple reasons"
    result = call_llm_api(prompt=test_prompt)
    print("="*50)
    print("LLM API test response:")
    print(result)
    print("="*50)