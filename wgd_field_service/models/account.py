from odoo import models, fields, api
from datetime import date,timedelta
# from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

class AccountPartner(models.Model):
    _inherit = "account.move.line"

    finance_charges = fields.Monetary(string='Finance Charge', compute='_compute_finance_charge')

    def _compute_finance_charge(self):
        untx_amt = 0
        todays_date = date.today()
        # today = fields.Date.today()

        for r in self:

            if r.move_id.invoice_date_due:
                inv_date = r.move_id.invoice_date_due
                date_rep = r.move_id.invoice_date_due
                one_mon = inv_date.replace(day=30)
                two_mo = date_rep.replace(day=30)
                three_mo = date_rep.replace(day=30)
                two_mons = two_mo + relativedelta(months=2)
                three_mon = three_mo + relativedelta(months=3)

                if todays_date > one_mon and todays_date <= two_mons:
                    untx_amt = r.move_id.amount_untaxed
                    amt = (untx_amt * 2) / 100
                    r.finance_charges = amt

                elif todays_date > two_mons and todays_date <= three_mon:
                    untx_amt = r.move_id.amount_untaxed
                    amt = (untx_amt * 4) / 100
                    r.finance_charges = amt

                elif todays_date > three_mon:
                    untx_amt = r.move_id.amount_untaxed
                    amt = (untx_amt * 6) / 100
                    r.finance_charges = amt
                else:

                    r.finance_charges = 0
            else:

                r.finance_charges = 0




