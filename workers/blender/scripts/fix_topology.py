import sys
import bpy

def fix_topology(filepath, out_path, target_ratio=0.5):
    print(f"Loading model for topology decimation: {filepath}")
    bpy.ops.wm.read_factory_settings(use_empty=True)

    if filepath.endswith('.glb') or filepath.endswith('.gltf'):
        bpy.ops.import_scene.gltf(filepath=filepath)
    elif filepath.endswith('.fbx'):
        bpy.ops.import_scene.fbx(filepath=filepath)

    for obj in bpy.context.scene.objects:
        if obj.type == 'MESH':
            # Add decimate modifier to reduce polygon count
            decimate_mod = obj.modifiers.new(name="WebDecimate", type='DECIMATE')
            decimate_mod.ratio = float(target_ratio)

            # Active object selection to apply modifiers
            bpy.context.view_layer.objects.active = obj
            bpy.ops.object.modifier_apply(modifier="WebDecimate")
            print(f"Decimated {obj.name} by ratio {target_ratio}")

    bpy.ops.export_scene.gltf(filepath=out_path, export_format='GLB')

if __name__ == "__main__":
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    if len(args) >= 2:
        ratio = args[2] if len(args) >= 3 else 0.5
        fix_topology(args[0], args[1], ratio)
    else:
        print("Usage: blender --background --python fix_topology.py -- <in_path> <out_path> <ratio>")
