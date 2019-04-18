# Generate shaft encoder
# - Gray encoding
# - MSB (Most Significant Bit) on the innermost circular band, LSB (Least Significant Bit) on the outermost
# - 0 = White, 1 = Black

import os
import sys
import math
import svgwrite

src_dirpath = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'src')
sys.path.append(src_dirpath)

from boost.gray_code import generate_gray_codes


TARGET_SHAFT_ENCODER_MASK       = 1
TARGET_SHAFT_ENCODER_CUT        = 2
TARGET_SENSORS_SUPPORT_CUT      = 4
TARGET_SENSORS_SUPPORT_ENGRAVE  = 8
TARGET_ALL                      = 1 + 2 + 4 + 8


PAGE_SIZE = [350.0, 420.0]  # larger than A3, but printable on A3

PAGE_CENTER = (PAGE_SIZE[0]/2, PAGE_SIZE[1]/2)

SENSOR = {
    'size': [14.0, 31.0],  # width, height
    'sensor_hole': [1.5, 25.0, 11.0, 6.0],  # x, y, width, height
    'screw_hole': [7.0, 7.5, 1.0],  # Center and diameter (hole is actually 3 mm, but we make it smaller, for the screw)
}

SHAFT = {
    'diameter': 70.0,
}

SHAFT_ENCODER = {
    # 'diameter': 180.0,
    'inner_diameter': 80.0,
    'band_width': 16.0,
    'band_gap': 0.0,
    'band_angle_displacement': 0.0,
}

SENSORS_CUTTING_PROFILE = {
    'height': 33.0,
    'abbundance': 4.0,
    'external_abbundance': 10.0,
    'internal_abbundance': -50.0,
    'top_abbundance': -30.0,
}

# For printing only, not cutting
MARKING_STROKE_WIDTH = 0.1

NUM_BANDS = 6
all_gray_codes = generate_gray_codes(NUM_BANDS)


def draw_page(dwg):
    return dwg.rect((0, 0), PAGE_SIZE, fill='white', stroke_width=MARKING_STROKE_WIDTH, stroke='black')


def main(target):
    filename = {
        TARGET_SHAFT_ENCODER_MASK: 'encoder_mask',
        TARGET_SHAFT_ENCODER_CUT: 'encoder_cut',
        TARGET_SENSORS_SUPPORT_CUT: 'sensors_cut',
        TARGET_SENSORS_SUPPORT_ENGRAVE: 'sensors_engrave',
        TARGET_ALL: 'all',
    }[target]
    if not os.path.exists('shaft_encoder'):
        os.makedirs('shaft_encoder')

    dwg = svgwrite.Drawing('shaft_encoder/{0}.svg'.format(filename),
                           size=['{0}mm'.format(int(d)) for d in PAGE_SIZE], x='0mm', y='0mm',
                           enable_background="new 0 0 {0} {1}".format(*[int(d) for d in PAGE_SIZE]),
                           viewBox="0 0 {0} {1}".format(*[int(d) for d in PAGE_SIZE]),
                           )

    if target == TARGET_ALL:
        dwg.add(draw_page(dwg))

    dwg.add(draw_shaft_encoder(dwg, center=PAGE_CENTER, encoder_starting_angle=0, target=target))

    dwg.save()


def draw_sensor(dwg, translate, rotate_cw, target):
    parent_group = dwg.g(transform='translate({1} {2}) rotate({0})'.format(180+rotate_cw, translate[0], PAGE_SIZE[1]-translate[1]))
    g = dwg.g(transform='translate({0} {1})'.format(-(SENSOR['sensor_hole'][0] + SENSOR['sensor_hole'][2]/2), -(SENSOR['sensor_hole'][1] + SENSOR['sensor_hole'][3]/2)))
    if target & TARGET_SENSORS_SUPPORT_ENGRAVE:
        g.add(dwg.rect((0, 0), SENSOR['size'], stroke_width=MARKING_STROKE_WIDTH, stroke='black', fill='white'))
    if target & TARGET_SENSORS_SUPPORT_CUT:
        g.add(dwg.rect(SENSOR['sensor_hole'][:2], SENSOR['sensor_hole'][2:], stroke_width=MARKING_STROKE_WIDTH, stroke='black', fill='black'))
        g.add(dwg.circle(center=(SENSOR['screw_hole'][0], SENSOR['screw_hole'][1]), r=SENSOR['screw_hole'][2]/2, stroke='black', stroke_width=MARKING_STROKE_WIDTH, fill='black'))
    parent_group.add(g)
    return parent_group


def draw_arc_cw(dwg, center, inner_radius, outer_radius, beginning_angle_cw, ending_angle_cw):
    p = dwg.path(fill='black')
    svg_arc(p, center, outer_radius, beginning_angle_cw, ending_angle_cw, firstArc=True)
    svg_arc(p, center, inner_radius, ending_angle_cw, beginning_angle_cw, cw=True)
    p.push('Z')
    return p


def svg_arc(dwg_path, center, r, startDeg, endDeg, cw=False, firstArc=False):
    # largeArc = (endDeg - startDeg) % 360 > 180
    largeArc = False
    startRad, endRad = startDeg*math.pi/180, endDeg*math.pi/180
    sx, sy = r*math.cos(startRad), r*math.sin(startRad)
    ex, ey = r*math.cos(endRad), r*math.sin(endRad)
    dwg_path.push('M' if firstArc else 'L', center[0]+sx, center[1]+sy)
    dwg_path.push('A', r, r, 0)
    dwg_path.push('1' if largeArc else '0', '0' if largeArc ^ cw else '1')
    dwg_path.push(center[0]+ex, center[1]+ey)


def draw_shaft_encoder(dwg, center, encoder_starting_angle, target):
    group = dwg.g()
    band_width = SHAFT_ENCODER['band_width']
    if 'inner_diameter' in SHAFT_ENCODER:
        outer_radius = SHAFT_ENCODER['inner_diameter']/2 + band_width * NUM_BANDS
    else:
        outer_radius = SHAFT_ENCODER['diameter']/2
    inter_band_gap = SHAFT_ENCODER['band_gap']
    band_angle_displacement = SHAFT_ENCODER['band_angle_displacement']
    bit_angle = 360.0 / len(all_gray_codes)
    sensor_positions = []

    # The circular mask circumference
    if target & TARGET_SHAFT_ENCODER_CUT or target & TARGET_SHAFT_ENCODER_MASK:
        group.add(dwg.circle(center=(center[0], PAGE_SIZE[1]-center[1]), r=outer_radius, stroke='black', stroke_width=MARKING_STROKE_WIDTH, fill='none'))

    # The shaft hole
    if target & TARGET_SHAFT_ENCODER_CUT or target & TARGET_SHAFT_ENCODER_MASK or target & TARGET_SENSORS_SUPPORT_CUT:
        group.add(draw_shaft_hole(dwg, PAGE_CENTER))

    # The bands
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
                group.add(draw_arc_cw(
                    dwg,
                    center,
                    band_inner_radius,
                    band_outer_radius,
                    arc_start,
                    arc_end))
        sensor_positions.append( (band_starting_position[0], band_starting_position[1], band_starting_angle) )

    # The sensors
    for sensor_x, sensor_y, sensor_angle in sensor_positions:
        group.add(draw_sensor(dwg, translate=(sensor_x, sensor_y), rotate_cw=sensor_angle, target=target))

    # The sensors cutting profile
    if target & TARGET_SENSORS_SUPPORT_CUT:
        group.add(draw_sensor_cutting_mask(dwg, outer_radius))

    return group


def draw_sensor_cutting_mask(dwg, disk_radius):
    g = dwg.g(transform='translate({0} {1})'.format(PAGE_SIZE[0]/2, PAGE_SIZE[1]/2))
    shaft_radius = SHAFT['diameter']/2.0
    g.add(dwg.rect((-shaft_radius - SENSORS_CUTTING_PROFILE['abbundance'] - SENSORS_CUTTING_PROFILE['internal_abbundance'], -shaft_radius - SENSORS_CUTTING_PROFILE['abbundance'] - SENSORS_CUTTING_PROFILE['top_abbundance']),
                   (shaft_radius + SENSORS_CUTTING_PROFILE['abbundance']*2 + disk_radius + SENSORS_CUTTING_PROFILE['external_abbundance'] + SENSORS_CUTTING_PROFILE['internal_abbundance'],
                    shaft_radius + SENSORS_CUTTING_PROFILE['abbundance']*2 + SENSORS_CUTTING_PROFILE['height'] + SENSORS_CUTTING_PROFILE['top_abbundance']),
                    stroke_width=MARKING_STROKE_WIDTH, stroke='black', fill='none'))
    return g


def draw_shaft_hole(dwg, center):
    return dwg.circle(center=(center[0], PAGE_SIZE[1]-center[1]), r=SHAFT['diameter']/2, stroke='black', stroke_width=MARKING_STROKE_WIDTH, fill='black')


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
