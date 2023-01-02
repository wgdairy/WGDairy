from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, Command, _
from odoo.exceptions import RedirectWarning, UserError, ValidationError, AccessError
from odoo.tools import float_compare, date_utils, email_split, email_re, html_escape, is_html_empty
from odoo.tools.misc import formatLang, format_date, get_lang

from datetime import date, timedelta
from collections import defaultdict
from odoo.addons.account.models.account_move import AccountMoveLine

class AccountPartner(models.Model):
    _inherit = "account.move.line"

    finance_charges = fields.Monetary(string='Finance Charge',
                                      related='move_id.finance_charge')
    two_finance_charge = fields.Monetary(string='Finance Charge')
    four_finance_charge = fields.Monetary(string='Finance Charge')
    move_id = fields.Many2one('account.move', string='Journal Entry',
                              index=True, required=True, readonly=True, auto_join=True, ondelete="cascade",
                              check_company=True,
                              help="The move of this entry line.")

    ref = fields.Char(related='move_id.ref', store=True, copy=False, index=True, readonly=False)
    parent_state = fields.Selection(related='move_id.state', store=True, readonly=True)
    journal_id = fields.Many2one(related='move_id.journal_id', store=True, index=True, copy=False)
    company_id = fields.Many2one(related='move_id.company_id', store=True, readonly=True)

    account_id = fields.Many2one('account.account', string='Account',
                                 index=True, ondelete="cascade",
                                 domain="[('deprecated', '=', False), ('company_id', '=', 'company_id'),('is_off_balance', '=', False)]",
                                 check_company=True,
                                 tracking=True)

    discount = fields.Float(string='Discount (%)', digits='Discount', default=0.0)
    debit = fields.Monetary(string='Debit', default=0.0, currency_field='company_currency_id')
    credit = fields.Monetary(string='Credit', default=0.0, currency_field='company_currency_id')
    balance = fields.Monetary(string='Balance', store=True,
                              currency_field='company_currency_id',
                              compute='_compute_balance',
                              help="Technical field holding the debit - credit in order to open meaningful graph views from reports")
    desc_sku = fields.Char(related='product_id.product_tmpl_id.sku', string='Description', readonly=False)
    
    # Modified default tax compute function 
    def _get_computed_taxes(self):
        self.ensure_one()

        if self.move_id.is_sale_document(include_receipts=True):
            # Out invoice.
            if self.move_id.store:
                tax_ids = self.move_id.w_tax
            elif self.product_id.taxes_id:
                tax_ids = self.product_id.taxes_id.filtered(lambda tax: tax.company_id == self.move_id.company_id)
            elif self.account_id.tax_ids:
                tax_ids = self.account_id.tax_ids
            else:
                tax_ids = self.env['account.tax']
            if not tax_ids and not self.exclude_from_invoice_tab:
                if not self.move_id.w_tax:
                    tax_ids = False
                else:
                    tax_ids = self.move_id.company_id.account_sale_tax_id
        elif self.move_id.is_purchase_document(include_receipts=True):
            # In invoice.
            if self.product_id.supplier_taxes_id:
                tax_ids = self.product_id.supplier_taxes_id.filtered(lambda tax: tax.company_id == self.move_id.company_id)
            elif self.account_id.tax_ids:
                tax_ids = self.account_id.tax_ids
            else:
                tax_ids = self.env['account.tax']
            if not tax_ids and not self.exclude_from_invoice_tab:
                tax_ids = self.move_id.company_id.account_purchase_tax_id
        else:
            # Miscellaneous operation.
            tax_ids = self.account_id.tax_ids

        if self.company_id and tax_ids:
            tax_ids = tax_ids.filtered(lambda tax: tax.company_id == self.company_id)

        return tax_ids





    @api.model
    def default_get(self, default_fields):
        # OVERRIDE
        # payment = models.Model.default_get(self, fields)
        values = super(AccountMoveLine, self).default_get(default_fields)

        if 'account_id' in default_fields and not values.get('account_id') \
            and (self._context.get('journal_id') or self._context.get('default_journal_id')) \
            and self._context.get('default_move_type') in ('out_invoice', 'out_refund',  'in_refund', 'out_receipt', 'in_receipt'):  #'in_invoice',
            # Fill missing 'account_id'.
            journal = self.env['account.journal'].browse(self._context.get('default_journal_id') or self._context['journal_id'])
            values['account_id'] = journal.default_account_id.id
        elif self._context.get('line_ids') and any(field_name in default_fields for field_name in ('debit', 'credit', 'account_id', 'partner_id')):
            move = self.env['account.move'].new({'line_ids': self._context['line_ids']})

            # Suggest default value for debit / credit to balance the journal entry.
            balance = sum(line['debit'] - line['credit'] for line in move.line_ids)
            # if we are here, line_ids is in context, so journal_id should also be.
            journal = self.env['account.journal'].browse(self._context.get('default_journal_id') or self._context['journal_id'])
            currency = journal.exists() and journal.company_id.currency_id
            if currency:
                balance = currency.round(balance)
            if balance < 0.0:
                values.update({'debit': -balance})
            if balance > 0.0:
                values.update({'credit': balance})

            # Suggest default value for 'partner_id'.
            if 'partner_id' in default_fields and not values.get('partner_id'):
                if len(move.line_ids[-2:]) == 2 and  move.line_ids[-1].partner_id == move.line_ids[-2].partner_id != False:
                    values['partner_id'] = move.line_ids[-2:].mapped('partner_id').id

            # Suggest default value for 'account_id'.
            if 'account_id' in default_fields and not values.get('account_id'):
                if len(move.line_ids[-2:]) == 2 and  move.line_ids[-1].account_id == move.line_ids[-2].account_id != False:
                    values['account_id'] = move.line_ids[-2:].mapped('account_id').id
        if values.get('display_type') or self.display_type:
            values.pop('account_id', None)

        return values



    # @api.depends('product_id')
    # def _compute_finance_charge(self):
    #     untx_amt = 0
    #     todays_date = date.today()
    #     # today = fields.Date.today()

    #     for r in self:

    #         if r.move_id.invoice_date:
    #             inv_date = r.move_id.invoice_date
    #             one_mon = inv_date.replace(day=30)
    #             two_per = one_mon + relativedelta(months=2)
    #             four_per = one_mon + relativedelta(months=3)
    #             six_per = one_mon + relativedelta(months=4)
    #             two_per_fin_date = two_per.replace(day=1)
    #             four_per_fin_date = four_per.replace(day=1)
    #             six_per_fin_date = six_per.replace(day=1)

    #             if todays_date > two_per_fin_date and todays_date <= four_per_fin_date:
    #                 untx_amt = r.move_id.amount_untaxed
    #                 amt = (untx_amt * 2) / 100
    #                 r.finance_charges = amt

    #             elif todays_date > four_per_fin_date and todays_date <= six_per_fin_date:
    #                 untx_amt = r.move_id.amount_untaxed
    #                 amt = (untx_amt * 4) / 100
    #                 r.finance_charges = amt

    #             elif todays_date > six_per_fin_date:
    #                 untx_amt = r.move_id.amount_untaxed
    #                 amt = (untx_amt * 6) / 100
    #                 r.finance_charges = amt
    #             else:

    #                 r.finance_charges = 0
    #         else:

    #             r.finance_charges = 0


class AccountMovePartner(models.Model):
    _inherit = "account.move"


    transaction_type = fields.Selection(selection=[
        ('vendor_bill', 'Vendor Bill For PO'),
        ('journal_transaction', 'Journal Transaction'),
    ], string='Transaction Type', required=True, default="journal_transaction")
    finance_charge = fields.Monetary(string='Finance Charge', store=True, compute='_compute_finance_charges')
    two_finance_charge = fields.Monetary(string='Finance Charge', store=True)
    four_finance_charge = fields.Monetary(string='Finance Charge', store=True)
    parant_invoice = fields.Char()

    @api.onchange('invoice_date', 'highest_name', 'company_id')
    def _onchange_invoice_date(self):
        if self.invoice_date:
            if not self.invoice_payment_term_id and (not self.invoice_date_due or self.invoice_date_due < self.invoice_date):
                self.invoice_date_due = self.invoice_date

            has_tax = bool(self.line_ids.tax_ids or self.line_ids.tax_tag_ids)
            accounting_date = self._get_accounting_date(self.invoice_date, has_tax)
            if accounting_date != self.date:
                if self.move_type == 'in_invoice':
                    # self.date = accounting_date
                    self._onchange_currency()
                else:
                    self.date = accounting_date
                    self._onchange_currency()

            else:
                self._onchange_recompute_dynamic_lines()

    # @api.onchange('job_ord_no')
    @api.depends('invoice_date')
    def _compute_finance_charges(self):
        untx_amt = 0
        todays_date = date.today()


        for r in self:

            if r.invoice_date:
                inv_date = r.invoice_date
                if inv_date.month == 2:
                    one_mon = inv_date.replace(day=28)

                else:
                    one_mon = inv_date.replace(day=30)
                # date_rep = r.invoice_date
                # one_mon = inv_date.replace(day=30)
                # two_mo = date_rep.replace(day=30)
                # three_mo = date_rep.replace(day=30)
                two_per = one_mon + relativedelta(months=2)
                four_per = one_mon + relativedelta(months=3)
                six_per = one_mon + relativedelta(months=4)
                two_per_fin_date = two_per.replace(day=1)
                four_per_fin_date = four_per.replace(day=1)
                six_per_fin_date = six_per.replace(day=1)
                untx_amt = r.amount_untaxed
                # four_finance_charge = 0


                if todays_date > two_per_fin_date and todays_date <= four_per_fin_date:
                    amt_two = (untx_amt * 2) / 100
                    r.finance_charge = amt_two
                elif todays_date > four_per_fin_date and todays_date <= six_per_fin_date:
                    amt = (untx_amt * 2) / 100
                    amt_four_two = amt + untx_amt
                    amt_four_three =  (amt_four_two * 2) / 100
                    amt_tot = amt_four_three + amt
                    r.finance_charge = amt_tot

                elif todays_date > six_per_fin_date:
                    # six_fin_charge = r.four_finance_charge
                    amt = (untx_amt * 2) / 100
                    amt_six_one =  amt + untx_amt
                    amt_six_two = (amt_six_one * 2) / 100
                    amt_six_three = amt + amt_six_two + untx_amt
                    amt_six_four = (amt_six_three * 2) / 100
                    amt_six_total = amt + amt_six_two + amt_six_four
                    r.finance_charge = amt_six_total
                else:
                    r.finance_charge = 0
                    # r.two_finance_charge = 0
                    # r.four_finance_charge = 0
            else:
                r.finance_charge = 0
                # r.two_finance_charge = 0
                # r.four_finance_charge = 0



    def _post(self, soft=True):
        """Post/Validate the documents.

        Posting the documents will give it a number, and check that the document is
        complete (some fields might not be required if not posted but are required
        otherwise).
        If the journal is locked with a hash table, it will be impossible to change
        some fields afterwards.

        :param soft (bool): if True, future documents are not immediately posted,
            but are set to be auto posted automatically at the set accounting date.
            Nothing will be performed on those documents before the accounting date.
        :return Model<account.move>: the documents that have been posted
        """
        if soft:
            future_moves = self.filtered(lambda move: move.date > fields.Date.context_today(self))
            future_moves.auto_post = True
            for move in future_moves:
                msg = _('This move will be posted at the accounting date: %(date)s',
                        date=format_date(self.env, move.date))
                move.message_post(body=msg)
            to_post = self - future_moves
        else:
            to_post = self

        # `user_has_group` won't be bypassed by `sudo()` since it doesn't change the user anymore.
        if not self.env.su and not self.env.user.has_group('account.group_account_invoice'):
            raise AccessError(_("You don't have the access rights to post an invoice."))
        for move in to_post:
            if move.partner_bank_id and not move.partner_bank_id.active:
                raise UserError(
                    _("The recipient bank account link to this invoice is archived.\nSo you cannot confirm the invoice."))
            if move.state == 'posted':
                raise UserError(_('The entry %s (id %s) is already posted.') % (move.name, move.id))
            if not move.line_ids.filtered(lambda line: not line.display_type):
                raise UserError(_('You need to add a line before posting.'))
            if move.auto_post and move.date > fields.Date.context_today(self):
                date_msg = move.date.strftime(get_lang(self.env).date_format)
                raise UserError(_("This move is configured to be auto-posted on %s", date_msg))
            if not move.journal_id.active:
                raise UserError(_(
                    "You cannot post an entry in an archived journal (%(journal)s)",
                    journal=move.journal_id.display_name,
                ))

            if not move.partner_id:
                if move.is_sale_document():
                    raise UserError(
                        _("The field 'Customer' is required, please complete it to validate the Customer Invoice."))
                elif move.is_purchase_document():
                    raise UserError(
                        _("The field 'Vendor' is required, please complete it to validate the Vendor Bill."))

            if move.is_invoice(include_receipts=True) and float_compare(move.amount_total, 0.0,
                                                                        precision_rounding=move.currency_id.rounding) < 0:
                raise UserError(
                    _("You cannot validate an invoice with a negative total amount. You should create a credit note instead. Use the action menu to transform it into a credit note or refund."))

            if move.display_inactive_currency_warning:
                raise UserError(_("You cannot validate an invoice with an inactive currency: %s",
                                  move.currency_id.name))

            # Handle case when the invoice_date is not set. In that case, the invoice_date is set at today and then,
            # lines are recomputed accordingly.
            # /!\ 'check_move_validity' must be there since the dynamic lines will be recomputed outside the 'onchange'
            # environment.
            if not move.invoice_date:
                if move.is_sale_document(include_receipts=True):
                    move.invoice_date = fields.Date.context_today(self)
                    move.with_context(check_move_validity=False)._onchange_invoice_date()
                elif move.is_purchase_document(include_receipts=True):
                    raise UserError(_("The Bill/Refund date is required to validate this document."))

            # When the accounting date is prior to the tax lock date, move it automatically to today.
            # /!\ 'check_move_validity' must be there since the dynamic lines will be recomputed outside the 'onchange'
            # environment.
            if (move.company_id.tax_lock_date and move.date <= move.company_id.tax_lock_date) and (
                    move.line_ids.tax_ids or move.line_ids.tax_tag_ids):
                move.date = move._get_accounting_date(move.invoice_date or move.date, True)
                move.with_context(check_move_validity=False)._onchange_currency()

        # Create the analytic lines in batch is faster as it leads to less cache invalidation.
        to_post.mapped('line_ids').create_analytic_lines()
        to_post.write({
            'state': 'posted',
            'posted_before': True,
        })

        for move in to_post:
            move.message_subscribe([p.id for p in [move.partner_id] if p not in move.sudo().message_partner_ids])

            # Compute 'ref' for 'out_invoice'.
            if move._auto_compute_invoice_reference():
                to_write = {
                    'payment_reference': move._get_invoice_computed_reference(),
                    'line_ids': []
                }
                for line in move.line_ids.filtered(
                        lambda line: line.account_id.user_type_id.type in ('receivable', 'payable')):
                    to_write['line_ids'].append((1, line.id, {'name': to_write['payment_reference']}))
                move.write(to_write)

        for move in to_post:
            if move.is_sale_document() \
                    and move.journal_id.sale_activity_type_id \
                    and (move.journal_id.sale_activity_user_id or move.invoice_user_id).id not in (
                    self.env.ref('base.user_root').id, False):
                move.activity_schedule(
                    date_deadline=min((date for date in move.line_ids.mapped('date_maturity') if date),
                                      default=move.date),
                    activity_type_id=move.journal_id.sale_activity_type_id.id,
                    summary=move.journal_id.sale_activity_note,
                    user_id=move.journal_id.sale_activity_user_id.id or move.invoice_user_id.id,
                )

        customer_count, supplier_count = defaultdict(int), defaultdict(int)
        for move in to_post:
            if move.is_sale_document():
                customer_count[move.partner_id] += 1
            elif move.is_purchase_document():
                supplier_count[move.partner_id] += 1
        for partner, count in customer_count.items():
            (partner | partner.commercial_partner_id)._increase_rank('customer_rank', count)
        for partner, count in supplier_count.items():
            (partner | partner.commercial_partner_id)._increase_rank('supplier_rank', count)

        # Trigger action for paid invoices in amount is zero
        to_post.filtered(
            lambda m: m.is_invoice(include_receipts=True) and m.currency_id.is_zero(m.amount_total)
        ).action_invoice_paid()

        # Force balance check since nothing prevents another module to create an incorrect entry.
        # This is performed at the very end to avoid flushing fields before the whole processing.
        to_post._check_balanced()
        self._finacharge()

        return to_post

    def _finacharge(self):

        for rec in self:

            if rec.finance_charge > 0 and rec.finance_charge != None:

                move_line = []
                move_line_ids = [0, False]
                move_line_vals = {}

                if rec.invoice_line_ids.account_id.code:
                    account = rec.env['account.account'].search([('code', '=', rec.invoice_line_ids.account_id.code)])

                else:
                    account = rec.env['account.account'].search([('code', '=', '4000100')])

                move_line_vals['name'] = 'Finance Charge'
                move_line_vals['price_unit'] = rec.finance_charge
                move_line_vals['finance_charges'] = rec.finance_charge
                move_line_vals['quantity'] = 1
                move_line_vals['account_id'] = account.id
                # move_line_vals['date'] = rec.invoice_date
                move_line_vals['date_maturity'] = rec.invoice_date_due
                move_line_ids.append(move_line_vals)
                move_line.append(move_line_ids)
                move_vals = {}
                move_vals['date'] = rec.date
                move_vals['state'] = 'draft'
                # move_vals['invoice_date'] = rec.invoice_date
                move_vals['invoice_date'] = date.today()
                move_vals['partner_id'] = rec.partner_id.id
                move_vals['invoice_date_due'] = rec.invoice_date_due
                move_vals['payment_reference'] = rec.name + '- Finance charge'
                move_vals['move_type'] = rec.move_type
                move_vals['invoice_line_ids'] = move_line
                move_vals['parant_invoice'] = self.name

                invoice = rec.env['account.move'].search([('parant_invoice', '=', self.name)])

                if invoice:
                    # invoice.update(move_vals)
                    invoice.state = 'draft'
                    invoice.write({'invoice_line_ids': [(5, 0, 0)]})
                    invoice.update(move_vals)

                    invoice._onchange_invoice_line_ids()
                    invoice.state = 'posted'
                else:
                    journal = rec.env['account.move'].create(move_vals)
                    journal._onchange_invoice_line_ids()
                    journal.state = 'posted'


