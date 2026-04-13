bl_info = {
    "name": "MeshLabGourmet",
    "author": "Kursad Karatas",
    "description":
    "Companion app for exhanging and processing meshes with Meshlab",
    "blender": (2, 80, 0),
    "version": (1, 2, 1),
    "location": "",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Object"
}

import os, sys
import subprocess
from pathlib import Path

if "bpy" in locals():
    import importlib
    from .blendlib import *
    importlib.reload(blendlib)
    importlib.reload(apiverlib)
else:
    from .blendlib import *
    from . import apiverlib as api

import bpy
import bpy_extras
from mathutils import Vector

from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator
from bpy.types import AddonPreferences
from bpy.types import PropertyGroup

preview_collections = {}


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


def debugPrintVariables(vars=[], names=[]):
    """Debug printing
    """

    if len(vars) == len(names):
        for c, p in enumerate(vars):
            print("VAR : {} >> {}".format(names[c], p))


def getPreferences(context):

    user_preferences = context.preferences

    addon_prefs = user_preferences.addons[__name__].preferences

    return addon_prefs


def setMeshLabFolder(path=None):
    """Add Meshlab executables to environment
    """
    if path:
        meshlabserver_path = path

    else:
        meshlabserver_path = ""
        print(">>> USING THE DEFAULT MESHLAB PATH <<<")

    return meshlabserver_path


def addTextEditor(fpath=None):

    if fpath:
        texteditor = fpath

    else:
        texteditor = None

    return texteditor


def updateScriptsFolder(path=None, name=None, *dic):
    """Script path for the custom Meshlab scripts
    """

    if not path:

        if name:
            scriptsfolder = os.path.normpath(
                os.path.join(bpy.utils.script_path_user(), "addons", name,
                             "scripts"))

        else:
            scriptsfolder = os.path.normpath(
                os.path.join(bpy.utils.script_path_user(), "addons",
                             "MeshLabGourmet", "scripts"))

    else:

        if name:
            scriptsfolder = os.path.normpath(
                os.path.join(path, "addons", name, "scripts"))

        else:
            scriptsfolder = os.path.normpath(
                os.path.join(path, "addons", "MeshLabGourmet", "scripts"))

    return scriptsfolder


def updateScriptPath(path=None, name=None):
    """Script path for the custom Meshlab scripts
    """

    if not path:
        scriptpath = os.path.join(
            bpy.data.window_managers["WinMan"].mlg_script_dir,
            bpy.data.window_managers["WinMan"].mlg_script)

        print(">>>SCRIPT_PATH is <<<", scriptpath)
        scriptpath = os.path.abspath(scriptpath)
        print(">>>SCRIPT_PATH is <<<", scriptpath)
    else:
        if name:
            scriptpath = os.path.join(path, name)
        else:
            scriptpath = os.path.join(
                path, bpy.data.window_managers["WinMan"].mlg_script)

    return scriptpath


def parseScriptList(self, context):
    """EnumProperty callback"""
    enum_items = []

    if context is None:
        return enum_items

    wm = context.window_manager
    directory = wm.mlg_script_dir

    pcoll = preview_collections["main"]

    if directory == pcoll.mlg_script_dir:
        return pcoll.mlg_script

    print("Scanning directory: %s" % directory)

    if directory and os.path.exists(directory):
        image_paths = []
        for fn in os.listdir(directory):
            if fn.lower().endswith(".mlx"):
                image_paths.append(fn)

        for i, name in enumerate(image_paths):
            filepath = os.path.join(directory, name)
            enum_items.append((name, name, "", i))

    pcoll.mlg_script = enum_items
    pcoll.mlg_script_dir = directory
    return enum_items


class WarningMeshlabDialogOperator(bpy.types.Operator):
    """# test call bpy.ops.object.warning_dialog_operator('INVOKE_DEFAULT')
    """
    bl_idname = "object.warning_meshlab_dialog_operator"
    bl_label = "[Warning] Set the path for Meshlab folder in the addon"

    def execute(self, context):

        message = " WARNING "

        self.report({'INFO'}, message)
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self, width=600, height=40)


class RefreshMeshlabScripts(bpy.types.Operator):
    """This appears in the tooltip of the operator and in the generated docs"""
    bl_idname = "object.refreshmeshlabscripts"
    bl_label = "Refresh Scripts"

    def execute(self, context):

        from bpy.types import WindowManager

        WindowManager.mlg_script = EnumProperty(items=parseScriptList, )

        import bpy.utils.previews
        pcoll = bpy.utils.previews.new()
        pcoll.mlg_script_dir = ""
        pcoll.mlg_script = ()

        preview_collections["main"] = pcoll

        return {'FINISHED'}


class EditScript(bpy.types.Operator):
    """This appears in the tooltip of the operator and in the generated docs"""

    bl_idname = "object.editscript"
    bl_label = "Edit the Script"

    def execute(self, context):

        wm = context.window_manager

        print(">>>[EditScript] SCRIPT_PATH is <<<", wm.mlg_script_path)

        if sys.platform.startswith('darwin'):
            subprocess.call(('open', wm.mlg_script_path))

        elif os.name == 'nt':
            os.startfile(wm.mlg_script_path)

        elif os.name == 'posix':
            subprocess.call(('xdg-open', wm.mlg_script_path))

        return {'FINISHED'}


def contructCommand(context, switch=None):
    """Main function that constructs the proper executable with the required commanline
    """

    command = ""
    platform = ""
    extension = ""
    meshlab = "meshlab"
    meshlabserver = "meshlabserver"
    ismeshlabserver = False

    if sys.platform.startswith('darwin'):
        platform = "macos"
        extension = ""

    elif os.name == 'nt':
        platform = "nt"
        extension = ".exe"

    elif os.name == 'posix':
        platforms = "linux"
        extension = ""

    scene = Scene()

    obj = Object()
    obj_name = obj.Name

    obj_loc = obj.LocationW
    obj_rot = obj.RotationW
    obj_scl = obj.ScaleW
    bpy.ops.object.location_clear()
    bpy.ops.object.rotation_clear()
    bpy.ops.object.scale_clear()

    out = Io()

    wm = context.window_manager

    processed_filename = out.Tempname + "_processed.obj"
    processed_fullpath = os.path.join(out.Tempfolder, processed_filename)
    prosessed_obj_name = os.path.splitext(processed_filename)[0]

    exported_by_meshlab = False

    if switch == "meshlab":

        labcommand = meshlab + extension

        meshlabexe = os.path.join(wm.mlg_meshlab_folder, labcommand)
        command = "{} {}".format(meshlabexe, out.Exportfullpath)

        prosessed_obj_name = out.Exportname
        object2import = out.Exportfullpath

        out.obj_Export(out.Exportfullpath)

    if switch == "meshlabserver":

        ismeshlabserver = True
        labcommand = meshlabserver + extension

        meshlabserver = os.path.join(wm.mlg_meshlab_folder, labcommand)
        command = '"{}" -i "{}" -o "{}"  -s "{}" '.format(
            meshlabserver, out.Tempexportfile, processed_fullpath,
            wm.mlg_script_path)
        object2import = processed_fullpath

        out.obj_Export()

    if wm.mlg_meshlab_folder:

        subprocess.run(command, shell=True)

        obj.Id.location = obj_loc
        obj.Id.rotation_euler = obj_rot
        obj.Id.scale = obj_scl

        print("MESHLABSERVER COMMAND ->>> {}".format(command))

        active_object = bpy.context.active_object
        selected_object = bpy.context.selectable_objects[0]

        with open(object2import, "r") as obj_file:
            for n, l in enumerate(obj_file):
                if n < 12 and "meshlab" in l.lower():
                    exported_by_meshlab = True
                    print(exported_by_meshlab, " ^^^^  ", n, " ....  ", l)
                    break

        if exported_by_meshlab:

            if out.obj_Import(file=object2import):
                print("obj imported")

                print("<< SELECTED OBJECT  {} >>".format(
                    bpy.context.selected_objects))
                print("<< ACTIVE OBJECT {} >>".format(bpy.context.object))
                print("<< LOCATION {} >>".format(obj.Location[0]))

                api.setSelectedAsActive(context=bpy.context)

                obj_processed = Object()
                obj_processed.Id.name = obj_name + "_processed"

                print("<< SELECTED OBJECT 2 {} >>".format(
                    bpy.context.selected_objects))
                print("<< ACTIVE OBJECT   2 {} >>".format(bpy.context.object))

                obj_processed.Id.data.use_auto_smooth = False

                obj_rot = Vector(
                    (obj_rot[0] + 1.5707963267948966, obj_rot[1], obj_rot[2]))
                bpy.context.active_object.location = obj_loc
                bpy.context.active_object.rotation_euler = obj_rot
                bpy.context.active_object.scale = obj_scl

                location_x = obj.Location[0]

                api.transform(loc=(scene.Object.dimensions[0], 0, 0))

                obj_processed.convertTris2Quads()

                bpy.context.view_layer.update()

                if not wm.mlg_keepmeshes:
                    if ismeshlabserver:
                        out.obj_CleanUp(file=object2import)
                        out.obj_CleanUp(file=out.Tempexportfile)
                    else:
                        out.obj_CleanUp(file=out.Exportfullpath)

    else:
        bpy.ops.object.warning_meshlab_dialog_operator('INVOKE_DEFAULT')

    bpy.context.view_layer.update()


class OBJECT_OT_ProcessScript(Operator):
    """This appears in the tooltip of the operator and in the generated docs"""
    bl_idname = "object.processmeshlabscript"
    bl_label = "Process the Script"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):

        return context.object.type == 'MESH'

    def invoke(self, context, event):

        obj = Object()
        if obj.isEditMode():
            obj.objectMode()
        else:
            pass
        return self.execute(context)

    def execute(self, context):

        contructCommand(context, "meshlabserver")

        return {'FINISHED'}


class OBJECT_OT_RunMeshLab(Operator):
    """This appears in the tooltip of the operator and in the generated docs"""
    bl_idname = "object.runmeshlab"
    bl_label = "Open in Meshlab"
    bl_options = {'REGISTER', 'UNDO'}

    message: bpy.props.StringProperty(name="You are in edit mode")

    @classmethod
    def poll(cls, context):

        return context.object.type == "MESH"

    def invoke(self, context, event):

        obj = Object()
        if obj.isEditMode():
            obj.objectMode()
        return self.execute(context)

    def execute(self, context):

        contructCommand(context, "meshlab")

        return {'FINISHED'}


def reconfigureMeshLabStage(context):

    con = context
    wm = context.window_manager
    obj = context.object
    scene = Scene()

    addon_prefs = getPreferences(con)
    info = ("Meshlab Folder Path: %s, Scripts: %s" %
            (addon_prefs.meshlabfolder, addon_prefs.scriptsfolder))

    wm.mlg_addon_name = "MeshLabGourmet"

    if addon_prefs.meshlabfolder:
        wm.mlg_meshlab_folder = addon_prefs.meshlabfolder
        setMeshLabFolder(path=wm.mlg_meshlab_folder)
    else:

        setMeshLabFolder()

    if addon_prefs.editorpath:
        wm.mlg_text_editor = addon_prefs.editorpath
    else:
        pass

    if addon_prefs.scriptsfolder:
        wm.mlg_scripts_folder = addon_prefs.scriptsfolder
    else:
        wm.mlg_scripts_folder = updateScriptsFolder(path=scene.ScriptsPath,
                                                    name=__name__)

    if wm.mlg_script:
        wm.mlg_script_path = updateScriptPath(path=wm.mlg_scripts_folder,
                                              name=wm.mlg_script)

    wm.mlg_script_path = updateScriptPath(path=wm.mlg_scripts_folder,
                                          name=wm.mlg_script)

    wm.mlg_script_dir = wm.mlg_scripts_folder

    to_print = [
        wm.mlg_script_dir, wm.mlg_script, wm.mlg_meshlab_folder,
        wm.mlg_text_editor, wm.mlg_scripts_folder, wm.mlg_script_path
    ]

    to_print_names = [
        "wm.mlg_script_dir", "wm.mlg_script", "wm.mlg_meshlab_folder",
        "wm.mlg_text_editor", "wm.mlg_scripts_folder", "wm.mlg_script_path"
    ]

    if wm.mlg_debug:
        debugPrintVariables(to_print, to_print_names)

        print(context.space_data.type)
    return


class MeshLabPreferences(AddonPreferences):
    bl_idname = __name__

    meshlabfolder: StringProperty(
        name="Meshlab 2018 Folder",
        subtype='DIR_PATH',
    )

    scriptsfolder: StringProperty(
        name="Custom Scripts Path",
        subtype='DIR_PATH',
    )

    editorpath: StringProperty(
        name="Script Text Editor",
        subtype='FILE_PATH',
    )

    def draw(self, context):
        layout = self.layout
        layout.label(text="This is a preferences view for our addon")
        layout.prop(self, "meshlabfolder")
        layout.prop(self, "scriptsfolder")
        layout.prop(self, "editorpath")


class MeshLabGourmetPanel(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "MeshLabGourmet"
    bl_idname = "OBJECT_PT_MeshLabGourmet"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

    @classmethod
    def poll(cls, context):

        reconfigureMeshLabStage(context)

        return len(context.selected_objects) > 0

    def draw(self, context):

        layout = self.layout
        wm = context.window_manager
        obj = context.object
        scene = Scene()

        row = layout.row()
        row.label(text="Enable Debug:")
        row = layout.row()
        row.prop(wm, "mlg_debug")
        row.prop(wm, "mlg_keepmeshes")

        row = layout.row()
        row.label(text="Active object is: " + obj.name)
        row = layout.row()
        row.prop(obj, "name")

        row = layout.row()
        row.prop(wm, "mlg_script_dir")

        row = layout.row()
        row = layout.row(align=True)
        row.prop(wm, "mlg_script", text="Script")

        row = layout.row()
        row.label(text="Refresh Script Folder")
        row.operator('object.refreshmeshlabscripts')

        row = layout.row()
        row.operator('object.editscript')

        row = layout.row()
        row.operator('object.processmeshlabscript')

        row = layout.row()
        row.operator('object.runmeshlab')


def register_helpers():
    from bpy.types import WindowManager
    from bpy.props import (
        StringProperty,
        EnumProperty,
    )

    WindowManager.mlg_script_dir = StringProperty(name="Scripts Path",
                                                  subtype='DIR_PATH',
                                                  default="")

    WindowManager.mlg_script = EnumProperty(name="",
                                            items=parseScriptList,
                                            options={'HIDDEN'})

    WindowManager.mlg_script_path = StringProperty(
        name="script_path",
        description="path for the current script",
        default="",
        subtype='FILE_PATH',
    )

    WindowManager.mlg_scripts_folder = StringProperty(
        name="scripts_folder",
        description="folder path for the  meshlab scripts",
        default='./scripts',
        subtype='DIR_PATH',
    )

    WindowManager.mlg_text_editor = StringProperty(
        name="text_editor",
        description="text editor for editing the current script",
        default='',
        subtype='FILE_PATH',
    )

    WindowManager.mlg_meshlab_folder = StringProperty(
        name="text_editor",
        description="folder for the meshlab binaries",
        default="",
        subtype='DIR_PATH',
    )

    WindowManager.mlg_addon_name = StringProperty(
        name="addon_name",
        description="folder for the meshlab binaries",
        default="",
    )

    WindowManager.mlg_debug = BoolProperty(
        name="MeshLabG debug",
        default=False,
    )

    WindowManager.mlg_keepmeshes = BoolProperty(
        name="Keep processed meshes",
        default=False,
    )

    import bpy.utils.previews
    pcoll = bpy.utils.previews.new()
    pcoll.mlg_script_dir = ""
    pcoll.mlg_script = ()

    preview_collections["main"] = pcoll


def unregister_helpers():
    from bpy.types import WindowManager

    del WindowManager.mlg_script

    del WindowManager.mlg_script_path
    del WindowManager.mlg_scripts_folder
    del WindowManager.mlg_text_editor
    del WindowManager.mlg_meshlab_folder
    del WindowManager.mlg_addon_name
    del WindowManager.mlg_debug
    del WindowManager.mlg_keepmeshes

    for pcoll in preview_collections.values():
        bpy.utils.previews.remove(pcoll)
    preview_collections.clear()


classes = (MeshLabGourmetPanel, OBJECT_OT_ProcessScript, OBJECT_OT_RunMeshLab,
           RefreshMeshlabScripts, EditScript, MeshLabPreferences,
           WarningMeshlabDialogOperator)


def register():
    register_helpers()

    for cls in classes:
        make_annotations(cls)

        bpy.utils.register_class(cls)


def unregister():
    unregister_helpers()

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
