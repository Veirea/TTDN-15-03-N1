from odoo import models, fields

class HopDong(models.Model):
    _name = 'hop_dong'
    _description = 'Hợp Đồng'

    name = fields.Char(string='Tên Hợp Đồng', required=True)
    ngay_bat_dau = fields.Date(string='Ngày Bắt Đầu', required=True)
    ngay_ket_thuc = fields.Date(string='Ngày Kết Thúc', required=True)
    nhan_vien_id = fields.Many2one('nhan_vien', string='Nhân Viên')
    trang_thai = fields.Selection([
        ('active', 'Đang Hoạt Động'),
        ('expired', 'Hết Hạn'),
    ], string='Trạng Thái', default='active', required=True)
    tu_dong_duyet = fields.Boolean(string="Tự động duyệt nghỉ phép", default=False)
    ngay_nghi_phep_toi_da = fields.Integer(string="Số ngày nghỉ phép tối đa", default=12)
    so_ngay_nghi_om = fields.Integer(string="Số ngày nghỉ ốm tối đa", default=10)
    nghi_phep_dac_biet = fields.Integer(string="Số ngày nghỉ đặc biệt tối đa", default=3)
    ngay_nghi_co_luong = fields.Integer(string="Số ngày nghỉ có lương tối đa", default=5)
