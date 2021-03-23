class Calibrations:
    def __init__(self, chars_dict):
        self.src_chars_dict = chars_dict
        self.values = {'amplitude_multiplier': self.get_amplitude_multiplier()
                       }
        del self.src_chars_dict

    def get_amplitude_multiplier(self):
        return float(self.src_chars_dict['CHINFONEED'][7])
        # print(chars_dict)
