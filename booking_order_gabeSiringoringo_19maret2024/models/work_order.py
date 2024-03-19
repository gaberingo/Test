from odoo import models, fields, api,_
from odoo.exceptions import UserError

STATE = [
    ('pending','Pending'),
    ('in_progress','In Progress'),
    ('done','Done'),
    ('cancel','Cancelled')
]

class WorkOrder(models.Model):
    _name = 'work.order'
    _description = 'Work Order'
    
    name = fields.Char(
        string="WO Number",
        readonly=True,
        default=lambda self: _("New"),
        copy=False,
    )
    bo_ref = fields.Many2one(
        'sale.order',
        string="Booking Order Reference",
        readonly=True,
    )
    service_team = fields.Many2one(
        'service.team',
        string="Team",
        required=True
    )
    team_lead = fields.Many2one(
        'res.users',
        string="Team Leader",
        required=True
    )
    team_members = fields.Many2many(
        'res.users',
        string="Team Members",
    )
    planned_start = fields.Date(
        string="Planned Start",
        required=True
    )
    planned_end = fields.Date(
        string="Planned End",
        required=True
    )
    date_start = fields.Date(
        string="Date Start",
        readonly=True
    )
    date_end = fields.Date(
        string="Date End",
        readonly=True
    )
    state = fields.Selection(
        selection=STATE,
        default='pending',
    )
    notes = fields.Text()
    
    def action_start_work(self):
        self.state = 'in_progress'
        self.date_start = fields.Date.today()
    
    def action_end_work(self):
        self.state = 'done'
        self.date_end = fields.Date.today()
    
    def action_reset(self):
        self.write(
            {
                'state':'pending',
                'date_start':False,
                'date_end':False
            }
        )
    
    def action_cancel(self):
        return {
            'name': 'Reason for cancellation',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'cancellation.popup',
            'target': 'new',
        }
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals["name"] = (
                self.env["ir.sequence"].next_by_code("work.order.seq.name")
            ) or _("New")
        return super().create(vals_list)
    
    
class CancellationPopup(models.TransientModel):
    _name = 'cancellation.popup'
    _description = 'Cancellation Popup'

    reason = fields.Text(string="Reason for cancellation")

    def confirm_cancel(self):
        work_order_id = self.env.context.get('active_id')
        work_order = self.env['work.order'].browse(work_order_id)
        if not work_order:
            raise UserError("Work Order not found!")
        
        
        work_order.state = 'cancel'
        
        if work_order.notes:
            work_order.notes += "\nCancellation Reason: " + self.reason
        else:
            work_order.notes = "Cancellation Reason: " + self.reason

        return {'type': 'ir.actions.act_window_close'}
