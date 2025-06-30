#!/bin/sh

python 3-tts.py --output 3.wav --format wav 'Hello world! My name is Alloy!'
python 3-tts.py --output 3.flac --format flac 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.'
python 3-tts.py --output 3-cn.opus --format opus '这是一个示例文本，用于占位。它的目的是填充空间，展示中文排版的视觉效果，而不传达具体含义'
python 3-tts.py --output 3-ru.opus --format opus 'Это пример текста, используемого в качестве заполнителя. Его цель — заполнить пространство и продемонстрировать визуальный эффект русской типографики без передачи конкретного смысла.'


