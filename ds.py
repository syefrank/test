from pagermaid.listener import listener
from pagermaid.utils import Message, pip_install
import urllib.request
import os
import random

# 安装所需的软件包
pip_install('Pillow')

# 导入所需模块
from PIL import Image, ImageDraw, ImageFont, ImageOps


@listener(command='ds', description='将用户输入文本转换为PNG图像，并将结果作为照片上传到Telegram。')
async def ds(message: Message):
    # 从消息参数获取输入文本
    args = message.arguments.split()
    text = args[0].strip()
    
    if message.reply_to_message:
        reply_message = message.reply_to_message
        text = reply_message.text.strip()

    # 基于输入文本的长度确定图像尺寸
    font_size = 120
    plugin_dir = 'plugins/ds'
    if not os.path.exists(plugin_dir):
        os.makedirs(plugin_dir)
    font_url = 'https://raw.githubusercontent.com/freefrank/font/main/%E4%B8%89%E6%9E%81%E6%B3%BC%E5%A2%A8%E4%BD%93.ttf'
    font_file = f'{plugin_dir}/font.ttf'
    if not os.path.isfile(font_file):
        urllib.request.urlretrieve(font_url, font_file)

    if len(args) > 1:
        try:
            font_size = int(args[1])
        except ValueError:
            pass

    font = ImageFont.truetype(font_file, font_size, encoding='unic')

    # 根据每行字符数计算换行位置
    line_length = 3
    lines = [text[i:i+line_length] for i in range(0, len(text), line_length)]
    text = '\n'.join(lines)

    # 根据换行后的文本长度确定图像尺寸
    image_width, image_height = font.getsize_multiline(text)
    image_width += 50
    image_height += 20
    color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    image = Image.new('RGBA', (image_width, image_height), color=(color[0], color[1], color[2], 255))

    # 加载字体并创建绘图上下文
    draw = ImageDraw.Draw(image)

    # 将文本绘制到图像上
    draw.multiline_text((25, 10), text, font=font, fill=(255, 255, 255))

    # 创建圆角掩码
    radius = 20
    mask = Image.new("L", (image_width, image_height), 0)
    draw_mask = ImageDraw.Draw(mask)
    draw_mask.rectangle((radius, 0, image_width - radius, image_height), fill=255)
    draw_mask.rectangle((0, radius, image_width, image_height - radius), fill=255)
    draw_mask.pieslice((0, 0, radius*2, radius*2), 180, 270, fill=255)
    draw_mask.pieslice((image_width - radius*2, 0, image_width, radius*2), 270, 360, fill=255)
    draw_mask.pieslice((0, image_height - radius*2, radius*2, image_height), 90, 180, fill=255)
    draw_mask.pieslice((image_width - radius*2, image_height - radius*2, image_width, image_height), 0, 90, fill=255)

    # 应用圆角掩码
    image.putalpha(mask)

    # 将图像保存为PNG文件
    img_path = 'plugins/ds/text_image.webp'
    image.save(img_path, "WEBP")

    # 将图像作为照片上传到Telegram
    try:
        await message.reply_document(img_path, quote=False, reply_to_message_id=message.reply_to_top_message_id,)
    except Exception as e:
        await edit_delete(message, "无法上传图像，请检查日志以获取详细信息。")
    await message.safe_delete()

    # 从磁盘中删除图像文件
    os.remove(img_path)
