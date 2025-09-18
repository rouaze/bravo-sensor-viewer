from .feature import Feature


class X2202(Feature):
    feature_id = 0x2202

    def get_sensor_dpi_parameters(self, sendor_id=0):
        res = self.construct_and_process_request(5, [sendor_id])
        if res:
            return [
                res.params[1] << 8 | res.params[2],
                res.params[5] << 8 | res.params[6],
                res.params[9],
            ]

    def set_sensor_dpi_parameters(self, sensor_id, dpi_x, dpi_y, lod):
        self.construct_and_process_request(
            6,
            [
                sensor_id,
                dpi_x >> 8 & 0xFF,
                dpi_x & 0xFF,
                dpi_y >> 8 & 0xFF,
                dpi_y & 0xFF,
                lod,
            ],
        )
