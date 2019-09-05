import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from chaojiying import Chaojiying_Client


def get_cookie():
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(chrome_options=chrome_options)
    driver.get('http://yitjw.minghuaetc.com/yjlgxy/')
    cookies_dict = driver.get_cookies()[0]
    cookies = {
        cookies_dict['name']: cookies_dict['value']
    }
    driver.quit()
    return cookies


def requests_login(username, password):
    session = requests.session()
    cookies = get_cookie()
    str_url = 'http://yitjw.minghuaetc.com/yjlgxy/Logon.do?method=logon&flag=sess'
    data_str = session.post(str_url, cookies=cookies).text
    scode = data_str.split('#')[0]
    sxh = data_str.split('#')[1]
    code = username + '%%%' + password
    encoded = ''
    for i in range(len(code)):
        if i < 20:
            encoded += code[i] + scode[:int(sxh[i])]
            scode = scode[int(sxh[i]):]
        else:
            encoded += code[i:]
            break

    captcha_url = 'http://yitjw.minghuaetc.com/yjlgxy/verifycode.servlet'
    img = session.get(captcha_url, cookies=cookies).content
    # 保存验证码图片
    with open('1.png', 'wb') as f:
        f.write(img)
    chaojiying = Chaojiying_Client('daxueshiguang', 'dxsg666666', '901221')
    im = open('1.png', 'rb').read()
    # 调用接口识别
    res = chaojiying.PostPic(im, 1902)
    # 识别结果
    pic_str = res['pic_str']

    login_url = 'http://yitjw.minghuaetc.com/yjlgxy/Logon.do?method=logon'
    data = {
        'view': '0',
        'useDogCode': '',
        'encoded': encoded,
        'RANDOMCODE': pic_str
    }
    session.post(login_url, cookies=cookies, data=data)
    return session
