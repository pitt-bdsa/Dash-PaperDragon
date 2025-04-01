def get_color_from_pixel(color_data):
    """Convert color data from the React component into a color string.

    Args:
        color_data (dict): Dictionary containing r, g, b values from the pixel color.

    Returns:
        str: A color string in the format 'rgb(r, g, b)'
    """
    if not color_data:
        return None
    return f"rgb({color_data['r']}, {color_data['g']}, {color_data['b']})"
