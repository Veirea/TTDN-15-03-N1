from odoo import models, fields, api
from odoo.exceptions import ValidationError

class BaoCao(models.Model):
    _name = 'bao_cao'
    _description = 'Báo Cáo Thời Gian Làm Việc'

    nhan_vien_id = fields.Many2one('nhan_vien', string='Nhân viên')

    thang = fields.Selection([(str(num), f'Tháng {num}') for num in range(1, 13)], string='Tháng', required=True)
    nam = fields.Integer('Năm', required=True, default=lambda self: fields.Date.today().year)
    tong_gio_lam = fields.Float('Tổng Giờ Làm', compute='_compute_tong_gio_lam', store=True)
    so_lan_di_muon = fields.Integer('Số Lần Đi Muộn', compute='_compute_thong_ke', store=True)
    so_lan_ve_som = fields.Integer('Số Lần Về Sớm', compute='_compute_thong_ke', store=True)

    @api.depends('nhan_vien_id', 'thang', 'nam')
    def _compute_tong_gio_lam(self):
        for rec in self:
            records = self.env['bang_diem_danh'].search([
                ('nhan_vien_id', '=', rec.nhan_vien_id.id),
                ('ngay_lam_viec', '>=', f'{rec.nam}-{rec.thang}-01'),
                ('ngay_lam_viec', '<', f'{rec.nam}-{int(rec.thang)+1}-01')
            ])
            rec.tong_gio_lam = sum([(r.gio_check_out - r.gio_check_in).total_seconds() / 3600 for r in records if r.gio_check_in and r.gio_check_out])

    @api.depends('nhan_vien_id', 'thang', 'nam')
    def _compute_thong_ke(self):
        for rec in self:
            records = self.env['bang_diem_danh'].search([
                ('nhan_vien_id', '=', rec.nhan_vien_id.id),
                ('ngay_lam_viec', '>=', f'{rec.nam}-{rec.thang}-01'),
                ('ngay_lam_viec', '<', f'{rec.nam}-{int(rec.thang)+1}-01')
            ])
            rec.so_lan_di_muon = sum(1 for r in records if r.gio_check_in and r.gio_check_in.hour > 8)  # Giả sử giờ chuẩn là 8h
            rec.so_lan_ve_som = sum(1 for r in records if r.gio_check_out and r.gio_check_out.hour < 17)  # Giả sử kết thúc là 17h
