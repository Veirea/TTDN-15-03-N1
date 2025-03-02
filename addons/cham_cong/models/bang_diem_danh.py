from odoo import models, fields, api
from odoo.exceptions import ValidationError

class BangDiemDanh(models.Model):
    _name = 'bang_diem_danh'
    _description = 'Bảng Điểm Danh Nhân Viên'

    nhan_vien_id = fields.Many2one('nhan_vien', string='Nhân viên')

    ngay_lam_viec = fields.Date('Ngày làm việc', required=True)
    gio_check_in = fields.Datetime('Giờ Check-in')
    gio_check_out = fields.Datetime('Giờ Check-out')
    trang_thai = fields.Selection([
        ('dang_lam', 'Đang làm việc'),
        ('da_check_out', 'Đã hoàn thành'),
        ('vang', 'Vắng mặt')
    ], string='Trạng thái', default='dang_lam')

    @api.constrains('gio_check_in', 'gio_check_out')
    def _kiem_tra_thoi_gian(self):
        for rec in self:
            if rec.gio_check_in and rec.gio_check_out and rec.gio_check_in > rec.gio_check_out:
                raise ValidationError('Giờ check-out phải sau giờ check-in!')

    def action_check_in(self):
        self.gio_check_in = fields.Datetime.now()
        self.trang_thai = 'dang_lam'
    
    def action_check_out(self):
        self.gio_check_out = fields.Datetime.now()
        self.trang_thai = 'da_check_out'