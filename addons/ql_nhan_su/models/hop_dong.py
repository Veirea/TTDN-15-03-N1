from odoo import models, fields

class HopDong(models.Model):
    _name = 'hop_dong'
    _description = 'Hợp Đồng'

    name = fields.Char(string='Tên Hợp Đồng', required=True)
    ngay_bat_dau = fields.Date(string='Ngày Bắt Đầu', required=True)
    ngay_ket_thuc = fields.Date(string='Ngày Kết Thúc', required=True)
    nhan_vien_id = fields.Many2one('', string='Nhân Viên')
    trang_thai = fields.Selection([
        ('active', 'Đang Hoạt Động'),
        ('expired', 'Hết Hạn'),
    ], string='Trạng Thái', default='active', required=True)
    tu_dong_duyet = fields.Boolean(string="Tự động duyệt nghỉ phép", default=False)