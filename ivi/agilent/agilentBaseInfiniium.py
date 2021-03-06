"""

Python Interchangeable Virtual Instrument Library

Copyright (c) 2012-2016 Alex Forencich

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

"""

from .agilentBaseScope import *

AcquisitionModeMapping = {
        'etim': ('normal', 'equivalent_time'),
        'rtim': ('normal', 'real_time'),
        'pdet': ('peak_detect', 'real_time'),
        'hres': ('high_resolution', 'real_time'),
        'segm': ('normal', 'segmented'),
        'segp': ('peak_detect', 'segmented'),
        'segh': ('high_resolution', 'segmented')
}
AcquisitionType = set(['normal', 'peak_detect', 'high_resolution'])
VerticalCoupling = set(['dc'])
ScreenshotImageFormatMapping = {
        'tif': 'tif',
        'tiff': 'tif',
        'bmp': 'bmp',
        'bmp24': 'bmp',
        'png': 'png',
        'png24': 'png',
        'jpg': 'jpg',
        'jpeg': 'jpg',
        'gif': 'gif'}
SampleMode = set(['real_time', 'equivalent_time', 'segmented'])
TimebaseReferenceMapping = {
        'left': 'left',
        'center': 'cent',
        'right': 'righ',
        'percent': 'perc'}

class agilentBaseInfiniium(agilentBaseScope):
    "Agilent Infiniium series IVI oscilloscope driver"

    def __init__(self, *args, **kwargs):
        self.__dict__.setdefault('_instrument_id', '')
        self._analog_channel_name = list()
        self._analog_channel_count = 4
        self._digital_channel_name = list()
        self._digital_channel_count = 16
        self._channel_count = self._analog_channel_count + self._digital_channel_count
        self._channel_common_mode = list()
        self._channel_differential = list()
        self._channel_differential_skew = list()
        self._channel_display_auto = list()
        self._channel_display_offset = list()
        self._channel_display_range = list()
        self._channel_display_scale = list()

        super(agilentBaseInfiniium, self).__init__(*args, **kwargs)

        self._analog_channel_name = list()
        self._analog_channel_count = 4
        self._digital_channel_name = list()
        self._digital_channel_count = 16
        self._channel_count = self._analog_channel_count + self._digital_channel_count
        self._bandwidth = 13e9

        self._horizontal_divisions = 10
        self._vertical_divisions = 8

        self._display_screenshot_image_format_mapping = ScreenshotImageFormatMapping
        self._display_color_grade = False

        self._identity_description = "Agilent Infiniium series IVI oscilloscope driver"
        self._identity_supported_instrument_models = ['MSO9104A', 'MSO9064A','DSO90254A',
                'DSO90404A','DSO90604A', 'DSO90804A','DSO91204A','DSO91304A','DSOX91304A',
                'DSOX91604A','DSOX92004A', 'DSOX92504A','DSOX92804A','DSOX93204A','DSA90254A',
                'DSA90404A','DSA90604A', 'DSA90804A','DSA91204A','DSA91304A','DSAX91304A',
                'DSAX91604A','DSAX92004A', 'DSAX92504A','DSAX92804A','DSAX93204A','MSOX91304A',
                'MSOX91604A','MSOX92004A', 'MSOX92504A','MSOX92804A','MSOX93204A']

        self._add_property('display.color_grade',
                        self._get_display_color_grade,
                        self._set_display_color_grade,
                        None,
                        ivi.Doc("""
                        Controls color grade persistance.

                        When in the color grade persistance mode, all waveforms are mapped into a
                        database and shown with different colors representing varying number of
                        hits in a pixel.  Vector display mode is disabled when color grade is
                        enabled.
                        """))
        self._add_method('display.fetch_color_grade_levels',
                        self._fetch_display_color_grade_levels,
                        ivi.Doc("""
                        Returns the range of hits represented by each color.  Fourteen values are
                        returned, representing the minimum and maximum count for each of seven
                        colors.  The values are returned in the following order:

                        * White minimum value
                        * White maximum value
                        * Yellow minimum value
                        * Yellow maximum value
                        * Orange minimum value
                        * Orange maximum value
                        * Red minimum value
                        * Red maximum value
                        * Pink minimum value
                        * Pink maximum value
                        * Blue minimum value
                        * Blue maximum value
                        * Green minimum value
                        * Green maximum value
                        """))
        self._add_property('acquisition.averaging_enabled',
                        self._get_acquisition_averaging_enabled,
                        self._set_acquisition_averaging_enabled,
                        None,
                        ivi.Doc("""
                        The acquisition averaging control allows Infiniium to acquire 
                        waveform data from several acquisitions and then average them all together. 
                        When enabled, the channel data is averaged before being displayed.
                        """))
        self._init_channels()


    def _utility_error_query(self):
        error_code = 0
        error_message = "No error"
        if not self._driver_operation_simulate:
            error_code = self._ask(":system:error?")
            error_code = int(error_code)
            if error_code != 0:
                error_message = "Unknown"
        return (error_code, error_message)

    def _init_channels(self):
        try:
            super(agilentBaseInfiniium, self)._init_channels()
        except AttributeError:
            pass

        # currently no additional parameters


    def _display_fetch_screenshot(self, format='png', invert=False):
        if self._driver_operation_simulate:
            return b''

        if format not in self._display_screenshot_image_format_mapping:
            raise ivi.ValueNotSupportedException()

        format = self._display_screenshot_image_format_mapping[format]

        self._write(":display:data? %s, screen, on, %s" % (format, 'invert' if invert else 'normal'))

        return self._read_ieee_block()

    def _get_display_vectors(self):
        if not self._driver_operation_simulate and not self._get_cache_valid():
            self._display_vectors = bool(int(self._ask(":display:connect?")))
            self._set_cache_valid()
        return self._display_vectors

    def _set_display_vectors(self, value):
        value = bool(value)
        if not self._driver_operation_simulate:
            self._write(":display:connect %d" % int(value))
        self._display_vectors = value
        self._set_cache_valid()

    def _get_display_color_grade(self):
        if not self._driver_operation_simulate and not self._get_cache_valid():
            self._display_color_grade = bool(int(self._ask(":display:cgrade?")))
            self._set_cache_valid()
        return self._display_color_grade

    def _set_display_color_grade(self, value):
        value = bool(value)
        if not self._driver_operation_simulate:
            self._write(":display:cgrade %d" % int(value))
        self._display_color_grade = value
        self._set_cache_valid()

    def _fetch_display_color_grade_levels(self):
        if self._driver_operation_simulate():
            return [0]*14

        lst = self._ask(":display:cgrade:levels?").split(',')
        return [int(x) for x in lst]

    def _get_channel_coupling(self, index):
        index = ivi.get_index(self._analog_channel_name, index)
        if not self._driver_operation_simulate and not self._get_cache_valid(index=index):
            self._channel_coupling[index] = self._ask(":%s:input?" % self._channel_name[index]).lower()
            self._set_cache_valid(index=index)
        return self._channel_coupling[index]

    def _set_channel_coupling(self, index, value):
        index = ivi.get_index(self._analog_channel_name, index)
        if value not in VerticalCoupling:
            raise ivi.ValueNotSupportedException()
        if not self._driver_operation_simulate:
            self._write(":%s:input %s" % (self._channel_name[index], value))
        self._channel_coupling[index] = value
        self._set_cache_valid(index=index)

    def _get_channel_input_impedance(self, index):
        index = ivi.get_index(self._analog_channel_name, index)
        if not self._driver_operation_simulate and not self._get_cache_valid(index=index):
            val = self._ask(":%s:input?" % self._channel_name[index]).lower()
            if val == 'dc':
                val == '1M'
            elif val == 'DC50':
                val == '50'
            elif val == 'AC':
                val == '1M'
            self._channel_coupling[index] = val
            self._set_cache_valid(index=index)
        return self._channel_input_impedance[index]

    def _set_channel_input_impedance(self, index, value):
        value = float(value)
        index = ivi.get_index(self._analog_channel_name, index)
        if value != 50:
            raise Exception('Invalid impedance selection')
        self._channel_input_impedance[index] = value
        self._set_cache_valid(index=index)

    def _get_timebase_reference(self):
        if not self._driver_operation_simulate and not self._get_cache_valid():
            value = self._ask(":timebase:reference?").lower()
            self._timebase_reference = [k for k,v in TimebaseReferenceMapping.items() if v==value][0]
            if self._timebase_reference == 'percent':
                self._timebase_reference = float(self._ask(":timebase:reference:percent?"))
            self._set_cache_valid()
        return self._timebase_reference

    def _get_trigger_coupling(self):
        if not self._driver_operation_simulate and not self._get_cache_valid():
            self._trigger_coupling = self._ask(":trigger:edge:coupling?")
        return self._trigger_coupling

    def _set_trigger_coupling(self, value):
        if value not in TriggerCouplingMapping:
            raise ivi.ValueNotSupportedException()
        if not self._driver_operation_simulate:
            self._write(":trigger:edge:coupling %s" % value)
        self._trigger_coupling = value
        self._set_cache_valid()

    def _get_trigger_source(self):
        if not self._driver_operation_simulate and not self._get_cache_valid():
            value = self._ask(":trigger:edge:source?").lower()
            # TODO process value
            self._trigger_source = value
            self._set_cache_valid()
        return self._trigger_source

    def _set_trigger_source(self, value):
        if hasattr(value, 'name'):
            value = value.name
        value = str(value)
        # if value not in self._channel_name:
        #     raise ivi.UnknownPhysicalNameException()
        if not self._driver_operation_simulate:
            self._write(":trigger:edge:source %s" % value)
        self._trigger_source = value
        self._set_cache_valid()

    def _get_trigger_type(self):
        if not self._driver_operation_simulate and not self._get_cache_valid():
            value = self._ask(":trigger:mode?").lower()
            self._trigger_type = value
            self._set_cache_valid()
        return self._trigger_type

    def _set_trigger_type(self, value):
        if value not in TriggerTypeMapping:
            raise ivi.ValueNotSupportedException()
        if not self._driver_operation_simulate:
            self._write(":trigger:mode %s" % TriggerTypeMapping[value])
            if value == 'ac_line':
                self._write(":trigger:source line")
            if value == 'glitch':
                qual = self._ask(":trigger:glitch:qualifier?").lower()
                if qual not in GlitchConditionMapping.values():
                    self._write(":trigger:glitch:qualifier %s" % GlitchConditionMapping[self._trigger_glitch_condition])
            if value == 'width':
                self._write(":trigger:glitch:qualifier range")
        self._trigger_type = value
        self._set_cache_valid()

    def _get_acquisition_averaging_enabled(self):
        if not self._driver_operation_simulate:
            value = self._ask(":acquire:average?")
            self._acquisition_averaging_enabled = value
        return self._acquisition_averaging_enabled

    def _set_acquisition_averaging_enabled(self, value):
        if not self._driver_operation_simulate:
            self._write(":acquire:average %s" % value)
            self._acquisition_averaging_enabled = value

    def _get_acquisition_number_of_averages(self):
        if not self._driver_operation_simulate and not self._get_cache_valid():
            self._acquisition_number_of_averages = int(self._ask(":acquire:average:count?"))
            self._set_cache_valid()
        return self._acquisition_number_of_averages

    def _set_acquisition_number_of_averages(self, value):
        if value < 1 or value > 65536:
            raise ivi.OutOfRangeException()
        if not self._driver_operation_simulate:
            self._write(":acquire:average:count %d" % value)
        self._acquisition_number_of_averages = value
        self._set_cache_valid()

    def _measurement_fetch_waveform(self, index):
        index = ivi.get_index(self._channel_name, index)

        if self._driver_operation_simulate:
            return list()

        if sys.byteorder == 'little':
            self._write(":waveform:byteorder lsbfirst")
        else:
            self._write(":waveform:byteorder msbfirst")
        self._write(":waveform:format word")
        self._write(":waveform:source %s" % self._channel_name[index])

        # Read preamble

        pre = self._ask(":waveform:preamble?").split(',')

        format = int(pre[0])
        type = int(pre[1])
        points = int(pre[2])
        count = int(pre[3])
        xincrement = float(pre[4])
        xorigin = float(pre[5])
        xreference = int(float(pre[6]))
        yincrement = float(pre[7])
        yorigin = float(pre[8])
        yreference = int(float(pre[9]))

        #if type == 1:
        #    raise scope.InvalidAcquisitionTypeException()

        if format != 2:
            raise UnexpectedResponseException()

        # Read waveform data
        raw_data = self._ask_for_ieee_block(":waveform:data?")

        # Split out points and convert to time and voltage pairs
        y_data = array.array('h', raw_data[0:points*2])

        data = [(((i - xreference) * xincrement) + xorigin, float('nan') if y == 31232 else ((y - yreference) * yincrement) + yorigin) for i, y in enumerate(y_data)]

        return data

    def _measurement_read_waveform(self, index, maximum_time):
        return self._measurement_fetch_waveform(index)

    def _measurement_initiate(self):
        if not self._driver_operation_simulate:
            self._write(":acquire:complete 100")
            self._write(":digitize")
            self._set_cache_valid(False, 'trigger_continuous')

    def _get_acquisition_mode(self):
        if not self._driver_operation_simulate and not self._get_cache_valid():
            value = self._ask(":acquire:mode?").lower()
            t = AcquisitionModeMapping[value]
            self._acquisition_type = t[0]
            self._acquisition_sample_mode = t[1]
            self._set_cache_valid()
            self._set_cache_valid(True, 'acquisition_sample_mode')
            self._set_cache_valid(True, 'acquisition_type')

    def _set_acquisition_mode(self, t, value):
        f1 = None
        f2 = None

        if t == 'type':
            f1 = [k for k,v in AcquisitionModeMapping.items() if v[0] == value]
            f2 = [k for k,v in AcquisitionModeMapping.items() if v[1] == self._acquisition_sample_mode and k in f1]
        elif t == 'mode':
            f1 = [k for k,v in AcquisitionModeMapping.items() if v[1] == value]
            f2 = [k for k,v in AcquisitionModeMapping.items() if v[0] == self._acquisition_type and k in f1]

        if len(f2):
            v = f2[0]
        else:
            v = f1[0]
        t = AcquisitionModeMapping[v]
        if not self._driver_operation_simulate:
            self._write(":acquire:mode %s" % v)
        self._acquisition_type = t[0]
        self._acquisition_sample_mode = t[1]
        self._set_cache_valid()
        self._set_cache_valid(True, 'acquisition_sample_mode')
        self._set_cache_valid(True, 'acquisition_type')

    def _get_acquisition_type(self):
        self._get_acquisition_mode()
        return self._acquisition_type

    def _set_acquisition_type(self, value):
        if value not in AcquisitionType:
            raise ivi.ValueNotSupportedException()
        self._set_acquisition_mode('type', value)

    def _get_acquisition_sample_mode(self):
        self._get_acquisition_mode()
        return self._acquisition_sample_mode

    def _set_acquisition_sample_mode(self, value):
        if value not in SampleMode:
            raise ivi.ValueNotSupportedException()
        self._set_acquisition_mode('mode', value)

    def _get_acquisition_number_of_points_minimum(self):
        if not self._driver_operation_simulate and not self._get_cache_valid():
            self._acquisition_number_of_points_minimum = int(self._ask(":ACQuire:POINts:ANALog?"))
        return self._acquisition_number_of_points_minimum

    def _set_acquisition_number_of_points_minimum(self, value):
        if not self._driver_operation_simulate:
            self._write(":ACQuire:POINts:ANALog %s" % value)
        self._acquisition_number_of_points_minimum = value
        self._set_cache_valid()