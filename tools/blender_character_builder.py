"""Reproducible vinyl character collection inspired by Ref/trump.jpg.
Run: blender --background --python tools/blender_character_builder.py
Optional: BLENDER_ONLY_KIND=boss BLENDER_RENDER=1 (studio previews).
Characters face -Y in Blender / +Z in glTF; feet sit on ground. No external textures.
"""
import bpy
import math
import os
import sys
from mathutils import Vector

OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'assets', 'characters')
VARIANTS = {
    'chef': ('#EBAF80', '#B92E34', '#623A24'),
    'boss': ('#F2B17A', '#183D79', '#EBA83F'),
    'colleague': ('#BD805A', '#DE6264', '#262532'),
    'customer': ('#D39769', '#E6AD32', '#302720'),
    'complainer': ('#E0AC85', '#58A994', '#A4A6B0'),
    'client': ('#BC825E', '#293951', '#282633'),
}

def material(name, color, rough=.4):
    rgb = [int(color[i:i+2], 16)/255 for i in (1, 3, 5)]
    linear = [c/12.92 if c < .04045 else ((c+.055)/1.055)**2.4 for c in rgb]
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*linear, 1)
    m.use_nodes = True
    bs = m.node_tree.nodes.get('Principled BSDF')
    bs.inputs['Base Color'].default_value = (*linear, 1)
    bs.inputs['Roughness'].default_value = rough
    return m

def finish(obj, name, mat):
    obj.name = name
    obj.data.materials.append(mat)
    for p in obj.data.polygons:
        p.use_smooth = True
    return obj

def sphere(name, loc, scale, mat):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=20, location=loc)
    o = bpy.context.object
    o.scale = scale
    return finish(o, name, mat)

def box(name, loc, size, mat, bevel=.04):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.object
    o.scale = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    b = o.modifiers.new('Soft molded edges', 'BEVEL')
    b.width = bevel
    b.segments = 5
    n = o.modifiers.new('Weighted surface normals', 'WEIGHTED_NORMAL')
    n.keep_sharp = True
    return finish(o, name, mat)

def path(name, points, radius, mat, radii=None):
    c = bpy.data.curves.new(name, 'CURVE')
    c.dimensions = '3D'
    c.resolution_u = 10
    c.bevel_depth = radius
    c.bevel_resolution = 3
    c.use_fill_caps = True
    s = c.splines.new('BEZIER')
    s.bezier_points.add(len(points)-1)
    for i, (p, co) in enumerate(zip(s.bezier_points, points)):
        p.co = co
        p.handle_left_type = p.handle_right_type = 'AUTO'
        if radii:
            p.radius = radii[i]
    o = bpy.data.objects.new(name, c)
    bpy.context.collection.objects.link(o)
    c.materials.append(mat)
    return o

def patch(name, xz, y, depth, mat, bevel=.018):
    # Rounded solid tailoring panels; front is the negative Y side.
    verts = [(x, y, z) for x, z in xz] + [(x, y+depth, z) for x,z in xz]
    n = len(xz)
    faces = [tuple(range(n)), tuple(reversed(range(n, n*2)))]
    faces += [(i, (i+1)%n, (i+1)%n+n, i+n) for i in range(n)]
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, [], faces)
    mesh.update()
    o = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(o)
    bpy.context.view_layer.objects.active = o
    o.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.object.mode_set(mode='OBJECT')
    o.select_set(False)
    b = o.modifiers.new('Tailored soft edge', 'BEVEL')
    b.width = bevel
    b.segments = 3
    o.modifiers.new('Panel normals', 'WEIGHTED_NORMAL')
    return finish(o, name, mat)

def build_character(kind):
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    skin_hex, coat_hex, hair_hex = VARIANTS[kind]
    skin = material(kind+'_warm_vinyl', skin_hex, .43)
    coat = material(kind+'_satin_clothing', coat_hex, .48)
    hair = material(kind+'_hair', hair_hex, .34)
    hair_light = material(kind+'_hair_ribbons', '#F8C362' if kind=='boss' else hair_hex, .38)
    white = material(kind+'_ivory', '#FFF6E3', .32)
    dark = material(kind+'_eyes', '#172032', .22)
    shoe = material(kind+'_shoes', '#18202D', .3)
    mouth = material(kind+'_mouth', '#40191C', .48)
    lip = material(kind+'_lip', '#C68059', .48)
    red = material(kind+'_red', '#BE303B', .4)
    gold = material(kind+'_gold', '#F2C15C', .34)
    trim = material(kind+'_trim', '#284F87' if kind=='boss' else coat_hex, .42)
    pink = material(kind+'_ear_inset', '#CB886F', .5)
    suit = kind in ('boss', 'client')
    # Low, broad shoes and a pear-shaped jacket, with a flatter hem.
    for s in (-1, 1):
        box(kind+f'_sole{s}', (s*.205, -.075, .0425), (.27,.38,.085), shoe, .04)
        box(kind+f'_shoe{s}', (s*.205, -.09, .12), (.27,.39,.17), shoe, .075)
        path(kind+f'_shoe_seam{s}', [(s*.205-.08,-.27,.13),(s*.205,-.286,.15),(s*.205+.08,-.27,.13)], .007, trim)
    box(kind+'_body', (0,0,.56), (.92,.65,.79), coat, .24)
    sphere(kind+'_neck', (0,0,.93), (.19,.19,.16), skin)
    # Every character has exactly two attached sleeves and sculpted hands.
    for s in (-1,1):
        path(kind+f'_sleeve{s}', [(s*.34,0,.81),(s*.49,-.025,.65),(s*.55,-.09,.47)], .137, coat, [1.05,1,.8])
        cuff = sphere(kind+f'_cuff{s}', (s*.554,-.09,.465), (.12,.12,.055), white if suit or kind=='chef' else trim)
        cuff.rotation_euler[1] = s*.3
        hm = white if kind=='chef' else skin
        sphere(kind+f'_palm{s}', (s*.57,-.105,.35), (.105,.092,.14), hm)
        for j in range(3):
            sphere(kind+f'_finger{s}_{j}', (s*(.519+j*.045),-.151,.29+abs(j-1)*.012), (.028,.054,.071), hm)
        sphere(kind+f'_thumb{s}', (s*.49,-.16,.375), (.053,.06,.082), hm)
    if suit:
        patch(kind+'_shirt', [(-.21,.89),(.21,.89),(.12,.4),(-.12,.4)], -.339,.055,white)
        for s in (-1,1):
            patch(kind+f'_lapel{s}', [(s*.22,.92),(s*.36,.78),(s*.25,.72),(s*.31,.64),(s*.105,.43),(s*.12,.75)], -.365,.04,trim)
            patch(kind+f'_collar{s}', [(s*.02,.86),(s*.19,.93),(s*.16,.74)], -.398,.036,white,.012)
        tie_mat = red if kind=='boss' else material('client_silk_purple','#8E416F',.35)
        patch(kind+'_tie', [(-.045,.77),(.045,.77),(.115,.3),(0,.225),(-.115,.3)], -.424,.04,tie_mat,.015)
        box(kind+'_tie_knot', (0,-.435,.805), (.105,.075,.105),tie_mat,.023)
        if kind=='boss':
            # Clip diagonal bands to the widening tie instead of protruding bars.
            for i in range(5):
                z=.32+i*.084
                w=.115-(z-.3)*.15
                patch(f'boss_tie_band{i}', [(-w,z-.033),(w,z+.055),(w-.006,z+.079),(-w+.004,z-.009)],-.448,.006,gold,.002)
            box('boss_lapel_pin',(.278,-.405,.786),(.074,.025,.043),red,.006)
            for j in range(2):
                box('boss_pin_stripe'+str(j),(.284,-.42,.777+j*.014),(.06,.004,.005),white,.001)
            box('boss_pin_canton',(.255,-.424,.793),(.025,.005,.019),trim,.002)
        else:
            box('client_pocket_square',(.29,-.342,.7),(.105,.027,.075),white,.009)
        path(kind+'_back_seam', [(0,.329,.79),(0,.332,.5),(0,.316,.24)], .0045,trim)
    elif kind=='chef':
        box('chef_apron',(0,-.329,.53),(.57,.06,.57),white,.07)
        for s in (-1,1):
            for z in (.66,.52):
                sphere(f'chef_button{s}_{z}',(s*.135,-.374,z),(.021,.016,.021),dark)
        box('chef_pocket',(0,-.367,.365),(.29,.025,.13),white,.025)
        path('chef_neckerchief',[(-.22,-.17,.92),(0,-.3,.86),(.22,-.17,.92)],.043,red)
        patch('chef_scarf_tail',[(0,.87),(.115,.72),(.03,.7),(-.045,.82)],-.38,.035,red)
    else:
        path(kind+'_collar',[(-.21,-.24,.905),(0,-.332,.84),(.21,-.24,.905)],.026,trim)
        path(kind+'_hem',[(-.31,-.29,.24),(0,-.335,.218),(.31,-.29,.24)],.009,trim)
    # Rounded square head leaves a readable face plane like a molded figurine.
    box(kind+'_head',(0,0,1.335),(1.0,.82,.84),skin,.235)
    for s in (-1,1):
        sphere(kind+f'_ear{s}',(s*.502,-.015,1.295),(.105,.079,.139),skin)
        sphere(kind+f'_ear_inner{s}',(s*.54,-.078,1.295),(.053,.024,.081),pink)
    # Curved smile silhouette, individual rounded teeth and lower lip.
    big = kind in ('boss','chef')
    w = .33 if big else .24
    outline = [(-w,1.205),(-w*.65,1.177),(0,1.166),(w*.65,1.177),(w,1.205),(w*.91,1.071),(w*.51,1.003),(0,.986),(-w*.51,1.003),(-w*.91,1.071)]
    patch(kind+'_smile_rim',outline,-.422,.055,lip,.033)
    inner=[(x*.93,1.11+(z-1.11)*.82) for x,z in outline]
    patch(kind+'_smile',inner,-.449,.03,mouth,.024)
    for i in range(6 if big else 4):
        count=6 if big else 4
        x=(i-(count-1)/2)*w*.285
        box(kind+f'_tooth{i}',(x,-.471,1.144+.03*(abs(x)/w)**2),(w*.265,.044,.08 if abs(x)>w*.55 else .098),white,.019)
    # Button eyes and a tapered caricature nose.
    sphere(kind+'_nose_bridge',(0,-.427,1.365),(.065,.07,.122),skin)
    sphere(kind+'_nose',(0,-.49,1.296),(.096,.112,.076),skin)
    for s in (-1,1):
        sphere(kind+f'_eye{s}',(s*.208,-.418,1.408),(.044,.027,.052),dark)
        sphere(kind+f'_catchlight{s}',(s*.208-.011,-.442,1.428),(.01,.006,.012),white)
        path(kind+f'_brow{s}',[(s*.105,-.425,1.507),(s*.208,-.429,1.548 if kind=='boss' else 1.543),(s*.302,-.403,1.529)],.029,hair,[.7,1,.55])
    # Scalp at rear, sideburns and overlapping swept locks; no face-covering dome.
    sphere(kind+'_hair_back',(0,.14,1.47),(.496,.327,.351),hair)
    for s in (-1,1):
        sphere(kind+f'_sideburn{s}',(s*.455,.018,1.487),(.08,.215,.19),hair)
    if kind not in ('boss','customer'):
        sphere(kind+'_hair_crown',(0,.07,1.685),(.49,.405,.17),hair)
    if kind=='boss':
        # Broad tapered swept ribbons share a silhouette and rise into a pointed flip.
        for i in range(6):
            y=-.29+i*.103
            path(f'boss_swept_lock{i}',[(-.45,y+.015,1.66),(-.29,y-.06,1.79),(.03,y-.065,1.80),(.34,y-.05,1.77),(.50,y-.01,1.90)],.091,hair if i%2 else hair_light,[.55,1.1,1.16,.85,.045])
        for s in (-1,1):
            for j in range(3):
                path(f'boss_side_ridge{s}_{j}',[(s*.43,-.13,1.62-j*.056),(s*.494,.02,1.60-j*.056),(s*.43,.2,1.58-j*.056)],.027,hair_light,[.25,1,.2])
        for i in range(7):
            x=(i-3)*.12
            path(f'boss_back_lock{i}',[(x*.7,.23,1.78),(x,.425,1.60),(x*.85,.399,1.30)],.039,hair,[.3,1,.15])
    elif kind=='colleague':
        for s in (-1,1):
            sphere(f'colleague_bob{s}',(s*.424,.13,1.39),(.12,.28,.32),hair)
        for i in range(5):
            path(f'colleague_fringe{i}',[(-.43+i*.06,-.21,1.69),(-.12+i*.1,-.34,1.75),(.20+i*.053,-.29,1.59)],.065,hair,[.4,1,.15])
    else:
        for i in range(5):
            path(kind+f'_lock{i}',[(-.4+i*.04,-.16+i*.055,1.67),(-.14,-.33+i*.06,1.77),(.22+i*.045,-.29+i*.05,1.68)],.075,hair,[.25,1,.25])
    if kind=='chef':
        box('chef_hat_band',(0,0,1.795),(.77,.66,.235),white,.08)
        for i,(x,y,z,sc) in enumerate([(-.26,0,1.99,.25),(0,.1,2.04,.29),(.26,0,1.99,.25),(0,-.18,2.04,.29)]):
            sphere('chef_hat_puff'+str(i),(x,y,z),(sc,sc*.85,sc),white)
    if kind=='customer':
        sphere('customer_cap',(0,.035,1.71),(.505,.438,.23),red)
        sphere('customer_brim',(0,-.375,1.685),(.47,.272,.042),red)
        sphere('customer_cap_button',(0,.035,1.943),(.04,.04,.023),red)
        box('customer_cap_patch',(0,-.401,1.787),(.16,.022,.092),white,.025)
        for s in (-1,1):
            sphere(f'customer_cheek{s}',(s*.325,-.406,1.285),(.055,.012,.031),pink)
    if kind in ('colleague','complainer'):
        for s in (-1,1):
            pts=[(s*.208+.109*math.cos(t*math.tau/8),-.468,1.414+.096*math.sin(t*math.tau/8)) for t in range(9)]
            path(kind+f'_spectacles{s}',pts,.012,dark)
            path(kind+f'_glasses_arm{s}',[(s*.32,-.46,1.44),(s*.46,-.3,1.46),(s*.49,-.02,1.43)],.011,dark)
        path(kind+'_bridge',[(-.094,-.474,1.43),(0,-.492,1.448),(.094,-.474,1.43)],.012,dark)
    if kind=='colleague':
        for s in (-1,1):
            path(f'colleague_lanyard{s}',[(s*.15,-.29,.875),(s*.105,-.36,.66),(s*.035,-.37,.53)],.013,dark)
        box('colleague_badge',(0,-.385,.48),(.19,.028,.19),white,.018)
        box('colleague_badge_photo',(-.045,-.404,.5),(.055,.008,.065),coat,.005)
        for j in range(2):
            box(f'colleague_badge_line{j}',(.038,-.404,.52-j*.035),(.065,.008,.009),dark,.002)
    # Bake geometry, join by material to limit draw calls, retain a named root.
    bpy.ops.object.select_all(action='DESELECT')
    meshes = [o for o in bpy.context.scene.objects if o.type in ('MESH','CURVE')]
    for o in meshes:
        o.select_set(True)
    bpy.context.view_layer.objects.active = meshes[0]
    bpy.ops.object.convert(target='MESH')
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    buckets={}
    for o in list(bpy.context.selected_objects):
        buckets.setdefault(o.data.materials[0].name,[]).append(o)
    for name, objects in buckets.items():
        bpy.ops.object.select_all(action='DESELECT')
        for o in objects:
            o.select_set(True)
        bpy.context.view_layer.objects.active=objects[0]
        if len(objects) > 1:
            bpy.ops.object.join()
        bpy.context.object.name=name
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    root=bpy.data.objects.new('NPC_'+kind,None)
    bpy.context.collection.objects.link(root)
    for o in list(bpy.context.scene.objects):
        if o.type=='MESH':
            o.parent=root
    return root

def export_glb(root,kind):
    bpy.ops.object.select_all(action='SELECT')
    os.makedirs(OUT_DIR,exist_ok=True)
    out=os.path.join(OUT_DIR,kind+'.glb')
    bpy.ops.export_scene.gltf(filepath=out,export_format='GLB',use_selection=True,export_apply=True)
    print('[builder]',kind,os.path.getsize(out),'bytes')

def render_preview(kind):
    scene=bpy.context.scene
    ground=material('Studio backdrop','#744944',.85)
    box('Studio floor',(0,0,-.05),(200,200,.1),ground,.01)
    world=bpy.data.worlds.new('Studio world')
    scene.world=world
    world.use_nodes=True
    world.node_tree.nodes['Background'].inputs[0].default_value=(.33,.38,.5,1)
    world.node_tree.nodes['Background'].inputs[1].default_value=.45
    for name,loc,power,size,color in [('Key',(-3,-4,6),450,4,(1,.87,.72)),('Fill',(4,-2,3),280,3,(.77,.86,1)),('Rim',(1,3,4),500,3,(1,.8,.53))]:
        d=bpy.data.lights.new(name,'AREA'); d.energy=power; d.shape='DISK'; d.size=size; d.color=color
        o=bpy.data.objects.new(name,d); scene.collection.objects.link(o); o.location=loc
        o.rotation_euler=(Vector((0,0,1))-o.location).to_track_quat('-Z','Y').to_euler()
    c=bpy.data.cameras.new('Preview camera'); cam=bpy.data.objects.new('Preview camera',c); scene.collection.objects.link(cam)
    scene.camera=cam; c.type='ORTHO'; c.ortho_scale=2.75
    scene.render.engine='CYCLES'; scene.cycles.samples=32; scene.cycles.use_denoising=True
    scene.render.resolution_x=640; scene.render.resolution_y=720; scene.render.resolution_percentage=100
    scene.view_settings.view_transform='AgX'
    views=[('preview_'+kind,(2.5,-6,2.8))]
    if kind=='boss':
        views += [('preview_boss_front',(0,-6,2.1)),('preview_boss_back',(2.6,6,2.8))]
    for name,loc in views:
        cam.location=loc
        cam.rotation_euler=(Vector((0,0,1.1))-cam.location).to_track_quat('-Z','Y').to_euler()
        scene.render.filepath=os.path.join(OUT_DIR,name+'.png')
        bpy.ops.render.render(write_still=True)

if __name__=='__main__':
    only=os.environ.get('BLENDER_ONLY_KIND')
    for kind in ([only] if only else VARIANTS):
        root=build_character(kind)
        export_glb(root,kind)
        if os.environ.get('BLENDER_RENDER') or '--render' in sys.argv:
            render_preview(kind)
