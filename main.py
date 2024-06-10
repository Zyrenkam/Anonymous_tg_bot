import telebot
from telebot import types
import tokens

token = tokens.token
bot = telebot.TeleBot(token)

moder_chat_id = tokens.moder_chat_id
group_chat_id = tokens.group_chat_id
channel = tokens.channel_name

check_all = ''

key = ''


def correct_msg(msg):
    # Функция для приведения символов к требуемой форме Markdown
    symbols = ['.', '(', ')', '!', '-', '@', '#', '$', '%', '^', '*', '_', '+', ';', ':', '=', '&']

    for sym in symbols:
        msg = msg.replace(sym, f'\{sym}')
    return msg


@bot.message_handler(commands=['start'])
def start_message(message):
    global key
    key = telebot.util.extract_arguments(message.text)

    if key:
        bot.send_message(message.chat.id, 'Напишите комментарий')

    markup_inline = types.InlineKeyboardMarkup()
    item_media = types.InlineKeyboardButton(text='Отправить медиафайл', callback_data='send_media')
    markup_inline.add(item_media)

    bot.send_message(message.chat.id, 'Напишите своё сообщение и отправьте его нам.'
        '\nПосле проверки администратором ваше сообщение будет анонимно опубликовано на канале.'
        '\nЕсли у вас есть один медиафайл, вы можете прикрепить его прямо здесь.'
        '\n Для отправки комментариев укажите перед текстом номер поста, например, №20 привет!'
        '\n\nЕсли же оно не было опубликовано, значит, не прошло модерацию. Пишите админу - @',
                     reply_markup=markup_inline)


@bot.callback_query_handler(func=lambda call: True)
def answer(call):
    if call.data == 'send_media':
        bot.send_message(call.message.chat.id, 'Прикрепите вместе с фотографией желаемый текст')


@bot.message_handler(func=lambda message: True)
def msg(message):
    global check_all, key

    # Сообщение от пользователя в лс боту
    if message.chat.id != moder_chat_id and message.chat.id != group_chat_id:
        # Если сообщение - комментарий
        if '№' in message.text and message.text[0] == '№':
            # Поиск в группе по слову
            find_code, comment = int(message.text.split()[0][1::]), ' '.join(message.text.split()[1::])

            bot.send_message(group_chat_id, comment, reply_to_message_id=find_code)

        # Если пользователь перешел по номеру коммента
        elif len(key) != 0 and '№' not in message.text:
            bot.send_message(group_chat_id,  message.text, reply_to_message_id=int(key))
            key = ''

        else:
            bot.send_message(message.chat.id, 'Ваше сообщение ушло на проверку админу, ожидайте')

            check_all = message

            bot.forward_message(moder_chat_id, message.chat.id, message.message_id)

    # Группа с модером
    elif message.chat.id == moder_chat_id:

        # Одобрение текста
        if message.text == 'да':
            try:
                msg_to_public = message.reply_to_message.text
                chan_id = bot.send_message(channel, msg_to_public).id
                gr_id = bot.send_message(group_chat_id, msg_to_public).id

                msg_to_public = correct_msg(msg_to_public)

                key = str(gr_id+1)

                bot.edit_message_text(msg_to_public + '\nНомер для анонимного комментирования: ||[№' + str(gr_id+1) +
                                      f']({tokens.link_to_bot}{key})||', channel, chan_id, parse_mode='MarkdownV2')
                bot.delete_message(group_chat_id, gr_id)
                bot.reply_to(check_all, 'Текст для поста одобрен')
            except:
                bot.send_message(moder_chat_id, 'Отсутствует вложенное сообщение')

        # Одобрение ФОТО
        elif message.text == 'фда':
            try:
                publ = message.reply_to_message.caption.split('|')[0]
                if publ is None:
                    publ = ' '

                chan_id = bot.send_photo(channel, photo=open('photo.jpg', 'rb'), caption=str(publ)).id
                gr_id = bot.send_photo(group_chat_id, photo=open('photo.jpg', 'rb'), caption=str(publ)).id

                publ = correct_msg(publ)

                key = str(gr_id + 1)

                bot.edit_message_caption(publ + '\nНомер для анонимного комментирования: ||[№' + str(gr_id+1) +
                                      f']({tokens.link_to_bot}{key})||', channel, chan_id, parse_mode='MarkdownV2')

                bot.delete_message(group_chat_id, gr_id)

                bot.send_message(int(message.reply_to_message.caption.split('|')[1]), 'Пост с фотографией одобрен')
            except:
                bot.send_message(message.chat.id, 'Отсутствует вложение')
        elif message.text == 'вда':
            try:
                publ = message.reply_to_message.caption.split('|')[0]

                if publ is None:
                    publ = ' '

                chan_id = bot.copy_message(chat_id=channel, from_chat_id=moder_chat_id,
                                 message_id=message.reply_to_message.message_id,
                                 caption=str(publ)).message_id

                gr_id = bot.copy_message(chat_id=group_chat_id, from_chat_id=moder_chat_id,
                                 message_id=message.reply_to_message.message_id,
                                 caption=str(publ)).message_id

                publ = correct_msg(publ)

                key = str(gr_id + 1)

                bot.edit_message_caption(publ + '\nНомер для анонимного комментирования: ||[№' + str(gr_id+1) +
                                      f']({tokens.link_to_bot}{key})||', channel, chan_id, parse_mode='MarkdownV2')

                bot.delete_message(group_chat_id, gr_id)

                bot.send_message(int(message.reply_to_message.caption.split('|')[1]), 'Пост с видео одобрен')
            except:
                bot.send_message(message.chat.id, 'Отсутствует вложение')

        # Отклонение ТЕКСТ
        elif message.text == 'нет':
            try:
                bot.reply_to(check_all, 'Не одобрено')
            except:
                bot.send_message(moder_chat_id, 'Отсутствует вложенное сообщение')

        # Отклонение ФОТО и ВИДЕО
        elif message.text == 'мнет':
            try:
                bot.send_message(int(message.reply_to_message.caption.split('|')[1]), 'Пост не одобрен')
            except:
                bot.send_message(moder_chat_id, 'Отсутствует вложенное сообщение')


@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    global key
    text = message.caption
    if text is None:
        text = ' '

    photo = message.photo[-1]
    file_info = bot.get_file(photo.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    save_path = tokens.save_photo

    with open(save_path, 'wb') as new_file:
        new_file.write(downloaded_file)

    # Сообщение от пользователя в лс боту
    if message.chat.id != moder_chat_id and message.chat.id != group_chat_id:
        if '№' in text and text[0] == '№':
            # Поиск в группе по слову
            find_code, comment = int(message.caption.split()[0][1::]), ' '.join(message.caption.split()[1::])

            bot.send_photo(group_chat_id, photo=open(save_path, 'rb'), caption=comment, reply_to_message_id=find_code)

        elif len(key) != 0 and '№' not in text:
            bot.copy_message(group_chat_id, message.chat.id, message_id=message.message_id,
                             reply_to_message_id=int(key))
            key = ''

        else:
            bot.reply_to(message, 'Фотография отправлена на проверку, ожидайте')
            bot.copy_message(chat_id=moder_chat_id, from_chat_id=message.chat.id, message_id=message.message_id,
                             caption=(text + '|' + str(message.chat.id)))


@bot.message_handler(content_types=['video'])
def get_file(message):
    global key
    text = message.caption
    if text is None:
        text = ' '

    # Сообщение от пользователя в лс боту
    if message.chat.id != moder_chat_id and message.chat.id != group_chat_id:
        if '№' in text and text[0] == '№':
            # Поиск в группе по слову
            find_code, comment = int(message.caption.split()[0][1::]), ' '.join(message.caption.split()[1::])

            bot.copy_message(group_chat_id, message.chat.id, message_id=message.message_id,
                             reply_to_message_id=int(find_code))

        elif len(key) != 0 and '№' not in text:
            bot.copy_message(group_chat_id, message.chat.id, message_id=message.message_id,
                             reply_to_message_id=int(key))
            key = ''

        else:
            bot.send_message(message.chat.id, 'Видео отправлено на проверку, ожидайте')

            bot.copy_message(chat_id=moder_chat_id, from_chat_id=message.chat.id, message_id=message.message_id,
                             caption=(text + '|' + str(message.chat.id)))


bot.polling(non_stop=True)
