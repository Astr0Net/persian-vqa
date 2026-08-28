# Persian VQA

## اجرای مدل Qwen در Google Colab

در Colab یک GPU Runtime انتخاب کنید و فایل
`ai/qwen_colab_gateway.ipynb` را آپلود و باز کنید. سلول‌ها را به‌ترتیب اجرا
کنید. در سلول دوم مقدار توکن ngrok را وارد کنید:

```python
import os
os.environ["NGROK_AUTHTOKEN"] = "توکن ngrok شما"
```

مدل پیش‌فرض `Qwen/Qwen2.5-1.5B-Instruct` است. پس از بالا آمدن سرویس، آدرس
`Public AI_SERVICE_URL` در خروجی Colab را کپی کنید. Runtime Colab باید تا پایان
کار روشن بماند.

## اجرای بک‌اند

```powershell
cd backend
python -m pip install -r requirements.txt
$env:AI_SERVICE_URL = "https://آدرس-ngrok-کپی‌شده"
uvicorn app:app --reload --port 8080
```

تست سؤال ثابت:

```powershell
Invoke-RestMethod http://127.0.0.1:8080/ask-fixed
```

برای سؤال دلخواه نیز می‌توان از `POST /ask` استفاده کرد:

```powershell
Invoke-RestMethod http://127.0.0.1:8080/ask `
  -Method Post -ContentType "application/json" `
  -Body '{"question":"پایتخت ایران کجاست؟"}'
```
