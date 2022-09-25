import telebot
import config
import urllib
import re
import os
from PIL import Image
import requests


 
bot = telebot.TeleBot(config.TOKEN)

def get_size_format(b, factor=1024, suffix="B"):
    for unit in ["", "K", "M", "G", "T", "P", "E", "Z"]:
        if b < factor:
            return f"{b:.2f}{unit}{suffix}"
        b /= factor
    return f"{b:.2f}Y{suffix}"

def compress_img(image_name,  message='', new_size_ratio=0.9, quality=90, width=None, height=None, to_jpg=True):
    # load the image to memory
    img = Image.open(image_name)
    # print the original image shape
    bot.send_message(message.chat.id, f'[*] Image shape: {img.size}')
    # get the original image size in bytes
    image_size = os.path.getsize(image_name)
    # print the size before compression/resizing
    bot.send_message(message.chat.id, f"[*] Size before compression:  {get_size_format(image_size)}")
    if new_size_ratio < 1.0:
        # if resizing ratio is below 1.0, then multiply width & height with this ratio to reduce image size
        img = img.resize((int(img.size[0] * new_size_ratio), int(img.size[1] * new_size_ratio)), Image.ANTIALIAS)
        # print new image shape
        bot.send_message(message.chat.id, f"[+] New Image shape:  {img.size}")
    elif width and height:
        # if width and height are set, resize with them instead
        img = img.resize((width, height), Image.ANTIALIAS)
        # print new image shape
        bot.send_message(message.chat.id, f"[+] New Image shape:  {img.size}")
    # split the filename and extension
    filename, ext = os.path.splitext(image_name)
    # make new filename appending _compressed to the original file name
    
    new_filename = f"{filename}_compressed.jpg"
    try:
        # save the image with the corresponding quality and optimize set to True
        img.save(new_filename, quality=quality, optimize=True)
    except OSError:
        # convert the image to RGB mode first
        img = img.convert("RGB")
        # save the image with the corresponding quality and optimize set to True
        img.save(new_filename, quality=quality, optimize=True)
    bot.send_message(message.chat.id, f"[+] New file saved:  {new_filename}")
    # get the new image size in bytes
    new_image_size = os.path.getsize(new_filename)
    # print the new size in a good format
    # print("[+] Size after compression:", get_size_format(new_image_size))
    # calculate the saving bytes
    saving_diff = new_image_size - image_size
    # print the saving percentage 
    bot.send_message(message.chat.id, f"[+] Image size change: {saving_diff/image_size*100:.2f}% of the original image size.")

@bot.message_handler(commands=['start'])
def welcome(message):
    sti = open('static/1.jpg', 'rb')
    bot.send_sticker(message.chat.id, sti)

    bot.send_message(message.chat.id, "Բարի գալուստ, {0.first_name}!\nԵս - <b>{1.first_name}</b>, բոտ եմ պատրաստված լավ տղու ոսկե ձեռներով, ձեր նկարների հերը անիծելու համար.".format(message.from_user, bot.get_me()),
        parse_mode='html')
 
@bot.message_handler(content_types=['photo'])
def lalala(message):
    url = 'https://api.telegram.org/bot' + config.TOKEN + '/getFile?file_id=' + message.photo[2].file_id
    f = urllib.request.urlopen(url)
    myfile = f.read().decode("utf-8") 
    path = re.search("\"file_path\":\"(.*)\"", myfile)
    img = "https://api.telegram.org/file/bot" + config.TOKEN + "/" + path.group(1)
    urllib.request.urlretrieve(img, "image/local-filename.jpg")
    compress_img('image/local-filename.jpg', message)
    bot.send_photo(message.chat.id, photo=open('image/local-filename_compressed.jpg', 'rb'))
# RUN
bot.polling(none_stop=True)