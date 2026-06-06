# 🗣️ AI英语口语陪练（七牛云实训营最终版）

> 语音 + 文字 · 场景对话 · 实时纠错 · 三维评分 · 学习趋势 · 错误排行榜 · 学习报告

---

## ✅ 实训营要求完成情况

| 要求 | 实现 |
|------|------|
| 场景选择（点餐/面试/会议/旅游） | ✅ |
| 实时语音对话 | ✅（Whisper语音输入） |
| 文字对话 | ✅ |
| 语法/表达纠错 | ✅ |
| 课后总结 | ✅ |
| 可量化反馈 | ✅ |
| 练习统计（时长/词数） | ✅ |
| 评分趋势图 | ✅ |
| 错误排行榜 | ✅ |

---

## 🚀 快速运行
、、、bash
git clone https://github.com/WWZhhhhh888/qiniu-ai-english-tutor.git
cd qiniu-ai-english-tutor
pip install -r requirements.txt
echo "DEEPSEEK_API_KEY=你的密钥" > .env
streamlit run app.py

> 首次语音识别会加载模型（约10秒），之后无需等待
、、、
---

## 🧪 测试示例

> **用户**：I want to order a pizza.  
> **AI**：Sure, what kind of pizza would you like?

> **用户**：I go to park yesterday.（故意错误）  
> **AI 纠错**：go → went（Tense 错误）

---

## 📊 核心功能

- 场景对话（点餐 / 面试 / 会议 / 旅游）
- 语音输入（Whisper）+ 文字输入
- 语法 / 流利度 / 词汇 三维评分
- 练习统计（时长 / 总词数）
- 评分趋势折线图
- 错误类型排行榜
- 学习报告自动生成

---

## 🛠️ 技术栈

- Streamlit
- DeepSeek API
- Faster‑Whisper
- sounddevice + scipy
- pandas + numpy

---

## 👤 作者

王子涵  
上海电力大学 自动化  
[GitHub](https://github.com/WWZhhhhh888)

---

## 📎 实训营提交

- 仓库：https://github.com/WWZhhhhh888/qiniu-ai-english-tutor
- 视频：
