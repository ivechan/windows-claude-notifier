#!/bin/bash

TITLE=${1:-"测试通知"}
BODY=${2:-"这是从 bash 脚本发送的测试消息"}

echo "Sending curl POST request to http://192.168.3.18:5000/notify ..."
echo "Title: $TITLE"
echo "Body: $BODY"
echo ""

curl -X POST http://192.168.3.18:5000/notify -H "Content-Type: application/json" -d "{\"title\":\"$TITLE\",\"body\":\"$BODY\",\"sound\":\"default\"}"

echo ""
