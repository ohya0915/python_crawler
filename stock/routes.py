from flask import Blueprint, flash, redirect, url_for, render_template, Response
from flask_login import current_user, login_required
from stock.forms import StockForm
from utils import GetWebInfo, check_month_length, StockToCsv

stock = Blueprint('stock', __name__)

twse_url = 'https://www.twse.com.tw/exchangeReport/FMSRFK?'   #舊版

@login_required
@stock.route("/stock", methods=['GET', 'POST'])  
def collect():
    if current_user.is_authenticated:
        form = StockForm()
        if form.validate_on_submit():
            try:
                url = twse_url
                target_year = form.target_year.data
                target_stock = form.search_stock.data
                get_info = GetWebInfo()
                result = get_info.range_stock(url, target_year, target_stock)
            except Exception as error:
                flash('Type error!', 'warning')
                return redirect(url_for('stock.collect'))
            return render_template('stock_result.html', data=result['data'], title=result['title'], target_year=target_year, target_stock=target_stock)
    else:
        flash('You need login!', 'warning')
        return redirect(url_for('main.home'))
    return render_template('stock.html', form=form)
    

@login_required
@stock.route("/stock_to_csv/<string:target_year>/<string:target_stock>", methods=['GET', 'POST']) 
def stock_to_csv(target_year, target_stock):
    if current_user.is_authenticated:
        try:
            url = twse_url
            get_info = GetWebInfo()
            data = get_info.range_stock(url, target_year, target_stock)
            to_csv = StockToCsv()
            result = to_csv.month_detail_csv(data)
            return Response(
                result.encode('big5'),
                mimetype="text/csv",
                headers={"Content-disposition":
                        "attachment; filename=Hans_Web_{}_{}.csv".format(target_stock, target_year)}
            )

        except Exception as error:
            flash('Type error!', 'warning')
            return redirect(url_for('stock.stock_to_csv', target_year=target_year, target_stock=target_stock))

        return render_template('stock_result.html', form=form, data=data['data'], title=data['title'], target_year=target_year, target_stock=target_stock)
    else:
        flash('You need login!', 'warning')
        return redirect(url_for('main.home'))
    return render_template('stock.html', form=form)
   
