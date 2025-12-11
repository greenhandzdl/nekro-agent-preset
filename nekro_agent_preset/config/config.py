import os
from dotenv import load_dotenv

class Config:
    def __init__(self, env_path: str = None):
        if env_path:
            load_dotenv(dotenv_path=env_path)
        else:
            load_dotenv()
        
        self.Author = os.getenv("Author")
        self.NekroInstanceID = os.getenv("NekroInstanceID")
        self.NekroAPIKey = os.getenv("NekroAPIKey")
        self.NEKRO_API_URL = os.getenv("NEKRO_API_URL", "https://community.nekro.ai/api")
        # 可以根据需要添加更多的环境变量
        
# 创建一个全局配置实例
config = Config("../.env")
