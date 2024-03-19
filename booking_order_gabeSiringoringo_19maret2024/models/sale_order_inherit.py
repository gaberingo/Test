from odoo import models, fields, api
from odoo.exceptions import UserError

default_MSG = "Team already has work order during that period on "


class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'
    
    is_booking_order = fields.Boolean()
    team = fields.Many2one(
        'service.team',
        string="Service Team",
    )
    team_leader = fields.Many2one(
        'res.users',
        string="Team Leader",
        
    )
    team_members = fields.Many2many(
        'res.users',
        string="Team Members",
    )
    booking_start_date = fields.Date(
        string="Booking Start Date",
    )
    booking_end_date = fields.Date(
        string="Booking End Date",
    )
    wo_count = fields.Integer(
        string="Work Order Count",
        compute="_compute_wo_count",
    )
    
    @api.onchange('team')
    def _onchange_team(self):
        if self.team:
            self.team_leader = self.team.team_leader
            self.team_members = self.team.team_members
        else:
            self.team_leader = False
            self.team_members = False
    
    def check_overlap(self):
        work_order_overlap = self.env['work.order'].search(
            [
                ('service_team', '=', self.team.id),
                ('team_lead','=',self.team_leader.id),
                ('planned_start','<=',self.booking_end_date),
                ('planned_end','>=',self.booking_start_date),
                ('state','not in',['cancel'])
            ],
        )
        return work_order_overlap
    
    def action_check_work_order(self):
        work_order_overlap = self.check_overlap()
        if work_order_overlap:
            raise UserError(f"{default_MSG}{work_order_overlap[0].bo_ref.name}")
        else:
            raise UserError(f"Team is available for booking")
    
    def action_confirm(self):
        if self.is_booking_order:
            overlap = self.check_overlap()
            if not overlap:
                self.env['work.order'].create(
                    {
                        'bo_ref': self.id,
                        'service_team': self.team.id,
                        'team_lead': self.team_leader.id,
                        'team_members': [(6,0,self.team_members.ids)],
                        'planned_start': self.booking_start_date,
                        'planned_end': self.booking_end_date,
                        'state': 'pending'
                    }
                )
            else:
                raise UserError(f"{default_MSG}{overlap[0].bo_ref.name}.Please book on another date.")
        return super(SaleOrderInherit, self).action_confirm()
    
    def action_view_work_order(self):
        return {
            'name': 'Work Order',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'work.order',
            'domain': [('bo_ref','=',self.id)],
            'context': {'default_bo_ref': self.id}
        }
        
    @api.depends('wo_count','team')
    def _compute_wo_count(self):
        for record in self:
            record.wo_count = self.env['work.order'].search_count([('bo_ref','=',record.id)])