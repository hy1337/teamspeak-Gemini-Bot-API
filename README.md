# TeamSpeak & Gemini API Chat Bot

## 介绍 (Introduction)

本项目是一个集成了TeamSpeak 3和Google Gemini API的聊天机器人。该机器人能够在TeamSpeak频道中监听并响应用户消息，并使用Google Gemini API生成回复。读取历史记录采用Unicode编码，用户可以自行编辑或删除。

This project is a chat bot that integrates TeamSpeak 3 and Google Gemini API. The bot can listen to and respond to user messages in a TeamSpeak channel, using the Google Gemini API to generate responses. Chat history is read with Unicode encoding, allowing users to edit or delete it as needed.

## 特性 (Features)

- 连接到TeamSpeak服务器并监听频道消息
- 使用Google Gemini API生成回复
- 读取和写入聊天历史记录，支持Unicode编码
- 支持重置BOT功能，需输入密码

- Connect to a TeamSpeak server and listen to channel messages
- Generate responses using the Google Gemini API
- Read and write chat history with Unicode encoding
- Support BOT reset function with password input

## 安装 (Installation)

安装此存储库 (Clone this repository):
pip install ts3
pip install google-generativeai
