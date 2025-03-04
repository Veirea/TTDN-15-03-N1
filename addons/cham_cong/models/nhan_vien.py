from odoo import models, fields, api
from odoo.exceptions import ValidationError


class NhanVien(models.Model):
    _name = 'nhan_vien'
    _description = 'Bảng chứa thông tin nhân viên'
    _rec_name = 'ma_dinh_danh'

    ma_dinh_danh = fields.Char("Mã định danh", required=True)
    ho_ten_dem = fields.Char("Họ Tên Đệm", required=True)
    ten = fields.Char("Tên", required=True)
    ho_va_ten = fields.Char("Họ Và Tên",  required=True)    
    ngay_sinh = fields.Date("Ngày sinh")
    que_quan = fields.Char("Quê quán")
    email = fields.Char("Email")
    so_dien_thoai = fields.Char("Số điện thoại")
    gioi_tinh = fields.Selection([
        ('Nam', 'Nam'),
        ('Nu', 'Nữ'),
        ('Khac', 'Khác'),
    ], string="Giới tính", default='...')

    chuc_vu_ids = fields.Many2many("chuc_vu", string="Chức Vụ")

    @api.depends("ho_ten_dem", "ten")
    def _compute_ho_va_ten(self):
        for record in self:
            if record.ho_ten_dem and record.ten:
                record.ho_va_ten = record.ho_ten_dem + ' ' + record.ten

    @api.onchange("ten", "ho_ten_dem")
    def _default_ma_dinh_danh(self):
        for record in self:
            if record.ho_ten_dem and  record.ten:
                chu_cai_đau = ' ' .join([tu[0][0] for tu in record.ho_ten_dem.lower().split()])
                record.ma_dinh_danh = record.ten.lower() + chu_cai_đau            
    
    
    @api.constrains('tuoi')
    def _check_tuoi(self):
        for record in self:
            if record.tuoi < 18:
                raise ValidationError("Tuổi Không Được Bé Hơn 18")
            
    _sql_constraints = [
        ('ma_dinh_danh_unique', 'unique(ma_dinh_danh)', 'Mã Định danh phải là duy nhất')
    ]