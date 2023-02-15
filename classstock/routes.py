from flask import Blueprint, flash, redirect, url_for, render_template
from flask_login import current_user
from utils import GetWebInfo

classstock = Blueprint('classstock', __name__)
# 類別對照表
class_list = {
    1: '水泥', 2: '食品', 3: '塑膠', 4: '紡織', 5: '電機', 6: '電器電纜', 7: '化學',
    8: '生技', 9: '玻璃', 10: '造紙', 11: '鋼鐵', 12: '橡膠', 13: '汽車', 14: '半導體',
    15: '電腦周邊', 16: '光電', 17: '通訊網路', 18: '電子零組件', 19: '電子通路', 20: '資訊服務',
    21: '其它電子', 22:'營建', 23: '航運', 24: '觀光', 25: '金融業', 26: '貿易百貨', 27:'油電燃氣',
    28: '存託憑證', 29: '受益證卷', 30: '其它'
}

class_dict = {
    1: "https://tw.stock.yahoo.com/_td-stock/api/resource/StockServices.getClassQuotes;exchange=TAI;offset=0;sectorId=1",
    2: "https://tw.stock.yahoo.com/_td-stock/api/resource/StockServices.getClassQuotes;exchange=TAI;offset=0;sectorId=2",
    3: "https://tw.stock.yahoo.com/_td-stock/api/resource/StockServices.getClassQuotes;exchange=TAI;offset=0;sectorId=3",
    4: "https://tw.stock.yahoo.com/_td-stock/api/resource/StockServices.getClassQuotes;exchange=TAI;offset=0;sectorId=4",
    5: "https://tw.stock.yahoo.com/_td-stock/api/resource/StockServices.getClassQuotes;exchange=TAI;offset=0;sectorId=6",
    6: "https://tw.stock.yahoo.com/_td-stock/api/resource/StockServices.getClassQuotes;exchange=TAI;offset=0;sectorId=7",
    7: "https://tw.stock.yahoo.com/_td-stock/api/resource/StockServices.getClassQuotes;exchange=TAI;offset=0;sectorId=37",
    8: "https://tw.stock.yahoo.com/_td-stock/api/resource/StockServices.getClassQuotes;exchange=TAI;offset=0;sectorId=38",
    9: "https://tw.stock.yahoo.com/_td-stock/api/resource/StockServices.getClassQuotes;exchange=TAI;offset=0;sectorId=9",
    10: "https://tw.stock.yahoo.com/_td-stock/api/resource/StockServices.getClassQuotes;exchange=TAI;offset=0;sectorId=10",
    11: "https://tw.stock.yahoo.com/_td-stock/api/resource/StockServices.getClassQuotes;exchange=TAI;offset=0;sectorId=11",
    12: "https://tw.stock.yahoo.com/_td-stock/api/resource/StockServices.getClassQuotes;exchange=TAI;offset=0;sectorId=12",
    13: "https://tw.stock.yahoo.com/_td-stock/api/resource/StockServices.getClassQuotes;exchange=TAI;offset=0;sectorId=13",
    14: "https://tw.stock.yahoo.com/_td-stock/api/resource/StockServices.getClassQuotes;exchange=TAI;offset=0;sectorId=40",
    15: "https://tw.stock.yahoo.com/_td-stock/api/resource/StockServices.getClassQuotes;exchange=TAI;offset=0;sectorId=41",
    16: "https://tw.stock.yahoo.com/_td-stock/api/resource/StockServices.getClassQuotes;exchange=TAI;offset=0;sectorId=42",
    17: "https://tw.stock.yahoo.com/_td-stock/api/resource/StockServices.getClassQuotes;exchange=TAI;offset=0;sectorId=43",
    18: "https://tw.stock.yahoo.com/_td-stock/api/resource/StockServices.getClassQuotes;exchange=TAI;offset=0;sectorId=44",
    19: "https://tw.stock.yahoo.com/_td-stock/api/resource/StockServices.getClassQuotes;exchange=TAI;offset=0;sectorId=45",
    20: "https://tw.stock.yahoo.com/_td-stock/api/resource/StockServices.getClassQuotes;exchange=TAI;offset=0;sectorId=46",
    21: "https://tw.stock.yahoo.com/_td-stock/api/resource/StockServices.getClassQuotes;exchange=TAI;offset=0;sectorId=47",
    22: "https://tw.stock.yahoo.com/_td-stock/api/resource/StockServices.getClassQuotes;exchange=TAI;offset=0;sectorId=19",
    23: "https://tw.stock.yahoo.com/_td-stock/api/resource/StockServices.getClassQuotes;exchange=TAI;offset=0;sectorId=20",
    24: "https://tw.stock.yahoo.com/_td-stock/api/resource/StockServices.getClassQuotes;exchange=TAI;offset=0;sectorId=21",
    25: "https://tw.stock.yahoo.com/_td-stock/api/resource/StockServices.getClassQuotes;exchange=TAI;offset=0;sectorId=22",
    26: "https://tw.stock.yahoo.com/_td-stock/api/resource/StockServices.getClassQuotes;exchange=TAI;offset=0;sectorId=24",
    27: "https://tw.stock.yahoo.com/_td-stock/api/resource/StockServices.getClassQuotes;exchange=TAI;offset=0;sectorId=39",
    28: "https://tw.stock.yahoo.com/_td-stock/api/resource/StockServices.getClassQuotes;exchange=TAI;offset=0;sectorId=25",
    29: "https://tw.stock.yahoo.com/_td-stock/api/resource/StockServices.getClassQuotes;exchange=TAI;offset=0;sectorId=29",
    30: "https://tw.stock.yahoo.com/_td-stock/api/resource/StockServices.getClassQuotes;exchange=TAI;offset=0;sectorId=30"
}


@classstock.route("/class_stock")
def class_stock():
    if current_user.is_authenticated:
        return render_template('classstock.html')
    else:
        flash('You need login!', 'warning')
        return redirect(url_for('main.home'))

@classstock.route("/classstock_result/<int:number>", methods=['GET', 'POST'])
def classstock_result(number):
    if current_user.is_authenticated:
        web_data = GetWebInfo()
        data = web_data.class_stock(class_dict[number])
    else:
        flash('You need login!', 'warning')
        return redirect(url_for('main.home'))

    return render_template('classstock_result.html', data=data)

