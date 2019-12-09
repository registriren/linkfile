#!/usr/bin/python
# -*- coding: utf-8 -*-


from botapitamtam import BotHandler
import json
import shutil
import youtube_dl
import os
import logging

config = 'config.json'
with open(config, 'r', encoding='utf-8') as c:
    conf = json.load(c)
    token = conf['access_token']

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

bot = BotHandler(token)


def main():
    marker = None
    # chat_id = bot.get_chat_id() # Получаем chat_id последнего активного диалога с ботом
    # bot.send_message("Отправьте боту ссылку для скачивания", chat_id)
    # video = ['mp4', 'avi', 'mkv', 'wmv', 'mov', 'm4v', 'h264', 'mpg', 'vob', 'flv']
    # image = ['jpg', 'png', 'bmp', 'jpeg', 'tiff', 'psd', 'gif']
    try:
        shutil.rmtree(os.getcwd() + '/video')
    except:
        logger.error('Каталог для удаления не найден')
    while True:
        update = bot.get_updates(
            marker)  # получаем внутреннее представление сообщения (контента) отправленного боту (сформированного ботом)
        # тут можно вставить любые действия которые должны выполняться во время ожидания события
        if update == None:  # проверка на пустое событие, если пусто - возврат к началу цикла
            continue
        marker = bot.get_marker(update)
        updates = update['updates']
        for last_update in list(updates):  # формируем цикл на случай если updates вернул список из нескольких событий
            text = bot.get_text(last_update)
            chat_id = bot.get_chat_id(last_update)
            try:
                upd = bot.send_message('Обрабатываю контент...', chat_id)
                mid = bot.get_message_id(upd)
                ydl_opts = {
                    'format': 'best',
                    'outtmpl': 'video.%(ext)s',
                    'logger': logging.getLogger(__name__)
                }
                with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                    # dat = ydl.download([text])
                    dat = ydl.extract_info(text, download=True)
                    # url_vid = dat['url']
                # protocol = dat['protocol']
                # format = dat['format']
                title = dat['title']
                ext = dat['ext']
                # bot.send_message('format - {}\nProtocol - {}\nTitle - {}\nExt - {}'.format(format, protocol, title,
                # ext), chat_id, dislinkprev=True)
                bot.delete_message(mid)
                upd = bot.send_message('Загружаю видео...', chat_id)
                mid = bot.get_message_id(upd)
                bot.send_video(os.getcwd() + '/video/video.{}'.format(ext), chat_id, text=title)
                bot.delete_message(mid)
                try:
                    shutil.rmtree(os.getcwd() + '/video')
                except:
                    logger.error('Каталог для удаления не найден')
                logger.info('{} download {}'.format(chat_id, text))

            except Exception as e:
                bot.delete_message(mid)
                bot.send_message('Ошибка скачивания, возможно ссылка с данного сервиса не поддерживается', chat_id)
                logger.error('{}'.format(e))


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        exit()
