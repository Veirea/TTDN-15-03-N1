from odoo import models, fields, api
from odoo.exceptions import ValidationError

class LichLamViec(models.Model):
    _name = 'lich_lam_viec'
    _description = 'Lịch Đăng Ký Làm Việc'

    nhan_vien_id = fields.Many2one('nhan_vien', string='Nhân viên')

    ngay_lam_viec = fields.Date('Ngày làm Việc', required=True)

    ca_lam_viec = fields.Selection([
        ('sang', 'Ca Sáng'),
        ('chieu', 'Ca Chiều'),
        ('toi', 'Ca Tối')
    ], string='Ca Làm Việc', required=True)

    trang_thai = fields.Selection([
        ('cho_xac_nhan', 'Chờ xác nhận'),
        ('da_xac_nhan', 'Đã xác nhận'),
        ('huy', 'Hủy')
    ], string='Trạng thái', default='cho_xac_nhan')

    



    