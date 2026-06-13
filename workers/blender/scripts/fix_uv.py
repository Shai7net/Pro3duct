import sys
import bpy

def fix_uv(filepath, out_path):
    print(f"Loading model for UV correction: {filepath}")
    bpy.ops.wm.read_factory_settings(use_empty=True)

    if filepath.endswith('.glb') or filepath.endswith('.gltf'):
        bpy.ops.import_scene.gltf(filepath=filepath)

    for obj in bpy.context.scene.objects:
        if obj.type == 'MESH':
            bpy.context.view_layer.objects.active = obj
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')

            # Perform Smart UV Project unwrap
            bpy.ops.uv.smart_project(angle_limit=66.0, island_margin=0.02)
            bpy.ops.object.mode_set(mode='OBJECT')
            print(f"UV unwrapped for: {obj.name}")

    bpy.ops.export_scene.gltf(filepath=out_path, export_format='GLB')

if __name__ == "__main__":
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    if len(args) >= 2:
        fix_uv(args[0], args[1])
