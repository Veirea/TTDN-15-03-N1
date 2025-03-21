from odoo import models, fields, api
from datetime import date
from odoo.exceptions import ValidationError

class YeuCauNghiPhep(models.Model):
    _name = "yeu_cau_nghi_phep"
    _description = "Yêu cầu nghỉ phép"

    nhan_vien_id = fields.Many2one("nhan_vien", string="Nhân viên")
    ma_dinh_danh = fields.Char(related='nhan_vien_id.ma_dinh_danh', string="Mã Định Danh", readonly=True)
    so_dien_thoai = fields.Char(related='nhan_vien_id.so_dien_thoai', string="Số Điện Thoại", readonly=True)
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
        ("nghi_phep", "Nghỉ phép năm"),
        ("nghi_om", "Nghỉ Ốm"),
        ("nghi_co_luong", "Nghỉ phép có lương"),
        ("nghi_dac_biet", "Nghỉ phép đặc biệt"),
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

    @api.constrains('nhan_vien_id', 'so_ngay_nghi', 'loai_nghi_phep')
    def _check_nghi_phep(self):
        for record in self:
            hop_dong = self.env['hop_dong'].search([('nhan_vien_id', '=', record.nhan_vien_id.id)], limit=1)
            if hop_dong:
                max_days = 0
                if record.loai_nghi_phep == 'nghi_phep':
                    max_days = hop_dong.ngay_nghi_phep_toi_da
                elif record.loai_nghi_phep == 'nghi_om':
                    max_days = hop_dong.so_ngay_nghi_om
                elif record.loai_nghi_phep == 'nghi_co_luong':
                    max_days = hop_dong.ngay_nghi_co_luong
                elif record.loai_nghi_phep == 'nghi_dac_biet':
                    max_days = hop_dong.nghi_phep_dac_biet
                
                if record.so_ngay_nghi > max_days:
                    raise ValidationError("Số ngày nghỉ %s không được vượt quá %s ngày." % (record.loai_nghi_phep, max_days))
                else:
                    # Tự động duyệt nếu đủ điều kiện
                    record.trang_thai = 'da_duyet'