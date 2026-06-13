import sys
import bpy

def fix_geometry(filepath, out_path):
    print(f"Loading model for geometry correction: {filepath}")

    # Clear existing scene meshes
    bpy.ops.wm.read_factory_settings(use_empty=True)

    # Import GLB/FBX
    if filepath.endswith('.glb') or filepath.endswith('.gltf'):
        bpy.ops.import_scene.gltf(filepath=filepath)
    elif filepath.endswith('.fbx'):
        bpy.ops.import_scene.fbx(filepath=filepath)
    elif filepath.endswith('.obj'):
        bpy.ops.import_scene.obj(filepath=filepath)

    # Process each mesh in the imported scene
    for obj in bpy.context.scene.objects:
        if obj.type == 'MESH':
            print(f"Processing mesh: {obj.name}")
            bpy.context.view_layer.objects.active = obj

            # Switch to edit mode to run cleanup operators
            bpy.ops.object.mode_set(mode='EDIT')

            # Select all geometry
            bpy.ops.mesh.select_all(action='SELECT')

            # Clean duplicate double vertices
            bpy.ops.mesh.remove_doubles(threshold=0.0001)

            # Recalculate outside normals
            bpy.ops.mesh.normals_make_consistent(inside=False)

            # Return to object mode
            bpy.ops.object.mode_set(mode='OBJECT')

    # Export cleaned mesh
    print(f"Exporting cleaned model to: {out_path}")
    bpy.ops.export_scene.gltf(filepath=out_path, export_format='GLB')

if __name__ == "__main__":
    # Get python args after "--"
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    if len(args) >= 2:
        fix_geometry(args[0], args[1])
    else:
        print("Usage: blender --background --python fix_geometry.py -- <in_path> <out_path>")
