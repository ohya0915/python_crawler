from config import Config
import requests
# from bs4 import BeautifulSoup
import pandas as pd
from threading import Thread
import smtplib
# from mimetypes import guess_type
from flask import render_template, current_app
from flask_login import current_user
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.header import Header
from email.utils import parseaddr, formataddr

def password_policy_check(user_password):
    import re

    check_errors = []

    min_length = Config.MINIMUM_PASSWORD_LENGTH
    password_complex = Config.PASSWORD_COMPLEX_PATTER
    

    if len(user_password) < min_length:
        err_msg = f"Password at least {min_length} chracters"
        check_errors.append(err_msg)

    if password_complex and not re.search(password_complex, user_password):
        err_msg = "Passowrd does not meet complexity rules"
        check_errors.append(err_msg)

    return check_errors if check_errors else False



def _operator():
    
    return current_user.name if current_user and current_user.is_authenticated else None


def _format_addr(s):
    
    name, addr = parseaddr(s)
    return formataddr((Header(name, "utf-8").encode(), addr))


def send_mail_async(app, msg):
    
    with app.app_context():
        try:
            with smtplib.SMTP(host=Config.MAIL_SERVER, port=Config.MAIL_PORT) as smtp:
                # 這裡加上送件者
                body = msg["Body"]
                body["From"] = _format_addr(Config.MAIL_DEFAULT_SENDER)
                
                smtp.starttls()
                
                smtp.login(Config.MAIL_DEFAULT_SENDER, Config.MAIL_DEFAULT_SENDER_PASSWORD)
                current_app.logger.debug("will send mail to {}".format(body["To"]))
                smtp.sendmail(from_addr=Config.MAIL_DEFAULT_SENDER,
                              to_addrs=msg["To"]+msg["Cc"]+msg["Bcc"],
                              msg=body.as_string())

                smtp.quit()

        except Exception as e:
            app.logger.error(str(e))


def create_mail_message(to: [str, list], subject: str, text: str = None, template: str = None, **kwargs):
    
    msg = {"To": [], "Cc": [], "Bcc": []}
    
    mail = None
    
    mime_text = None
    if template:
        html = render_template("{}".format(template), operator=_operator(), **kwargs)
        mime_text = MIMEText(html, "html", "utf-8")
    else:
        mime_text = MIMEText(text, "plain", "utf-8")

    if mail:
        mail.attach(mime_text)
    else:
        mail = mime_text

    mail["Subject"] = Header(subject, "utf-8").encode()
    recipients = []
    if type(to) == list:
        recipients += to
    else:
        recipients.append(to)
    msg["To"] = [_format_addr(recipient) for recipient in recipients]
    mail["To"] = ",".join(msg["To"])

    msg["Body"] = mail

    return msg


def send_mail(msgs):
    
    app = current_app._get_current_object()
    thread = Thread(target=send_mail_async, args=[app, msgs])
    thread.start()
    return thread


def check_month_length(month):
    '''
    check month length
    input: str
    output: str
    '''
    if len(month) < 2:
        month = '0' + month
    return month


class GetWebInfo:
    def get_web(slef, url):
        '''
        get web infomation
        input: url
        output: list
        '''
        html = requests.get(url)
        row_data = html.json()
        total_results = row_data['pagination']['resultsTotal']
        result = []
        if total_results > 30:
            result = row_data['list']
            n = 30
            numbers = total_results - 30
            length = 0
            if numbers % 30 == 0:
                length = numbers // 30
            else:
                length = (numbers // 30) + 1
            for i in range(length):
                other_html = requests.get(url.replace('offset=0', 'offset=' + str(n)))
                other_data = other_html.json()
                result.extend(other_data['list'])
                n = n + 30
            return result
        result = row_data['list']
        return result


    def class_stock(self, url):
        '''
        get web infomation
        input: url
        output: DataFrame
        '''
        data = self.get_web(url)
        
        names_list = []
        target_list = []
        group_list = []
        times_list = []
        for value in data:
            names_list.append(value['symbolName'])
            target_list.append(value['price'])
            if value['changeStatus'] == 'up':
                target_list.append('+' + value['change'])
            else:
                target_list.append(value['change'])
            target_list.append(value['changePercent'])
            target_list.append(value['regularMarketOpen'])
            target_list.append(value['regularMarketPreviousClose'])
            target_list.append(value['regularMarketDayHigh'])
            target_list.append(value['regularMarketDayLow'])
            if value['volumeK'] == None:
                target_list.append('-')
            else:
                target_list.append(value['volumeK'])
            group_list.append(target_list)
            target_list = []
            time = '-'
            if value['regularMarketTime'] != '-':
                time = value['regularMarketTime'][11:16]
                time = str(int(time[:2]) + 8) + time[2:]
            times_list.append(time)
        
        pd.set_option("max_rows", None)
        df = pd.DataFrame(group_list, columns =['股價', '漲跌', '漲跌幅(%)','開盤', '昨收', '最高','最低', '成交量(張)'])
        df.insert(loc=0, column='股票名稱', value=names_list)
        df.insert(loc=9, column='時間', value=times_list)
        df.index += 1

        return df

    def range_stock(self, url, target_year, target_stock):
        '''
        get stock range info
        input: url
        output: dict
        '''
        table_dict = {}
        result = requests.get(url + 'date=' + target_year + '0112&stockNo=' + target_stock)
        data = result.json()
        title = data['title']
        columns = data['fields']
        group_list = data['data']
        pd.set_option("max_rows", None)
        
        df = pd.DataFrame(group_list, columns=columns)
        df.index += 1
        table_dict['data'] = df
        table_dict['title'] = title
        return table_dict


class StockToCsv():
    def daily_detail_csv(self, url, target_year, target_month, target_stock):
        '''
        get stock target year month's daily detail csv
        input: url
        output: csv
        '''
        data = requests.get(url + '&date=' + target_year + target_month + '10' + '&stockNo=' + target_stock)
        return data

    def month_detail_csv(self, data):
        '''
        get stock target year's month detail csv
        input: dict
        output: csv
        '''
        df = data['data']
        result = df.to_csv(index=False)
        return result
