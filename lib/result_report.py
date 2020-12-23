class Report:
    def __init__(self, utc_time_func):
        """
        Class to realize results and its output
        :type utc_time_func: function object from DrumCorr to search value using UTCDateTime
        """
        self.get_time_value = utc_time_func

        self.current_file_name = None
        self.beats_count = None
        self.detection_value = None
        self.approx_xcorr = None
        self.max_xcorr_value = None
        self.max_xcorr_amplitude = None

        # anon functions
        self.stream = None
        self.detects = None
        self.sims = None
        self.times = None

    def report_head(self):
        out = '''DrumCorr File <{file}> result:\n
Beats count:\t\t\t{beats}
Detection value:\t\t{detect}
Average correlation:\t{xcorr}
Max corr:
    Value:\t\t{max_xcorr_val}
    Amplitude:\t{max_amp}(x1000 = {ap_max_amp})'''.format(file=self.current_file_name,
                                                          beats=len(self.detects),
                                                          detect=self.detection_value,
                                                          xcorr=self.approx_xcorr,
                                                          max_xcorr_val=self.max_xcorr_value,
                                                          max_amp=self.max_xcorr_amplitude,
                                                          ap_max_amp=round(self.max_xcorr_amplitude * 1000, 2)
                                                          )
        return out

    def report_print(self):
        print(self.report_head())

    def report_to_file(self, out_file_name):
        """
        Writing report to file
        :type out_file_name: name of output report file
        """
        time_format = "%Y-%m-%dT%H:%M:%SZ.%f"
        with open(out_file_name, 'w+') as f:
            #  export header with results
            f.write(self.report_head())

            # write space
            f.write('\n\n')

            #  out data
            for detect in self.detects:
                cur_time = detect['time'].datetime.strftime(time_format)
                f.write('{current_time}\t{sim:0.3f}\t{amp:0.4f}\n'.format(current_time=str(cur_time),
                                                                          sim=detect['similarity'],
                                                                          amp=self.get_time_value(
                                                                              stream=self.stream,
                                                                              utc_time=detect[
                                                                                  'time']) * 1000)
                        )

            f.close()

    def generate_report_name(self, report_format):
        return report_format.format(file_name=self.current_file_name)
