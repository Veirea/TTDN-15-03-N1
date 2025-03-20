from odoo import models, fields, api
from datetime import datetime, timedelta, time

class DiemDanh(models.Model):
    _name = 'diem_danh'
    _description = 'Bảng Điểm Danh'

    nhan_vien_id = fields.Many2one('nhan_vien', string="Nhân Viên")
    ma_dinh_danh = fields.Char(related='nhan_vien_id.ma_dinh_danh', string="Mã Định Danh", store=True, readonly=True)
    ngay_lam_viec = fields.Date('Ngày Làm Việc', required=True, default=fields.Date.context_today)
    gio_check_in = fields.Datetime('Giờ Check-in')
    gio_check_out = fields.Datetime('Giờ Check-out')
    tong_gio_lam = fields.Float('Tổng Giờ Làm', compute='_compute_tong_gio_lam', store=True)
    lich_lam_viec_id = fields.Many2one('lich_lam_viec', string="Lịch Làm Việc", domain="[('nhan_vien_id', '=', nhan_vien_id), ('ngay_lam_viec', '=', ngay_lam_viec)]")
    ca_lam_viec = fields.Selection(related='lich_lam_viec_id.ca_lam_viec', string="Ca Làm Việc", store=True)

    trang_thai_cham_cong = fields.Selection([
        ('dung_gio', 'Đúng Giờ'),
        ('muon', 'Muộn'),
        ('som', 'Sớm'),
    ], string="Trạng Thái Chấm Công", compute='_compute_trang_thai_cham_cong', store=True)

    @api.depends('gio_check_in', 'lich_lam_viec_id.gio_bat_dau')
    def _compute_trang_thai_cham_cong(self):
        for rec in self:
            if rec.gio_check_in and rec.lich_lam_viec_id and rec.lich_lam_viec_id.gio_bat_dau:
                gio_check_in_thuc_te = rec.gio_check_in.time()

                
                if isinstance(rec.lich_lam_viec_id.gio_bat_dau, float):
                    gio_bat_dau_hours = int(rec.lich_lam_viec_id.gio_bat_dau)
                    gio_bat_dau_minutes = int((rec.lich_lam_viec_id.gio_bat_dau - gio_bat_dau_hours) * 60)
                    gio_bat_dau = time(hour=gio_bat_dau_hours, minute=gio_bat_dau_minutes)
                else:
                    gio_bat_dau = rec.lich_lam_viec_id.gio_bat_dau

                if gio_check_in_thuc_te > gio_bat_dau:
                    rec.trang_thai_cham_cong = 'muon'
                elif gio_check_in_thuc_te == gio_bat_dau:
                    rec.trang_thai_cham_cong = 'dung_gio'
                else:
                    rec.trang_thai_cham_cong = 'som'
            else:
                rec.trang_thai_cham_cong = False


    @api.onchange('lich_lam_viec_id')
    def _onchange_lich_lam_viec(self):
        if self.lich_lam_viec_id:
            if isinstance(self.lich_lam_viec_id.gio_bat_dau, float):
                gio_bat_dau_hours = int(self.lich_lam_viec_id.gio_bat_dau)
                gio_bat_dau_minutes = int((self.lich_lam_viec_id.gio_bat_dau - gio_bat_dau_hours) * 60)
                self.gio_check_in = datetime.combine(self.ngay_lam_viec, time(hour=gio_bat_dau_hours, minute=gio_bat_dau_minutes))
            else:
                self.gio_check_in = self.lich_lam_viec_id.gio_bat_dau

            if isinstance(self.lich_lam_viec_id.gio_ket_thuc, float):
                gio_ket_thuc_hours = int(self.lich_lam_viec_id.gio_ket_thuc)
                gio_ket_thuc_minutes = int((self.lich_lam_viec_id.gio_ket_thuc - gio_ket_thuc_hours) * 60)
                self.gio_check_out = datetime.combine(self.ngay_lam_viec, time(hour=gio_ket_thuc_hours, minute=gio_ket_thuc_minutes))
            else:
                self.gio_check_out = self.lich_lam_viec_id.gio_ket_thuc

    @api.depends('gio_check_in', 'gio_check_out')
    def _compute_tong_gio_lam(self):
        for rec in self:
            if rec.gio_check_in and rec.gio_check_out:
                duration = rec.gio_check_out - rec.gio_check_in
                rec.tong_gio_lam = duration.total_seconds() / 3600
            else:
                rec.tong_gio_lam = 0

    @api.model
    def update_diem_danh(self):
        today = fields.Date.today()
        ds_don_nghi_phep = self.env['yeu_cau_nghi_phep'].search([('trang_thai', '=', 'da_duyet')])
    
        for don in ds_don_nghi_phep:
            ngay_hien_tai = don.ngay_bat_dau
            while ngay_hien_tai <= don.ngay_ket_thuc:
                diem_danh = self.env['diem_danh'].search([
                    ('nhan_vien_id', '=', don.nhan_vien_id.id),
                    ('ngay_lam_viec', '=', ngay_hien_tai)
                ], limit=1)

                if diem_danh:
                    diem_danh.trang_thai_cham_cong = 'co_phep'
                else:
                    self.env['diem_danh'].create({
                        'nhan_vien_id': don.nhan_vien_id.id,
                        'ngay_lam_viec': ngay_hien_tai,
                        'trang_thai_cham_cong': 'co_phep'
                    })

                ngay_hien_tai += timedelta(days=1)
