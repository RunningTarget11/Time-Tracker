# Renders the 3D graphics for Stacy's Time Tracker with Blender (Cycles).
# Run:  python3 source/blender/render_assets.py   (needs `pip install bpy`)
# Output: img/*.png  (transparent backgrounds)
import bpy, math, os, sys
from mathutils import Vector

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
OUT = os.path.join(ROOT, 'img'); os.makedirs(OUT, exist_ok=True)
FONT = '/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf'
ONLY = sys.argv[1:]  # optional: names to render

def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = 40
    sc.cycles.use_denoising = True; sc.render.film_transparent = True
    sc.view_settings.view_transform = 'Standard'; sc.view_settings.exposure = -0.35
    sc.render.image_settings.file_format = 'PNG'; sc.render.image_settings.color_mode = 'RGBA'
    w = bpy.data.worlds.new('w'); sc.world = w; w.use_nodes = True
    bg = w.node_tree.nodes['Background']; bg.inputs['Color'].default_value = (0.55, 0.45, 0.38, 1); bg.inputs['Strength'].default_value = 0.6
    return sc

def mat(name, col, metal=0.0, rough=0.35, coat=0.0, emit=None):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*col, 1); b.inputs['Metallic'].default_value = metal
    b.inputs['Roughness'].default_value = rough; b.inputs['Coat Weight'].default_value = coat
    if emit: b.inputs['Emission Color'].default_value = (*emit, 1); b.inputs['Emission Strength'].default_value = 1.5
    return m

GOLD = lambda: mat('gold', (1.0, 0.68, 0.18), 1.0, 0.16)
BRASS_D = lambda: mat('brassd', (0.55, 0.33, 0.08), 1.0, 0.28)
CREAM = lambda: mat('cream', (0.98, 0.95, 0.88), 0.0, 0.25, 0.6)
INK = lambda: mat('ink', (0.03, 0.02, 0.015), 0.0, 0.35)
PURPLE = lambda: mat('purple', (0.45, 0.25, 0.85), 0.0, 0.3, 0.5)
RED = lambda: mat('red', (0.85, 0.18, 0.12), 0.0, 0.3, 0.5)
WOOD = lambda: mat('wood', (0.42, 0.24, 0.12), 0.0, 0.55)
PAPER = lambda: mat('paper', (0.97, 0.95, 0.9), 0.0, 0.7)

def link(o): bpy.context.scene.collection.objects.link(o); return o

def light(name, loc, energy, col=(1, 1, 1), size=3):
    l = bpy.data.lights.new(name, 'AREA'); l.energy = energy; l.color = col; l.size = size
    o = link(bpy.data.objects.new(name, l)); o.location = loc
    o.rotation_euler = (Vector((0, 0, 0)) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler(); return o

def studio(scale=1.0):
    light('key', (-4 * scale, -5 * scale, 6 * scale), 1400 * scale * scale, (1, 0.9, 0.78), 4 * scale)
    light('rim', (5 * scale, 4 * scale, 3 * scale), 900 * scale * scale, (0.75, 0.82, 1), 3 * scale)
    light('fill', (3 * scale, -6 * scale, -1 * scale), 300 * scale * scale, (1, 0.8, 0.6), 5 * scale)

def camera(target, dist, lens=60, elev=8, az=0):
    c = bpy.data.cameras.new('cam'); c.lens = lens; o = link(bpy.data.objects.new('cam', c))
    e, a = math.radians(elev), math.radians(az)
    o.location = Vector(target) + Vector((dist * math.sin(a) * math.cos(e), -dist * math.cos(a) * math.cos(e), dist * math.sin(e)))
    o.rotation_euler = (Vector(target) - o.location).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.scene.camera = o; return o

def text(body, size, depth, bevel, m, loc=(0, 0, 0), m_side=None, spacing=1.0):
    cu = bpy.data.curves.new('t', 'FONT'); cu.body = body; cu.font = bpy.data.fonts.load(FONT)
    cu.size = size; cu.extrude = depth; cu.bevel_depth = bevel; cu.bevel_resolution = 4
    cu.align_x = 'CENTER'; cu.align_y = 'CENTER'; cu.space_character = spacing
    o = link(bpy.data.objects.new('t', cu)); o.location = loc; o.rotation_euler = (math.radians(90), 0, 0)
    o.data.materials.append(m)
    if m_side: o.data.materials.append(m_side)
    return o

def cyl(r, d, loc, m, rot=(math.radians(90), 0, 0), verts=96, bevel=0.0):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=d, location=loc, rotation=rot)
    o = bpy.context.object; o.data.materials.append(m)
    if bevel:
        bm = o.modifiers.new('b', 'BEVEL'); bm.width = bevel; bm.segments = 4
    bpy.ops.object.shade_smooth(); return o

def box(size, loc, m, rot=(0, 0, 0), bevel=0.02):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
    o = bpy.context.object; o.scale = size; o.data.materials.append(m)
    bm = o.modifiers.new('b', 'BEVEL'); bm.width = bevel; bm.segments = 3
    return o

def render(name, w, h, samples=None):
    sc = bpy.context.scene; sc.render.resolution_x = w; sc.render.resolution_y = h
    if samples: sc.cycles.samples = samples
    sc.render.filepath = os.path.join(OUT, name + '.png'); bpy.ops.render.render(write_still=True)
    print('rendered', name)

def want(n): return not ONLY or n in ONLY

# ---------- stopwatch (used on splash, Today screen, app icon area) ----------
def stopwatch(at=(0, 0, 0), hh=3, mm=48):
    g, gd, cr, ink, red = GOLD(), BRASS_D(), CREAM(), INK(), RED()
    x, y, z = at
    cyl(1.0, 0.32, (x, y, z), g, bevel=0.08)                       # case
    cyl(0.9, 0.05, (x, y - 0.17, z), cr)                            # face
    cyl(0.93, 0.06, (x, y - 0.16, z), gd)                            # bezel ring (behind face edge)
    bpy.ops.mesh.primitive_torus_add(major_radius=0.93, minor_radius=0.06, location=(x, y - 0.18, z), rotation=(math.radians(90), 0, 0))
    t = bpy.context.object; t.data.materials.append(g); bpy.ops.object.shade_smooth()
    cyl(0.16, 0.22, (x, y, z + 1.08), g, rot=(0, 0, 0), bevel=0.03)        # stem
    cyl(0.24, 0.16, (x, y, z + 1.27), g, rot=(0, 0, 0), bevel=0.05)        # crown button
    bpy.ops.mesh.primitive_torus_add(major_radius=0.22, minor_radius=0.055, location=(x, y, z + 1.5), rotation=(math.radians(90), 0, 0))
    t = bpy.context.object; t.data.materials.append(g); bpy.ops.object.shade_smooth()   # ring
    for s in (-1, 1):                                                       # side pushers
        o = cyl(0.09, 0.22, (x + s * 0.62, y, z + 0.82), g, rot=(0, math.radians(s * -40), 0), bevel=0.02)
    for i in range(60):                                                     # ticks
        a = math.radians(i * 6); big = i % 5 == 0
        L = 0.14 if big else 0.06; r = 0.82 - L / 2
        box((0.035 if big else 0.016, 0.02, L), (x + r * math.sin(a), y - 0.21, z + r * math.cos(a)), ink, rot=(0, a, 0), bevel=0.004)
    def hand(angle, length, width, m):
        a = math.radians(angle)
        box((width, 0.02, length), (x + length / 2 * math.sin(a), y - 0.24, z + length / 2 * math.cos(a)), m, rot=(0, a, 0), bevel=0.008)
    hand((hh % 12 + mm / 60) * 30, 0.45, 0.07, ink)
    hand(mm * 6, 0.7, 0.045, ink)
    hand(200, 0.78, 0.02, red)
    cyl(0.07, 0.06, (x, y - 0.27, z), red)

if want('stopwatch'):
    reset(); studio()
    stopwatch()
    camera((0, 0, 0.3), 6.0, lens=55, elev=10, az=-18)
    render('stopwatch', 512, 600)

# ---------- splash / header logo: 3D "STACY'S / Time Tracker" ----------
if want('logo'):
    reset(); studio(1.6)
    g, cr, gd = GOLD(), CREAM(), BRASS_D()
    a = text("STACY'S", 1.42, 0.14, 0.03, cr, (0, 0, 0.8), spacing=1.42)
    b = text("Time Tracker", 1.25, 0.2, 0.035, g, (0, 0, -0.25))
    for o in (a, b): o.data.offset = -0.012
    # gold underline bar
    box((5.2, 0.14, 0.09), (0, 0.05, -1.12), gd, bevel=0.03)
    camera((0, 0, 0.0), 14, lens=60, elev=6, az=0)
    render('logo', 1400, 620, samples=48)

# ---------- clipboard with time sheet (Timesheet tab) ----------
if want('clipboard'):
    reset(); studio()
    wd, pa, gd, ink, pu = WOOD(), PAPER(), GOLD(), INK(), PURPLE()
    box((2.0, 0.08, 2.7), (0, 0, 0), wd, bevel=0.06)
    box((1.75, 0.02, 2.3), (0, -0.05, -0.1), pa, bevel=0.005)
    box((0.9, 0.12, 0.32), (0, -0.08, 1.25), gd, bevel=0.05)                 # clip
    cyl(0.12, 0.14, (0, -0.1, 1.42), gd, rot=(math.radians(90), 0, 0), bevel=0.02)
    for i in range(7):                                                       # table lines
        zz = 0.7 - i * 0.28
        box((1.5, 0.01, 0.025), (0, -0.065, zz), ink, bevel=0.003)
        if i:
            box((0.35, 0.012, 0.09), (-0.45, -0.07, zz + 0.13), ink if i % 2 else pu, bevel=0.01)
            box((0.25, 0.012, 0.09), (0.35, -0.07, zz + 0.13), pu if i in (2, 5) else ink, bevel=0.01)
    box((0.04, 0.01, 1.68), (-0.05, -0.065, -0.12), ink, bevel=0.003)
    # check mark
    for (sx, sz, rot, L) in ((-0.62, -0.95, 40, 0.28), (-0.47, -0.88, -50, 0.5)):
        box((0.09, 0.03, L), (sx + 0.85, -0.09, sz - 0.05), mat('green', (0.15, 0.6, 0.3), 0, 0.3, 0.5), rot=(0, math.radians(rot), 0), bevel=0.02)
    camera((0, 0, 0.1), 9.5, lens=55, elev=14, az=20)
    render('clipboard', 480, 560)

# ---------- coin stack (pay) ----------
if want('coins'):
    reset(); studio()
    g = GOLD(); gd = BRASS_D()
    import random; random.seed(4)
    def coin(loc, tilt=0):
        o = cyl(0.62, 0.14, loc, g, rot=(math.radians(tilt), 0, random.random() * 6), bevel=0.03)
        cyl(0.48, 0.15, loc, gd, rot=(math.radians(tilt), 0, 0))
    for i in range(6): coin((random.uniform(-.05, .05) - 0.45, random.uniform(-.05, .05), -0.8 + i * 0.15), 0)
    for i in range(4): coin((random.uniform(-.05, .05) + 0.55, random.uniform(-.05, .05) + 0.2, -0.8 + i * 0.15), 0)
    for i in range(3): coin((random.uniform(-.05, .05) + 0.05, random.uniform(-.05, .05) - 0.7, -0.8 + i * 0.15), 0)
    camera((0, 0, -0.45), 8.0, lens=55, elev=22, az=-12)
    render('coins', 480, 420)
