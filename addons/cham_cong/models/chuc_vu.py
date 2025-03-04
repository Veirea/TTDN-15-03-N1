from odoo import models, fields

class ChucVu(models.Model):
    _name = 'chuc_vu'
    _description = 'Bảng chứa thông tin chức vụ'
    _rec_name ='ten_chuc_vu'

    ten_chuc_vu = fields.Char("Tên chức vụ", required=True)
    mo_ta = fields.Text("Mô tả chức vụ")
    nhan_vien_ids = fields.Many2many("nhan_vien", string="Nhân viên")
    