Colorops converts between colorspaces, finds the best text color for your
background, and can adjust hue, saturation, contrast and brightness. It's
particularly useful for templated HTML and CSS, e.g:

    border: {{ primary_color.adjust(brightness_offset=0.4) }}

The module uses YUV for high-quality results, rather than HSV.
