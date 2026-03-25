from supabase import create_client, Client
from dotenv import load_dotenv
import os

load_dotenv()
supabase: Client = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

# write bot logs  
def write_bot_log(user_id: int, user_message: str, bot_response: str, llm_model: str):
    try:
        supabase.table("bot_logs").insert({
            "user_id": user_id,
            "user_message": user_message,
            "bot_response": bot_response,
            "llm_model": llm_model
        }).execute()
        return True
    except Exception as e:
        print(f"日志写入失败：{e}")
        return False

# 读取日志（可选，用于调试）
def get_bot_logs(user_id: int):
    return supabase.table("bot_logs").select("*").eq("user_id", user_id).execute()