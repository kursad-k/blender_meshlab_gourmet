import os

import sys
import bpy

import logging

import copy

from mathutils import Vector

APIVER = str(bpy.app.version[0]) + str(bpy.app.version[1])


def make_annotations(cls):

    if bpy.app.version < (2, 80):
        return cls
    bl_props = {k: v for k, v in cls.__dict__.items() if isinstance(v, tuple)}
    if bl_props:
        if '__annotations__' not in cls.__dict__:
            setattr(cls, '__annotations__', {})
        annotations = cls.__dict__['__annotations__']
        for k, v in bl_props.items():
            annotations[k] = v
            delattr(cls, k)
    return cls


def setMeshlabserver():

    if sys.platform.startswith('darwin'):
        return "meshlabserver"

    elif os.name == 'nt':
        return "meshlabserver.exe"

    elif os.name == 'posix':
        return "meshlabserver"


def setIcon(iname=""):

    if APIVER == "279":

        if iname == "object":
            icon = "OBJECT_DATA"

        if iname == "remesh":
            icon = "OBJECT_DATA"

        if iname == "mesh":
            icon = "MESH_DATA"

        if iname == "sculpt":
            icon = "SCULPTMODE_HLT"

        if iname == "dyntopo":
            icon = "SCULPTMODE_HLT"

        if iname == "merge":
            icon = "AUTOMERGE_ON"

        if iname == "preset":
            icon = 'INFO'

        if iname == "preset_new":
            icon = "PRESET_NEW"

        if iname == "file":
            icon = "FILE_BLEND"

        if iname == "commit":
            icon = "FILE_TICK"

        if iname == "remove":
            icon = "CANCEL"

    if int(APIVER) >= 280:

        if iname == "object":
            icon = "OBJECT_DATAMODE"

        if iname == "remesh":
            icon = "MOD_REMESH"

        if iname == "mesh":
            icon = "MESH_DATA"

        if iname == "sculpt":
            icon = "SCULPTMODE_HLT"

        if iname == "dyntopo":
            icon = "SCULPTMODE_HLT"

        if iname == "merge":
            icon = "AUTOMERGE_ON"

        if iname == "preset":
            icon = "PRESET"

        if iname == "preset_new":
            icon = "PRESET_NEW"

        if iname == "file":
            icon = "FILE_BLEND"

        if iname == "commit":
            icon = "FILE_TICK"

        if iname == "remove":
            icon = "REMOVE"

    return icon


def hide_in_viewport(obj):
    if APIVER == "279":
        obj.hide = True

    if int(APIVER) >= 280:
        obj.hide_viewport = True


def isEditMode():

    if bpy.context.object.mode == "EDIT":
        return True

    else:
        return False


def isSculptMode():

    return bpy.context.object.mode == "SCULPT"


def isObjectMode():

    return bpy.context.object.mode == "OBJECT"


def toggleObjectMode():

    if isEditMode() or isSculptMode():
        bpy.ops.object.mode_set(mode="OBJECT")

    else:
        return True

    return


def toggleEditMode():

    bpy.ops.object.mode_set(mode='EDIT')


def toggleSculptMode():

    if isObjectMode():
        bpy.ops.object.mode_set(mode='SCULPT')
    elif isSculptMode():
        bpy.ops.object.mode_set(mode='OBJECT')


def toggleSculptDynTopoToggle():

    if isObjectMode():
        bpy.ops.object.mode_set(mode='SCULPT')
        bpy.ops.sculpt.dynamic_topology_toggle()

    elif isSculptMode():
        bpy.ops.sculpt.dynamic_topology_toggle()


def toolBisect():

    if not isEditMode():
        toggleEditMode()

        bpy.ops.mesh.select_all(action='SELECT')

        if bpy.ops.mesh.bisect.poll():
            try:
                bpy.ops.mesh.bisect('INVOKE_DEFAULT',
                                    use_fill=True,
                                    clear_inner=False,
                                    clear_outer=True)
            except:
                pass


def preferences(context):

    if APIVER == "279":
        return context.user_preferences
    if int(APIVER) >= 280:
        return context.preferences


def getPreferences(context):
    if APIVER == "279":
        user_preferences = context.user_preferences

    if int(APIVER) >= 280:
        user_preferences = context.preferences

    addon_prefs = user_preferences.addons[__name__].preferences

    return addon_prefs


def getSelection():
    return bpy.context.selected_objects


def setActiveObject(context, obj):

    if APIVER == "279":
        bpy.context.scene.objects.active = obj
    if int(APIVER) >= 280:
        bpy.context.view_layer.objects.active = obj


def selectObject(obj):

    if APIVER == "279":
        obj.select = True
    if int(APIVER) >= 280:
        obj.select_set(True)


def deselectObject(obj):

    if APIVER == "279":
        obj.select = False
    if int(APIVER) >= 280:
        obj.select_set(False)


def setSelectedAsActive(context):

    if getSelection():
        obj = getSelection()[-1]

        setActiveObject(context, obj)

        return True


def transform(loc):
    if APIVER == "279":
        bpy.ops.transform.translate(value=loc,
                                    constraint_orientation='GLOBAL',
                                    constraint_axis=(True, False, False))
    if int(APIVER) >= 280:
        bpy.ops.transform.translate(value=loc, orient_matrix_type='GLOBAL')


def setPivot(context, pivot_mode='MEDIAN_POINT'):

    if APIVER == "279":
        context.space_data.pivot_point = pivot_mode
    if int(APIVER) >= 280:
        bpy.context.scene.tool_settings.transform_pivot_point = pivot_mode


def setTransformOrient(context, transform_mode='GLOBAL'):

    if APIVER == "279":
        bpy.context.space_data.transform_orientation = transform_mode

    if int(APIVER) >= 280:
        loggy28_info(transform_mode)
        bpy.context.scene.transform_orientation_slots[0].type = transform_mode
        bpy.context.scene.transform_orientation_slots[1].type = transform_mode


def getCursorPosition():

    if APIVER == "279":
        return bpy.context.space_data.cursor_location
    if int(APIVER) >= 280:
        return bpy.context.scene.cursor_location


def setCursorLocation(pos):

    if APIVER == "279":
        bpy.context.space_data.cursor_location = pos
    if int(APIVER) >= 280:
        bpy.context.scene.cursor_location = pos


def enableManipulator(context):

    if APIVER == "279":
        bpy.context.space_data.show_manipulator = True
        bpy.context.space_data.transform_manipulators = {'TRANSLATE', 'ROTATE'}

    if int(APIVER) >= 280:
        context.scene.tool_settings.use_gizmo_mode = {'TRANSLATE', 'ROTATE'}
        bpy.ops.wm.tool_set_by_name(name="Transform")


def setObjectPivot2Cursor():

    bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
    return bpy.context.object.location


def setObjectPivot2OwnCenter(pivot_center="ORIGIN_CENTER_OF_MASS"):
    """ """
    ctype = 'GEOMETRY_ORIGIN'
    if pivot_center == ctype:
        bpy.ops.object.origin_set(type=ctype)

    ctype = 'ORIGIN_GEOMETRY'
    if pivot_center == ctype:
        bpy.ops.object.origin_set(type=ctype)

    ctype = 'ORIGIN_CURSOR'
    if pivot_center == ctype:
        bpy.ops.object.origin_set(type=ctype)

    ctype = 'ORIGIN_CENTER_OF_MASS'
    if pivot_center == ctype:
        bpy.ops.object.origin_set(type=ctype)

    ctype = 'ORIGIN_CENTER_OF_VOLUME'
    if pivot_center == ctype:
        bpy.ops.object.origin_set(type=ctype)

    return bpy.context.object.location


def setCursor2ObjectSelected():
    bpy.ops.view3d.snap_cursor_to_selected()
    return bpy.context.space_data.cursor_location


def exchangePivotCursor(pivot_center="ORIGIN_CENTER_OF_MASS"):

    if isEditMode():
        bpy.ops.object.editmode_toggle()

    mat_old = copy.copy(bpy.context.object.matrix_world)
    old = Vector(bpy.context.object.location)

    cur_loc_original = getCursorPosition()

    setCursorLocation(mat_old.translation)

    setObjectPivot2OwnCenter(pivot_center)

    new = Vector(bpy.context.object.location)
    mat_new = copy.copy(bpy.context.object.matrix_world)

    setObjectPivot2Cursor()

    setCursorLocation(mat_new.translation)

    return True


def centerCursor2Selection():

    old = Vector(bpy.context.object.location)
    cur_loc_original = bpy.context.space_data.cursor_location

    setCursorLocation(old)

    setObjectPivot2OwnCenter()
    new = Vector(bpy.context.object.location)


def parentLocationAxis(context):

    obj = bpy.context.object
    parent = obj.parent

    loc = copy.copy(parent.location)
    rot = copy.copy(parent.rotation_euler)

    bpy.ops.object.select_all(action='DESELECT')

    selectObject(parent)

    setActiveObject(context, parent)

    setTransformOrient(context, 'NORMAL')

    bpy.ops.transform.create_orientation(name="modoaction",
                                         use_view=False,
                                         use=True,
                                         overwrite=True)

    setCursorLocation(loc)

    setPivot(context, 'CURSOR')
    setTransformOrient(context, 'modoaction')
    bpy.ops.object.select_all(action='DESELECT')
    selectObject(obj)
    setActiveObject(context, obj)


def processBoolUnion():

    to_add = [
        o for o in bpy.context.selected_objects if not o == bpy.context.object
    ][0]

    name = "MERGE"
    bpy.ops.object.modifier_add(type='BOOLEAN')
    md = bpy.context.object.modifiers.values()[-1]
    md.name = name
    md.object = to_add
    md.operation = 'UNION'
    md.double_threshold = 0.000001

    deselectObject(to_add)
    hide_in_viewport(to_add)


def processTempIO():
    import tempfile

    out_file = tempfile.mktemp(suffix=".obj")

    script_name = ""

    bpy.ops.export_scene.obj(filepath=out_file,
                             use_selection=True,
                             use_materials=False,
                             keep_vertex_order=True,
                             use_edges=False,
                             use_smooth_groups=True,
                             use_vertex_groups=False,
                             use_triangles=True)

    bpy.ops.import_scene.obj(filepath=out_file)

    return out_file


def processScript(meshlab="", mode=""):

    import subprocess
    import tempfile
    from pathlib import Path

    meshlab = meshlab
    print("MESHLAB SET FROM PREFERENCES {}".format(meshlab))

    out_file = tempfile.mktemp(suffix=".obj")

    run_meshlab = True
    script_name = ""

    if mode == "basic":

        run_meshlab = False

    if mode == "rough":
        script_name = "Rmsh_Isotropic_Rough.mlx"

    if mode == "fine":
        script_name = "Rmsh_Isotropic_Fine.mlx"

    if mode == "extrafine":
        script_name = "Rmsh_Isotropic_ExtraFine.mlx"

    if mode == "marchingcubes_a":
        script_name = "Rmsh_MarchingCbs_RIMLS.mlx"

    if mode == "marchingcubes_b":
        script_name = "Rmsh_MarchingCbs_APSS.mlx"

    if mode == "poissonscreen":
        script_name = "Rmsh_PoissonScreen.mlx"

    if mode == "cleanup_a":
        script_name = "CleanUp1.mlx"

    if mode == "smooths":
        script_name = "Smooth_2Step.mlx"

    file = Path(__file__).parent
    script = file.joinpath("Library").joinpath("Scripts").joinpath(script_name)

    print("SCRIPT PATH IS  {}".format(script))

    command = '{} -i {} -o {} -l x -s "{}"'.format(meshlab, out_file, out_file,
                                                   str(script))

    print("MESHLAB COMMAND > ", command)

    bpy.ops.export_scene.obj(filepath=out_file,
                             use_selection=True,
                             use_materials=False,
                             keep_vertex_order=True,
                             use_edges=False,
                             use_smooth_groups=True,
                             use_vertex_groups=False,
                             use_triangles=True)

    if run_meshlab:
        subprocess.run(command, shell=True)

    bpy.ops.import_scene.obj(filepath=out_file)

    return True
