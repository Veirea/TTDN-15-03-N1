from odoo import models, fields, api
from odoo.exceptions import ValidationError

class BaoCao(models.Model):
    _name = 'bao_cao'
    _description = 'Báo Cáo Bảng Công'

    nhan_vien_id = fields.Many2one("nhan_vien", string="Nhân Viên")
    thang = fields.Selection([(str(num), f'Tháng {num}') for num in range(1, 13)], string='Tháng', required=True)
    nam = fields.Integer('Năm', required=True, default=lambda self: fields.Date.today().year)
    tong_gio_lam = fields.Float('Tổng Giờ Làm', compute='_compute_tong_gio_lam', store=True)
    so_lan_di_muon = fields.Integer('Số Lần Đi Muộn', compute='_compute_thong_ke', store=True)
    so_lan_ve_som = fields.Integer('Số Lần Về Sớm', compute='_compute_thong_ke', store=True)
    so_nhan_vien_dang_ky = fields.Integer(string='Số Nhân Viên Đăng Ký', compute='_compute_so_nhan_vien_dang_ky', store=True)
    so_don_xin_phep = fields.Integer(string='Số Đơn Xin Phép', compute='_compute_so_don_xin_phep',  store=True)

    @api.depends('thang', 'nam')
    def _compute_tong_gio_lam(self):
        for rec in self:
            if not rec.thang:
                rec.tong_gio_lam = 0
                continue
                
            records = self.env['bang_diem_danh'].search([
                ('ngay_lam_viec', '>=', f'{rec.nam}-{int(rec.thang):02d}-01'),
                ('ngay_lam_viec', '<', f'{rec.nam}-{int(rec.thang)+1 if int(rec.thang) < 12 else 1:02d}-01')
            ])
            rec.tong_gio_lam = sum([(r.gio_check_out - r.gio_check_in).total_seconds() / 3600 for r in records if r.gio_check_in and r.gio_check_out])
    
    @api.depends('thang', 'nam')
    def _compute_so_nhan_vien_dang_ky(self):
        for rec in self:
            if not rec.thang:
                rec.so_nhan_vien_dang_ky = 0
                continue

            records = self.env['lich_lam_viec'].search([
                ('ngay_lam_viec', '>=', f'{rec.nam}-{int(rec.thang):02d}-01'),
                ('ngay_lam_viec', '<', f'{rec.nam}-{int(rec.thang) + 1 if int(rec.thang) < 12 else 1:02d}-01')
            ])
            rec.so_nhan_vien_dang_ky = len(set(records.mapped('nhan_vien_id.id')))
    
    @api.depends('thang', 'nam')
    def _compute_so_don_xin_phep(self):
        for rec in self:
            if not rec.thang:
                rec.so_don_xin_phep = 0
                continue

            records = self.env['don_xin_phep'].search([
                ('ngay_bat_dau', '>=', f'{rec.nam}-{int(rec.thang):02d}-01'),
                ('ngay_bat_dau', '<', f'{rec.nam}-{int(rec.thang) + 1 if int(rec.thang) < 12 else 1:02d}-01'),
                ('trang_thai', '=', 'duyet')
            ])
            rec.so_don_xin_phep = len(records)