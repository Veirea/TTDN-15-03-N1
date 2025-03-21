from odoo import models, fields

class LuuFile(models.Model):
    _name = 'luu_file'
    _description = 'Lưu file'

    yeu_cau_nghi_phep_id = fields.Many2one('yeu_cau_nghi_phep',inverse_name ="luu_file_id", string="Yêu Cầu Nghỉ Phép", ondelete="cascade")
    lich_lam_viec_id = fields.Many2one('lich_lam_viec', inverse_name = "luu_file_id", string=" Lịch Làm Việc", ondelete="cascade")
    luu_file = fields.Binary("Tệp", attachment=True)  
    luu_file_name = fields.Char("Tên Tệp")  