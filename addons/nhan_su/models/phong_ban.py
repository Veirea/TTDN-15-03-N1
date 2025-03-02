from odoo import models, fields, api


class PhongBan(models.Model):
    _name = 'phong_ban'
    _description = 'Bảng chứa thông tin nhân viên'

    ma_phong_ban = fields.Char("Mã định danh", required=True)
      