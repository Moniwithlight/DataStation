import random



def generate_captcha_code(length=4):
    """生成图片验证码字符串"""
    selected_chars = random.choices(
        '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz',
        k=length
    )
    return ''.join(selected_chars)