from flask import Blueprint, flash, redirect, url_for, render_template, Response
from flask_login import current_user, login_required
from daily_record.forms import TargetStockForm
from utils import StockToCsv, check_month_length

daily_record = Blueprint('daily_record', __name__)

twse_url = 'http://www.twse.com.tw/exchangeReport/STOCK_DAY?response=csv'

@login_required
@daily_record.route("/target_stock", methods=['GET', 'POST']) 
def to_csv():
    if current_user.is_authenticated:
        form = TargetStockForm()
        if form.validate_on_submit():
            try:
                to_csv = StockToCsv()
                url = twse_url
                target_year = form.target_year.data
                target_month = form.target_month.data
                target_stock = form.target_stock.data
                target_month = check_month_length(target_month)
                result = to_csv.daily_detail_csv(url, target_year, target_month, target_stock)
                
                return Response(
                    result,
                    mimetype="text/csv",
                    headers={"Content-disposition":
                            "attachment; filename=Hans_Web_{}_{}{}.csv".format(target_stock, target_year, target_month)}
                )

            except Exception as error:
                flash('Type error!', 'warning')
                return redirect(url_for('daily_record.to_csv'))

            return render_template('dialy_record.html', form=form)
    else:
        flash('You need login!', 'warning')
        return redirect(url_for('main.home'))
    return render_template('dialy_record.html', form=form)

    


   
