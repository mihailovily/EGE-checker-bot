#!/bin/bash

echo Впиши токен telegram бота

read vartoken

echo $vartoken > settings/token.txt

echo Токен записан

echo Впиши ID админа

read varadmin

echo $varadmin > settings/admin.txt

echo ID админа записан

echo Установка зависимостей

pip install -r requirements.txt

echo Зависимости установлены

echo Формирование базы

bash encoder.sh

echo К запуску готов