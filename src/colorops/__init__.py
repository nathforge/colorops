import math
import re


VERSION = (0, 1)

def version_string():
    return '.'.join(str(component) for component in VERSION)


class Color(object):
    def __init__(self):
        raise NotImplemented()
    
    @classmethod
    def from_rgb_color(cls, rgb_color):
        raise NotImplemented()
    
    def to_rgb_color(self):
        raise NotImplemented()
    
    def convert(self, other_color_cls):
        return other_color_cls.from_rgb_color(self.to_rgb_color())
    
    def adjust(self, **kwargs):
        return self.convert(YUVColor).adjust(**kwargs).convert(type(self))
    
    def relative_luminance(self):
        return self.convert(RGBColor).relative_luminance()
    
    def contrast_ratio(self, other):
        return self.convert(RGBColor).contrast_ratio(other)
    
    def contrast_color(self, *args, **kwargs):
        return self.convert(RGBColor).contrast_color(*args, **kwargs)


class RGBColor(Color):
    THREE_HEX_DIGIT_RE = re.compile(r'^(?i)#?([0-9a-f])([0-9a-f])([0-9a-f])$')
    SIX_HEX_DIGIT_RE = re.compile(r'^(?i)#?([0-9a-f]{2})([0-9a-f]{2})([0-9a-f]{2})$')
    CSS_RGB_INT_RE = re.compile(r'^(?i)rgb\s*\((\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)$')
    CSS_RGB_PERCENT_RE = re.compile(r'^(?i)rgb\s*\((0|\d+%)\s*,\s*(0|\d+%)\s*,\s*(0|\d+%)\s*\)$')
    
    def __init__(self, value):
        if isinstance(value, int):
            self.rgb = self.rgb_tuple_from_int(value)
        elif isinstance(value, basestring):
            self.rgb = self.rgb_tuple_from_string(value)
        elif isinstance(value, RGBColor):
            self.rgb = value.rgb
        elif isinstance(value, Color):
            self.rgb = value.convert(RGBColor).rgb
        else:
            self.rgb = value
    
    def __repr__(self):
        return 'RGBColor((0x%02x, 0x%02x, 0x%02x))' % (self.r, self.g, self.b,)
    
    def __str__(self):
        return '%02X%02X%02X' % (self.r, self.g, self.b,)
    
    def __setattr__(self, name, value):
        if name in ('r', 'g', 'b'):
            value = int(value)
            if not 0x00 <= value <= 0xFF:
                raise ValueError('%s must be in the 0x00 to 0xFF range' % (name,))
        super(RGBColor, self).__setattr__(name, value)
    
    def get_rgb(self):
        return (self.r, self.g, self.b)
    
    def set_rgb(self, (r, g, b)):
        self.r, self.g, self.b = r, g, b
    
    rgb = property(get_rgb, set_rgb)
    
    def relative_luminance(self):
        """
        Calculate our relative luminance.
        <http://www.w3.org/TR/WCAG20/#relativeluminancedef>
        """
        
        srgb_r = self.r / 255.0
        srgb_g = self.g / 255.0
        srgb_b = self.b / 255.0
        
        r = srgb_r / 12.92 if srgb_r <= 0.03928 else ((srgb_r + 0.055) / 1.055) ** 2.4
        g = srgb_g / 12.92 if srgb_g <= 0.03928 else ((srgb_g + 0.055) / 1.055) ** 2.4
        b = srgb_b / 12.92 if srgb_b <= 0.03928 else ((srgb_b + 0.055) / 1.055) ** 2.4
        
        l = (0.2126 * r) + (0.7152 * g) + (0.0722 * b)
        
        return l
    
    def contrast_ratio(self, other):
        """
        Calculate contrast ratio between ourselves and another color.
        <http://www.w3.org/TR/WCAG20/#contrast-ratiodef>
        """
        
        if not isinstance(other, RGBColor):
            other = RGBColor(other)
        
        l = self.relative_luminance()
        other_l = other.relative_luminance()
        
        light_l = max(l, other_l)
        dark_l = min(l, other_l)
        
        return (light_l + 0.05) / (dark_l + 0.05)
    
    def contrast_color(self, colors=(0x000000, 0xFFFFFF)):
        """
        Find the color with the greatest contrast to ourselves.
        Can determine the best text color for a given background.
        
        Black and white:
            >>> print RGBColor('#FFFFFF').contrast_color(('#000000', '#FFFFFF'))
            000000
            >>> print RGBColor('#000000').contrast_color(('#000000', '#FFFFFF'))
            FFFFFF
        
        Full-intensity red, green and blue:
            >>> print RGBColor('#FF0000').contrast_color(('#000000', '#FFFFFF'))
            000000
            >>> print RGBColor('#00FF00').contrast_color(('#000000', '#FFFFFF'))
            000000
            >>> print RGBColor('#0000FF').contrast_color(('#000000', '#FFFFFF'))
            FFFFFF
        """
        
        if len(colors) < 1:
            raise ValueError('Expected at least one contrast color')
        
        best_contrast_ratio = 0
        for color in colors:
            # Ensure that we return a Color object
            if not isinstance(color, Color):
                color = RGBColor(color)
            
            contrast_ratio = self.contrast_ratio(color)
            if contrast_ratio > best_contrast_ratio:
                best_contrast_ratio = contrast_ratio
                best_color = color
        
        return best_color
    
    @classmethod
    def from_rgb_color(cls, rgb_color):
        return cls((rgb_color.r, rgb_color.g, rgb_color.b,))
    
    def to_rgb_color(self):
        return RGBColor((self.r, self.g, self.b,))
    
    def rgb_tuple_from_int(self, value):
        if not 0x000000 <= value <= 0xFFFFFF:
            raise ValueError('value must be in the 0x000000 to 0xFFFFFF range')
        
        return (
            (value & 0xFF0000) >> 16,
            (value & 0x00FF00) >> 8,
            (value & 0x0000FF),
        )
    
    def rgb_tuple_from_string(self, string):
        match = self.THREE_HEX_DIGIT_RE.search(string)
        if match:
            return tuple(
                int(hex_str * 2, 16)
                for hex_str in match.groups()
            )
        
        match = self.SIX_HEX_DIGIT_RE.search(string)
        if match:
            return tuple(
                int(hex_str, 16)
                for hex_str in match.groups()
            )
        
        match = self.CSS_RGB_INT_RE.search(string)
        if match:
            return tuple(
                int(num_str)
                for num_str in match.groups()
            )
        
        match = self.CSS_RGB_PERCENT_RE.search(string)
        if match:
            return tuple(
                int(int(num_str.rstrip('%')) / 100.0 * 255)
                for num_str in match.groups()
            )
        
        raise ValueError('Invalid string format %r' % (string,))


class YUVColor(Color):
    def __init__(self, value):
        if isinstance(value, YUVColor):
            self.yuv = value.yuv
        elif isinstance(value, Color):
            self.yuv = value.convert(YUVColor).yuv
        else:
            self.yuv = value
    
    def __repr__(self):
        return 'YUVColor(%r, %r, %r)' % (self.y, self.u, self.v,)
    
    def __setattr__(self, name, value):
        if name == 'y':
            if not 0.0 <= value <= 1.0:
                raise ValueError('y must be in the 0.0 to 1.0 range')
        
        if name == 'u':
            if not -0.436 <= value <= 0.436:
                raise ValueError('u must be in the -0.436 to 0.436 range')
        
        if name == 'v':
            if not -0.615 <= value <= 0.615:
                raise ValueError('v must be in the -0.615 to 0.615 range')
        
        super(YUVColor, self).__setattr__(name, value)
    
    def get_yuv(self):
        return (self.y, self.u, self.v)
    
    def set_yuv(self, (r, g, b)):
        self.y, self.u, self.v = y, u, v
    
    yuv = property(get_yuv, set_yuv)
    
    @classmethod
    def from_rgb_color(cls, rgb_color):
        r = rgb_color.r / 255.0
        g = rgb_color.g / 255.0
        b = rgb_color.b / 255.0
        
        y = ( 0.2126  * r) + ( 0.7152  * g) + ( 0.0722  * b)
        u = (-0.09991 * r) + (-0.33609 * g) + ( 0.436   * b)
        v = ( 0.615   * r) + (-0.55861 * g) + (-0.05639 * b)
        
        return cls((y, u, v))
    
    def to_rgb_color(self):
        y = self.y
        u = self.u
        v = self.v
        
        r = int(max(0.0, min(1.0, y +                  ( 1.28033 * v))) * 255.0)
        g = int(max(0.0, min(1.0, y + (-0.21482 * u) + (-0.38059 * v))) * 255.0)
        b = int(max(0.0, min(1.0, y + ( 2.12798 * u)                 )) * 255.0)
        
        return RGBColor((r, g, b))
    
    def adjust(self, hue_offset=0.0, saturation_multiplier=1.0,
                     contrast_multiplier=1.0, brightness_offset=0.0):
        
        hue_offset = float(hue_offset)
        saturation_multiplier = float(saturation_multiplier)
        contrast_multiplier = float(contrast_multiplier)
        brightness_offset = float(brightness_offset)
        
        y, u, v = self.y, self.u, self.v
        
        if hue_offset != 0.0:
            hue_cos, hue_sin = math.cos(hue_offset), math.sin(hue_offset)
            u = (u * hue_cos) + (v * hue_sin)
            v = (v * hue_cos) - (u * hue_sin)
        
        saturation_multiplier = max(0.0, saturation_multiplier)
        
        y = max(0.0, min(1.0, (y * contrast_multiplier) + brightness_offset))
        u = u * contrast_multiplier * saturation_multiplier
        v = v * contrast_multiplier * saturation_multiplier
        
        return YUVColor((y, u, v))
