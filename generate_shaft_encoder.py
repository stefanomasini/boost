import os
import sys
import math
import drawSvg as draw

src_dirpath = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'src')
sys.path.append(src_dirpath)

from boost.gray_code import generate_gray_codes


TARGET_SHAFT_ENCODER_MASK       = 1
TARGET_SHAFT_ENCODER_CUT        = 2
TARGET_SENSORS_SUPPORT_CUT      = 4
TARGET_SENSORS_SUPPORT_ENGRAVE  = 8
TARGET_ALL                      = 1 + 2 + 4 + 8


PAGE_SIZE = [210.0, 297.0]

PAGE_CENTER = (PAGE_SIZE[0]/2, PAGE_SIZE[1]/2)

SENSOR = {
    'size': [14.0, 31.0],  # width, height
    'sensor_hole': [1.5, 25.0, 11.0, 6.0],  # x, y, width, height
    'screw_hole': [7.0, 7.5, 1.0],  # Center and diameter (hole is actually 3 mm, but we make it smaller, for the screw)
}

SHAFT = {
    'diameter': 10.0,
}

SHAFT_ENCODER = {
    'diameter': 180.0,
    'band_width': 14.0,
    'band_gap': 0.0,
    'band_angle_displacement': 20,
}

# For printing only, not cutting
MARKING_STROKE_WIDTH = 0.1

NUM_BANDS = 5
all_gray_codes = generate_gray_codes(NUM_BANDS)


def draw_page():
    return draw.Rectangle(0, 0, *PAGE_SIZE, fill='white', stroke_width=MARKING_STROKE_WIDTH, stroke='black')


def main(target):
    d = draw.Drawing(*PAGE_SIZE)

    if target == TARGET_ALL:
        d.draw(draw_page())

    d.append(draw_shaft_encoder(center=PAGE_CENTER, encoder_starting_angle=0, target=target))

    # d.setRenderSize(*PAGE_SIZE)
    d.setPixelScale(10)  # Set number of pixels per geometry unit
    # d.setRenderSize(400,200)  # Alternative to setPixelScale
    filename = {
        TARGET_SHAFT_ENCODER_MASK: 'encoder_mask',
        TARGET_SHAFT_ENCODER_CUT: 'encoder_cut',
        TARGET_SENSORS_SUPPORT_CUT: 'sensors_cut',
        TARGET_SENSORS_SUPPORT_ENGRAVE: 'sensors_engrave',
        TARGET_ALL: 'all',
    }[target]
    if not os.path.exists('shaft_encoder'):
        os.makedirs('shaft_encoder')
    if not os.path.exists('shaft_encoder/svg'):
        os.makedirs('shaft_encoder/svg')
    if not os.path.exists('shaft_encoder/png'):
        os.makedirs('shaft_encoder/png')
    d.saveSvg('shaft_encoder/svg/{0}.svg'.format(filename))
    d.savePng('shaft_encoder/png/{0}.png'.format(filename))

    # Display in iPython notebook
    # d.rasterize()  # Display as PNG
    # d  # Display as SVG


def draw_sensor(translate, rotate_cw, target):
    parent_group = draw.Group(transform='translate({1} {2}) rotate({0})'.format(rotate_cw, translate[0], -translate[1]))
    g = draw.Group(transform='translate({0} {1})'.format(-(SENSOR['sensor_hole'][0] + SENSOR['sensor_hole'][2]/2), SENSOR['sensor_hole'][1] + SENSOR['sensor_hole'][3]/2))
    if target & TARGET_SENSORS_SUPPORT_ENGRAVE:
        g.draw(draw.Rectangle(0, 0, *SENSOR['size'], stroke_width=MARKING_STROKE_WIDTH, stroke='black', fill='white'))
    if target & TARGET_SENSORS_SUPPORT_CUT:
        g.draw(draw.Rectangle(*SENSOR['sensor_hole'], stroke_width=MARKING_STROKE_WIDTH, stroke='black', fill='black'))
        g.draw(draw.Circle(*SENSOR['screw_hole'][:2], SENSOR['screw_hole'][2]/2, stroke='black', stroke_width=MARKING_STROKE_WIDTH, fill='black'))
    parent_group.draw(g)
    return parent_group


def draw_arc_cw(center, inner_radius, outer_radius, beginning_angle_cw, ending_angle_cw):
    p = draw.Path(fill='black')
    p.arc(center[0], center[1], outer_radius, -ending_angle_cw, -beginning_angle_cw)
    p.arc(center[0], center[1], inner_radius, -beginning_angle_cw, -ending_angle_cw, cw=True, includeL=True)
    p.Z()
    return p


def draw_shaft_encoder(center, encoder_starting_angle, target):
    group = draw.Group()
    outer_radius = SHAFT_ENCODER['diameter']/2
    band_width = SHAFT_ENCODER['band_width']
    inter_band_gap = SHAFT_ENCODER['band_gap']
    band_angle_displacement = SHAFT_ENCODER['band_angle_displacement']
    bit_angle = 360.0 / len(all_gray_codes)
    sensor_positions = []
    if target & TARGET_SHAFT_ENCODER_CUT or target & TARGET_SHAFT_ENCODER_MASK:
        group.draw(draw.Circle(*center, SHAFT_ENCODER['diameter']/2, stroke='black', stroke_width=MARKING_STROKE_WIDTH, fill='none'))
    if target & TARGET_SHAFT_ENCODER_CUT or target & TARGET_SHAFT_ENCODER_MASK or target & TARGET_SENSORS_SUPPORT_CUT:
        group.append(draw_shaft_hole(PAGE_CENTER))
    for band_idx in range(NUM_BANDS):
        arcs = []
        bit_values = [code[NUM_BANDS-1-band_idx] == '1' for code in all_gray_codes]
        bit_values.append(False)  # Add a 0 to make the below iteration happy and complete
        band_outer_radius = outer_radius - band_idx * band_width
        band_inner_radius = band_outer_radius - band_width + inter_band_gap
        last_bit_value = False
        band_starting_angle = encoder_starting_angle + band_angle_displacement * band_idx
        band_starting_angle_rad = 2 * math.pi * band_starting_angle / 360.0
        sensor_center_radius = (band_outer_radius + band_inner_radius) / 2
        band_starting_position = [
            center[0] + sensor_center_radius * math.cos(-band_starting_angle_rad),
            center[1] + sensor_center_radius * math.sin(-band_starting_angle_rad),
        ]
        starting_angle = None
        for bit_idx, bit_value in enumerate(bit_values):
            current_iteration_angle = bit_idx * bit_angle + band_starting_angle
            if not last_bit_value and bit_value:
                starting_angle = current_iteration_angle
            if starting_angle and last_bit_value and not bit_value:
                arcs.append( (starting_angle, current_iteration_angle) )
            last_bit_value = bit_value
        if target & TARGET_SHAFT_ENCODER_MASK:
            for arc_start, arc_end in arcs:
                group.draw(draw_arc_cw(
                    center,
                    band_inner_radius,
                    band_outer_radius,
                    arc_start,
                    arc_end))
        sensor_positions.append( (band_starting_position[0], band_starting_position[1], band_starting_angle) )
    for sensor_x, sensor_y, sensor_angle in sensor_positions:
        group.append(draw_sensor(translate=(sensor_x, sensor_y), rotate_cw=sensor_angle, target=target))
    return group


def draw_shaft_hole(center):
    return draw.Circle(*center, SHAFT['diameter']/2, stroke='black', stroke_width=MARKING_STROKE_WIDTH, fill='black')


if __name__ == '__main__':
    main(target=TARGET_SHAFT_ENCODER_MASK)
    main(target=TARGET_SHAFT_ENCODER_CUT)
    main(target=TARGET_SENSORS_SUPPORT_CUT)
    main(target=TARGET_SENSORS_SUPPORT_ENGRAVE)
    main(target=(
            TARGET_SHAFT_ENCODER_MASK
            | TARGET_SHAFT_ENCODER_CUT
            | TARGET_SENSORS_SUPPORT_CUT
            | TARGET_SENSORS_SUPPORT_ENGRAVE
        ))
