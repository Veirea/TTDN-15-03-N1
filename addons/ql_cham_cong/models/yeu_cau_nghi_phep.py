from odoo import models, fields, api
from datetime import date
from odoo.exceptions import ValidationError

class YeuCauNghiPhep(models.Model):
    _name = "yeu_cau_nghi_phep"
    _description = "Yêu cầu nghỉ phép"

    nhan_vien_id = fields.Many2one("nhan_vien", string="Nhân viên")
    hop_dong_id = fields.Many2one('hop_dong', string='Hợp Đồng', compute='_compute_hop_dong', store=True)
    phong_ban_id = fields.Many2one('phong_ban', string='Phòng Ban', related='nhan_vien_id.phong_ban_id', store=True)
    chuc_vu_id = fields.Many2one('chuc_vu', string='Chức Vụ', related='nhan_vien_id.chuc_vu_id', store=True)
    luu_file_id = fields.One2many('luu_file', inverse_name ='yeu_cau_nghi_phep_id', string="File đính kèm")
    luu_file = fields.Binary("Tệp", attachment=True)
    luu_file_name = fields.Char("Tên Tệp")
    ngay_bat_dau = fields.Date(string="Ngày bắt đầu nghỉ", required=True)
    ngay_ket_thuc = fields.Date(string="Ngày kết thúc nghỉ", required=True)
    so_ngay_nghi = fields.Integer(string="Số ngày nghỉ", compute="_compute_so_ngay_nghi", store=True)
    trang_thai = fields.Selection([
        ("cho_duyet", "Chờ duyệt"),
        ("da_duyet", "Đã duyệt"),
        ("tu_choi", "Từ chối")
    ], string="Trạng thái", default="cho_duyet", required=True)

    loai_nghi_phep = fields.Selection([
        ("nghi_phep_nam", "Nghỉ phép năm"),
        ("nghi_om", "Nghỉ Ốm"),
        ("nghi_phep_dac_biet", "Nghỉ phép đặc biệt"),
        ("nghi_phep_khong_luong", "Nghỉ phép không lương"),
    ], string="Loại nghỉ phép", required=True)

    @api.depends("ngay_bat_dau", "ngay_ket_thuc")
    def _compute_so_ngay_nghi(self):
        for rec in self:
            if rec.ngay_bat_dau and rec.ngay_ket_thuc:
                rec.so_ngay_nghi = (rec.ngay_ket_thuc - rec.ngay_bat_dau).days + 1
            else:
                rec.so_ngay_nghi = 0

    @api.depends('nhan_vien_id')
    def _compute_hop_dong(self):
        for rec in self:
            hop_dong = self.env['hop_dong'].search([
                ('nhan_vien_id', '=', rec.nhan_vien_id.id),
                ('trang_thai', '=', 'active'),
            ], limit=1)
            rec.hop_dong_id = hop_dong.id if hop_dong else False

    @api.constrains('nhan_vien_id', 'hop_dong_id')
    def _check_hop_dong(self):
        for rec in self:
            hop_dong = self.env['hop_dong'].search([
                ('nhan_vien_id', '=', rec.nhan_vien_id.id),
                ('trang_thai', '=', 'active'),
            ], limit=1)
            if not hop_dong:
                raise ValidationError("Nhân viên này không có hợp đồng đang hoạt động!")

    @api.model
    def create(self, vals):
        """Tự động duyệt yêu cầu nghỉ phép nếu hợp đồng có điều khoản tự động duyệt"""
        record = super(YeuCauNghiPhep, self).create(vals)

        # Tìm hợp đồng sau khi đã tạo bản ghi
        hop_dong = self.env['hop_dong'].search([
            ('nhan_vien_id', '=', record.nhan_vien_id.id),
            ('trang_thai', '=', 'active'),
        ], limit=1)

        if hop_dong and hop_dong.tu_dong_duyet:
            record.write({'trang_thai': 'da_duyet'})  # Cập nhật trạng thái đã duyệt
    
        return record

    @api.model
    def tu_dong_duyet_nghi_phep(self):
        """Cron Job: Tự động duyệt các yêu cầu nghỉ phép nếu hợp đồng có điều khoản cho phép"""
        yeu_cau_phep = self.search([('trang_thai', '=', 'cho_duyet')])
    
        for yc in yeu_cau_phep:
            hop_dong = self.env['hop_dong'].search([
                ('nhan_vien_id', '=', yc.nhan_vien_id.id),
                ('trang_thai', '=', 'active'),
            ], limit=1)

            if hop_dong and hop_dong.tu_dong_duyet:
                yc.write({'trang_thai': 'da_duyet'})
