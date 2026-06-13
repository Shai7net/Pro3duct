import sys
import bpy

def set_pivots(filepath, out_path):
    print(f"Loading model for pivot centering: {filepath}")
    bpy.ops.wm.read_factory_settings(use_empty=True)

    if filepath.endswith('.glb') or filepath.endswith('.gltf'):
        bpy.ops.import_scene.gltf(filepath=filepath)

    # Set origin to geometry center bounds for each mesh object
    for obj in bpy.context.scene.objects:
        if obj.type == 'MESH':
            bpy.context.view_layer.objects.active = obj
            bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='BOUNDS')
            print(f"Pivot centered for: {obj.name}")

    bpy.ops.export_scene.gltf(filepath=out_path, export_format='GLB')

if __name__ == "__main__":
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    if len(args) >= 2:
        set_pivots(args[0], args[1])
